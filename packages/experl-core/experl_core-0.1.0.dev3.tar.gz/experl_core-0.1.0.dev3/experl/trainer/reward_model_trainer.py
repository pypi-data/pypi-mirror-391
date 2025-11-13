from datasets import load_dataset
from mlflow.data.huggingface_dataset import from_huggingface
from omegaconf import OmegaConf
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from trl import RewardConfig, RewardTrainer

from experl.config.config_loader import ConfigLoader
from experl.config.schema.config_classes import OrchestratorConfig
from experl.logger.mlflow_logger import MLFlowLogger
from experl.trainer.base_trainer import BaseTrainer
from experl.utils.dataset_utils import get_dataset_metadata
from experl.utils.logging_utils import get_logger
from experl.utils.trainer_utils import (
    get_device,
    get_dtype,
    get_tracking_path,
    parse_cli_args,
    sanitize_model,
)


log = get_logger(__name__)


class RewardModelTrainer(BaseTrainer):

    def __init__(
            self,
            config: OrchestratorConfig,
            mlflow_logger: MLFlowLogger,
    ):
        super().__init__(
            trainer_name="reward_model",
            config=config,
            mlflow_logger=mlflow_logger,
        )
        self.model_name_or_path = self.config.ppo.reward_model_name_or_path
        self.trainer_args = RewardConfig(
            **OmegaConf.to_container(self.config.ppo.reward)
        )

    def load_dataset(self):
        dataset = load_dataset(self.config.dataset.preference.path, name=self.config.dataset.preference.config)
        self.train_dataset = dataset[self.config.dataset.preference.train_split]
        self.eval_dataset = dataset[
            self.config.dataset.preference.test_split] if self.trainer_args.eval_strategy != "no" else None
        self.log_dataset()

    def log_dataset(self):
        self.mlflow_logger.log_dataset_metadata(get_dataset_metadata(self.train_dataset, self.tokenizer, name="train"))
        self.mlflow_logger.log_dataset(
            from_huggingface(self.train_dataset),
            context="train",
            model_id=self.config.ppo.reward_model_name_or_path,
        )

        if self.eval_dataset:
            self.mlflow_logger.log_dataset_metadata(
                get_dataset_metadata(self.eval_dataset, self.tokenizer, name="train"))
            self.mlflow_logger.log_dataset(
                from_huggingface(self.eval_dataset),
                context="test",
                model_id=self.config.ppo.reward_model_name_or_path,
            )

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.ppo.reward_model_name_or_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.config.ppo.reward_model_name_or_path,
            dtype=get_dtype(self.config.model.dtype),
            num_labels=1,
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        sanitize_model(self.model, self.tokenizer)
        self.model.to(get_device())

    def create_trainer(self):
        # self.trainer_args.eos_token = self.tokenizer.eos_token
        # self.trainer_args.gradient_checkpointing = False
        self.trainer = RewardTrainer(
            model=self.model,
            args=self.trainer_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
            processing_class=self.tokenizer,
        )

    def train_model(self):
        self.trainer.train()

    @staticmethod
    def run(args, overrides, nested=True) -> OrchestratorConfig:
        main_config = ConfigLoader.load_config(args, overrides)
        stage = "reward"
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
            trainer = RewardModelTrainer(main_config, mlogger)
            trainer.train()
        return main_config


if __name__ == "__main__":
    cli_args, cli_overrides = parse_cli_args()
    RewardModelTrainer.run(cli_args, cli_overrides)
