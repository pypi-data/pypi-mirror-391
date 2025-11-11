import os
from abc import abstractmethod
from dataclasses import asdict

from experl.config.schema.config_classes import OrchestratorConfig
from experl.logger.mlflow_logger import MLFlowLogger
from experl.utils.common_utils import get_sys_info
from experl.utils.logging_utils import get_logger
from experl.utils.trainer_utils import get_model_id


log = get_logger(__name__)


class BaseTrainer:
    """
    An abstract base class for all trainers in the RLHF pipeline (SFT, RM, PPO).

    This class handles common functionalities like loading model, load dataset , creating TRL trainer,
    training and saving model into output directory.
    """

    def __init__(
            self,
            trainer_name,
            config: OrchestratorConfig,
            mlflow_logger: MLFlowLogger,
    ):
        self.model_name_or_path = None
        self.model = None
        self.tokenizer = None
        self.config = config
        self.trainer_name = trainer_name
        self.mlflow_logger = mlflow_logger
        self.trainer = None
        self.train_dataset = None
        self.eval_dataset = None
        self.trainer_args = None
        self.output_dir = os.path.join(
            self.config.run_base_dir,
            self.trainer_name,
        )

    @abstractmethod
    def create_trainer(self):
        pass

    @abstractmethod
    def train_model(self):
        pass

    @abstractmethod
    def load_model(self):
        """Subclasses must implement this to load their specific model."""
        pass

    @abstractmethod
    def load_dataset(self):
        """Subclasses must implement this to load their specific dataset."""
        pass

    def prepare_args(self):
        self.trainer_args.output_dir = self.output_dir
        self.trainer_args.logging_dir = os.path.join(self.output_dir, "runs")

    def train(self):
        self.prepare_args()
        log.info(f"Training output will be saved to: {self.output_dir}")
        self.mlflow_logger.log_dict(get_sys_info(), "system_info.json")
        self.mlflow_logger.log_dict(asdict(self.trainer_args), "training_args.json")
        self.load_model()
        self.load_dataset()
        self.create_trainer()
        log.debug(f"training args = {self.trainer_args}")
        self.train_model()
        self.trainer.accelerator.print("✅ Training completed.")
        self.save_model()

    def save_model(self):
        final_model_id = get_model_id(self.model_name_or_path)
        final_model_path = os.path.join(
            self.output_dir, f"final-{self.trainer_name}-{final_model_id}"
        )
        log.info(f"Model and self.tokenizer saved to {final_model_path}")
        self.trainer.accelerator.print(f"💾 Model saved to {final_model_path}.")
        self.trainer.save_model(final_model_path)
        self.tokenizer.save_pretrained(final_model_path)
        self.log_model(final_model_id, final_model_path)

    def log_model(self, final_model_id, final_model_path):
        self.mlflow_logger.log_artifact(
            file_path=final_model_path, artifact_path="model"
        )
        self.mlflow_logger.log_model(final_model_path, final_model_id)
