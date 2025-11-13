from datasets import load_dataset
from mlflow.data.huggingface_dataset import from_huggingface
from omegaconf import OmegaConf
from transformers import AutoModelForCausalLM
from trl import SFTConfig, SFTTrainer

from experl.config.config_loader import ConfigLoader
from experl.config.schema.config_classes import OrchestratorConfig
from experl.logger.mlflow_logger import MLFlowLogger
from experl.trainer.base_trainer import BaseTrainer
from experl.utils.dataset_utils import get_dataset_metadata
from experl.utils.logging_utils import get_logger
from experl.utils.trainer_utils import (
    get_device,
    get_dtype,
    get_tokenizer,
    get_tracking_path,
    parse_cli_args,
    sanitize_model,
)


log = get_logger(__name__)


class SFTModelTrainer(BaseTrainer):

    def __init__(
            self,
            config: OrchestratorConfig,
            mlflow_logger: MLFlowLogger,
    ):
        super().__init__(
            trainer_name="sft_model",
            config=config,
            mlflow_logger=mlflow_logger,
        )
        self.model_name_or_path = self.config.model_name_or_path
        if self.config.config_name == "ppo":
            self.trainer_args = SFTConfig(**OmegaConf.to_container(self.config.ppo.sft))
        else:
            self.trainer_args = SFTConfig(**OmegaConf.to_container(self.config.dpo.sft))

    def load_model(self):
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name_or_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        self.tokenizer = get_tokenizer(
            self.config.model_name_or_path, self.config.model.padding_side
        )
        sanitize_model(self.model, self.tokenizer)
        self.model.to(get_device())

    def load_dataset(self):
        log.debug(f"Loading dataset from path : {self.config.dataset.sft.path}")
        prompt_key = "prompt"
        completion_key = "completion"

        def tokenize_prompt(example, tokenizer):
            tokenized = tokenizer(text=f"{example[prompt_key]} {example[completion_key]}")
            if tokenizer.eos_token_id is not None and tokenized["input_ids"][-1] != tokenizer.eos_token_id:
                tokenized["input_ids"] = tokenized["input_ids"] + [tokenizer.eos_token_id]
                tokenized["attention_mask"] = tokenized["attention_mask"] + [1]
            return tokenized

        dataset = load_dataset(self.config.dataset.sft.path, name=self.config.dataset.sft.config)

        dataset = dataset.map(tokenize_prompt, fn_kwargs={"tokenizer": self.tokenizer},
                              remove_columns=[prompt_key, completion_key])
        self.train_dataset = dataset[self.config.dataset.sft.train_split]
        self.eval_dataset = dataset[
            self.config.dataset.sft.test_split] if self.trainer_args.eval_strategy != "no" else None

        self.log_dataset()

    def log_dataset(self):
        self.mlflow_logger.log_dataset_metadata(get_dataset_metadata(self.train_dataset, self.tokenizer, name="train"))
        self.mlflow_logger.log_dataset(
            from_huggingface(self.train_dataset),
            context="train",
            model_id=self.config.model_name_or_path,
        )

        if self.eval_dataset:
            self.mlflow_logger.log_dataset_metadata(
                get_dataset_metadata(self.eval_dataset, self.tokenizer, name="test"))
            self.mlflow_logger.log_dataset(
                from_huggingface(self.eval_dataset),
                context="test",
                model_id=self.config.model_name_or_path,
            )

    def create_trainer(self) -> None:
        self.trainer = SFTTrainer(
            model=self.model,
            processing_class=self.tokenizer,
            args=self.trainer_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
        )

    def train_model(self):
        self.trainer.train()

    @staticmethod
    def run(args, overrides, nested=True) -> OrchestratorConfig:
        main_config: OrchestratorConfig
        main_config = ConfigLoader.load_config(args, overrides)
        stage = "sft"
        with MLFlowLogger(
                experiment_name=main_config.project_name,
                tracking_uri=get_tracking_path(main_config),
                run_name=f"{stage}__{main_config.run_name}",
                nested=nested,
                tags={
                    "stage": stage,
                    "run_name": f"{stage}__{main_config.run_name}",
                    "project_name": main_config.project_name,
                },
        ) as mlogger:
            mlogger.log_args_and_overrides(args, overrides)
            app = SFTModelTrainer(main_config, mlogger)
            app.train()
        return main_config


if __name__ == "__main__":
    cli_args, cli_overrides = parse_cli_args()
    SFTModelTrainer.run(cli_args, cli_overrides)
