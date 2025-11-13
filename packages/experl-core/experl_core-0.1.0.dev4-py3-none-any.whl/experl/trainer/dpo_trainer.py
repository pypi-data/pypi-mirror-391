from datasets import load_dataset
from mlflow.data.huggingface_dataset import from_huggingface
from omegaconf import OmegaConf
from transformers import AutoModelForCausalLM
from trl import DPOConfig, DPOTrainer, create_reference_model, get_quantization_config

from experl.config.config_loader import ConfigLoader
from experl.config.schema.config_classes import OrchestratorConfig
from experl.logger.mlflow_logger import MLFlowLogger
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


class DPOModelTrainer(BaseTrainer):

    def __init__(
            self,
            config: OrchestratorConfig,
            mlflow_logger: MLFlowLogger,
    ):
        self.ref_policy = None
        self.value_model = None
        self.reward_model = None
        self.model = None
        super().__init__(
            trainer_name="dpo_model",
            config=config,
            mlflow_logger=mlflow_logger,
        )
        self.model_name_or_path = self.config.model_name_or_path
        self.trainer_args = DPOConfig(**OmegaConf.to_container(self.config.dpo.dpo))
        self.quantization_config = get_quantization_config(self.config.model)
        log.info(
            f"Quantization Configs provided : {self.quantization_config is not None}"
        )

    def create_trainer(self):
        self.trainer = DPOTrainer(
            self.model,
            self.ref_policy,
            args=self.trainer_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
            processing_class=self.tokenizer,
        )

    def train_model(self):
        self.trainer.train()

    def load_model(self):
        self.load_policy_model()
        self.load_ref_model()

    def load_dataset(self):
        dataset = load_dataset(self.config.dataset.preference.path,
                               name=self.config.dataset.preference.config)
        self.train_dataset = dataset[self.config.dataset.preference.train_split]
        self.eval_dataset = dataset[
            self.config.dataset.preference.test_split] if self.trainer_args.eval_strategy != "no" else None
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

    def load_ref_model(self):
        self.ref_policy = create_reference_model(self.model)
        self.ref_policy.to(get_device())

    def load_policy_model(self):
        model_name_or_path = get_model_id(self.config.model_name_or_path)
        sft_model_path = create_file_path(
            self.config,
            f"sft_model/final-sft_model-{model_name_or_path}",
        )
        self.tokenizer = get_tokenizer(
            sft_model_path,
            padding_side="left",
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            sft_model_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        sanitize_model(self.model, self.tokenizer)
        self.model.to(get_device())

    @staticmethod
    def run(args, overrides, nested=True):
        main_config = ConfigLoader.load_config(args, overrides)
        stage = "dpo"
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
            model_trainer = DPOModelTrainer(main_config, mlogger)
            model_trainer.train()


if __name__ == "__main__":
    cli_args, cli_overrides = parse_cli_args()
    DPOModelTrainer.run(cli_args, cli_overrides)
