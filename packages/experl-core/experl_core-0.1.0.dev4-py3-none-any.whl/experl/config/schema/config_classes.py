from dataclasses import dataclass, field

from trl import DPOConfig, ModelConfig, PPOConfig, RewardConfig, SFTConfig


@dataclass
class DatasetConfigItem:
    path: str
    config: str = "default"
    train_split: str = "train"
    test_split: str = "test"

@dataclass
class DatasetConfig:
    sft: DatasetConfigItem
    preference: DatasetConfigItem
    prompt: DatasetConfigItem
    eval: DatasetConfigItem



@dataclass
class ModelArguments(ModelConfig):
    padding_side: str = ""


@dataclass
class EvalConfig:
    """Arguments for the evaluation script."""

    output_file: str
    max_new_tokens: int
    batch_size: int
    summary_file: str


@dataclass
class JudgeEvalConfig:
    model_name_or_path: str
    temperature: float
    max_new_tokens: int
    prompt_template: str

@dataclass
class PPOStage:
    reward_model_name_or_path: str
    reward: RewardConfig = field(default_factory=RewardConfig)
    sft: SFTConfig = field(default_factory=SFTConfig)
    ppo: PPOConfig = field(default_factory=PPOConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)

    def items(self):
        return self.__dict__.items()

@dataclass
class DPOStage:
    sft: SFTConfig = field(default_factory=SFTConfig)
    dpo: DPOConfig = field(default_factory=DPOConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    judge: JudgeEvalConfig = field(default_factory=EvalConfig)

    def items(self):
        return self.__dict__.items()

@dataclass
class MLflowConfig:
    """Configuration for MLflow integration."""
    enabled: bool
    tracking_dir: str


@dataclass
class OrchestratorConfig:
    """
    The main configuration dataclass for the entire RLHF Orchestrator.
    This structure directly mirrors the YAML file.
    """

    config_name: str
    model_name_or_path: str
    project_name: str
    exp_name: str
    max_seq_length: int
    run_name: str
    state_sleep_interval: int
    report_to: str
    root_dir: str
    run_base_dir: str
    stages: dict
    seed: int
    mlflow: MLflowConfig = field(default_factory=MLflowConfig)
    model: ModelArguments = field(default_factory=ModelArguments)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    ppo: PPOStage = field(default_factory=PPOStage)
    dpo: DPOStage = field(default_factory=DPOStage)
