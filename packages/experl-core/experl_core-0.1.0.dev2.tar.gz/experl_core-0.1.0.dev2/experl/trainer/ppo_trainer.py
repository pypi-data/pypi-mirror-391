from datasets import load_dataset
from mlflow.data.huggingface_dataset import from_huggingface
from omegaconf import OmegaConf
from transformers import AutoConfig, AutoModelForCausalLM
from trl import PPOConfig, PPOTrainer, create_reference_model, get_quantization_config

from experl.config.config_loader import ConfigLoader
from experl.config.schema.config_classes import OrchestratorConfig
from experl.logger.mlflow_logger import MLFlowLogger
from experl.models.reward_model import RewardModel
from experl.trainer.base_trainer import BaseTrainer
from experl.utils.dataset_utils import get_dataset_metadata
from experl.utils.logging_utils import get_logger
from experl.utils.trainer_utils import (
    create_file_path,
    get_device,
    get_dtype,
    get_model_id,
    get_tokenizer,
    get_tracking_path,
    parse_cli_args,
    sanitize_model,
)


log = get_logger(__name__)


class PPOModelTrainer(BaseTrainer):

    def __init__(
            self,
            config: OrchestratorConfig,
            mlflow_logger: MLFlowLogger,
    ):
        self.ref_policy = None
        self.value_model = None
        self.reward_model = None
        self.policy_model = None
        super().__init__(
            trainer_name="ppo_model",
            config=config,
            mlflow_logger=mlflow_logger,
        )
        self.model_name_or_path = self.config.model_name_or_path
        self.trainer_args = PPOConfig(**OmegaConf.to_container(self.config.ppo.ppo))
        self.quantization_config = get_quantization_config(self.config.model)
        log.info(
            f"Quantization Configs provided : {self.quantization_config is not None}"
        )

    def load_dataset(self):
        """Load json dataset and tokenize 'prompt' (and optional 'response')."""

        def tokenize_prompt(example, tokenizer):
            tokenized = tokenizer(text=example["prompt"])
            if tokenizer.eos_token_id is not None and tokenized["input_ids"][-1] != tokenizer.eos_token_id:
                tokenized["input_ids"] = tokenized["input_ids"] + [tokenizer.eos_token_id]
                tokenized["attention_mask"] = tokenized["attention_mask"] + [1]
            return tokenized

        dataset = load_dataset(self.config.dataset.prompt.path,
                               name=self.config.dataset.prompt.config)

        dataset = dataset.map(tokenize_prompt, fn_kwargs={"tokenizer": self.tokenizer}, remove_columns="prompt")

        self.train_dataset = dataset[self.config.dataset.prompt.train_split]
        self.eval_dataset = dataset[
            self.config.dataset.prompt.test_split] if self.trainer_args.eval_strategy != "no" else None
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

    def load_model(self):
        model_name_or_path = get_model_id(self.config.model_name_or_path)
        reward_model_name_or_path = get_model_id(self.config.ppo.reward_model_name_or_path)

        self.trainer_args.sft_model_path = create_file_path(
            self.config,
            f"sft_model/final-sft_model-{model_name_or_path}",
        )
        self.trainer_args.reward_model_path = create_file_path(
            self.config,
            f"reward_model/final-reward_model-{reward_model_name_or_path}",
        )

        self.load_policy_model()
        self.load_reward_model()
        self.load_value_model()
        self.load_ref_model()

    def load_ref_model(self):
        self.ref_policy = create_reference_model(self.policy_model)
        self.ref_policy.to(get_device())

    def load_value_model(self):
        config = AutoConfig.from_pretrained(
            self.config.ppo.reward_model_name_or_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        self.value_model = RewardModel(config)
        sanitize_model(self.value_model, self.tokenizer)
        self.value_model.to(get_device())

    def load_reward_model(self):
        reward_model_name_or_path = get_model_id(self.config.ppo.reward_model_name_or_path)
        log.debug(f"reward_model_name_or_path = {reward_model_name_or_path}")

        reward_model_path = create_file_path(
            self.config,
            f"reward_model/final-reward_model-{reward_model_name_or_path}",
        )

        rm_config = AutoConfig.from_pretrained(
            reward_model_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        self.reward_model = RewardModel(rm_config)
        sanitize_model(self.reward_model, self.tokenizer)
        self.reward_model.to(get_device())

    def load_policy_model(self):
        self.tokenizer = get_tokenizer(
            self.trainer_args.sft_model_path,
            padding_side="left",
        )
        self.policy_model = AutoModelForCausalLM.from_pretrained(
            self.trainer_args.sft_model_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        sanitize_model(self.policy_model, self.tokenizer)
        self.policy_model.to(get_device())

    def create_trainer(self):
        self.trainer = PPOTrainer(
            args=self.trainer_args,
            processing_class=self.tokenizer,
            model=self.policy_model,
            ref_model=self.ref_policy,
            reward_model=self.reward_model,
            value_model=self.value_model,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset
        )

    def train_model(self):
        self.trainer.train()

    @staticmethod
    def run(args, overrides, nested=True):
        main_config: OrchestratorConfig
        main_config = ConfigLoader.load_config(args, overrides)
        stage = "ppo"
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
            ppo_model_trainer = PPOModelTrainer(main_config, mlogger)
            ppo_model_trainer.train()
        return main_config


if __name__ == "__main__":
    cli_args, cli_overrides = parse_cli_args()
    PPOModelTrainer.run(cli_args, cli_overrides)
