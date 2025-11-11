from datasets import load_dataset
from mlflow.data.huggingface_dataset import from_huggingface
from omegaconf import OmegaConf
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from experl.config.config_loader import ConfigLoader
from experl.config.schema.config_classes import EvalConfig, OrchestratorConfig
from experl.evaluation.evaluator import BaseEvaluator
from experl.evaluation.judge_evaluator import EvaluationResult
from experl.evaluation.reward_judge_evaluator import RewardJudgeEvaluator
from experl.logger.mlflow_logger import MLFlowLogger
from experl.models.reward_model import RewardModel
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


class PPOEvaluator(BaseEvaluator):

    def __init__(
            self,
            config: OrchestratorConfig,
            mlflow_logger: MLFlowLogger,
    ):
        self.reward_tokenizer = None
        self.reward_model = None
        self.base_model = None
        self.ppo_model = None
        self.base_tokenizer = None
        self.eval_prompt_dataset = None
        super().__init__(
            trainer_name="eval_ppo",
            config=config,
            mlflow_logger=mlflow_logger,
        )
        self.eval_args = EvalConfig(**OmegaConf.to_container(self.config.ppo.eval))

    def load_model(self) -> None:
        model_name_or_path = get_model_id(self.config.model_name_or_path)
        reward_model_name_or_path = get_model_id(self.config.ppo.reward_model_name_or_path)

        sft_model_path = create_file_path(
            self.config,
            f"sft_model/final-sft_model-{model_name_or_path}",
        )
        reward_model_path = create_file_path(
            self.config,
            f"reward_model/final-reward_model-{reward_model_name_or_path}",
        )
        ppo_model_path = create_file_path(
            self.config,
            f"ppo_model/final-ppo_model-{model_name_or_path}",
        )

        self.load_ppo_model(ppo_model_path)
        self.load_base_model(sft_model_path)
        self.load_reward_model(reward_model_path)

    def load_ppo_model(self, ppo_model_path) -> None:
        log.debug(f"Loading tokenizer from: {ppo_model_path}")
        self.base_tokenizer = AutoTokenizer.from_pretrained(
            ppo_model_path, padding_side=self.config.model.padding_side
        )
        log.debug(f"Loading model from: {ppo_model_path}")
        self.ppo_model = AutoModelForCausalLM.from_pretrained(
            ppo_model_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        sanitize_model(self.ppo_model, self.base_tokenizer)
        self.ppo_model.to(get_device())

    def load_base_model(self, sft_model_path) -> None:
        log.debug(f"Loadin base model from : {sft_model_path}")
        self.base_model = AutoModelForCausalLM.from_pretrained(
            sft_model_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        self.base_model.to(get_device())
        sanitize_model(self.base_model, self.base_tokenizer)

    def load_reward_model(self, reward_model_path) -> None:
        log.debug(f"loading reward model from: {reward_model_path}")
        self.reward_tokenizer = get_tokenizer(
            reward_model_path, self.config.model.padding_side
        )
        rm_config = AutoConfig.from_pretrained(
            reward_model_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        self.reward_model = RewardModel(rm_config)
        sanitize_model(self.reward_model, self.reward_tokenizer)
        self.reward_model.to(get_device())

    def load_dataset(self) -> None:
        log.debug(
            f"Loading evaluation dataset from: {self.config.dataset.eval.path}"
        )
        self.eval_prompt_dataset = load_dataset(self.config.dataset.eval.path,
                                                name=self.config.dataset.eval.config,
                                                split=self.config.dataset.eval.train_split)


        self.mlflow_logger.log_dataset_metadata(
            get_dataset_metadata(self.eval_prompt_dataset, self.base_tokenizer, name="eval"))

        self.mlflow_logger.log_dataset(
            from_huggingface(self.eval_prompt_dataset),
            context="eval",
            model_id=self.config.model_name_or_path,
        )

    def eval_model(self) -> None:
        self.base_tokenizer.padding_side = "left"
        reward_evaluator = RewardJudgeEvaluator(
            self.base_model,
            self.ppo_model,
            self.reward_model,
            self.base_tokenizer,
            self.reward_tokenizer,
            self.config,
            self.result_file_path,
        )
        result: EvaluationResult = reward_evaluator.evaluate(
            self.eval_prompt_dataset, self.eval_args.batch_size
        )
        self.mlflow_logger.log_metrics(result.metrics)
        self.mlflow_logger.log_dict(
            result.results, f"eval/{self.config.ppo.eval.output_file}"
        )
        self.eval_summary(result)


if __name__ == "__main__":
    main_config: OrchestratorConfig
    args, overrides = parse_cli_args()
    main_config = ConfigLoader.load_config(args, overrides)
    stage = "eval"
    with MLFlowLogger(
            experiment_name=main_config.project_name,
            tracking_uri=get_tracking_path(main_config),
            run_name=f"{stage}__{main_config.run_name}",
            nested=True,
            tags={
                "stage": stage,
                "run_name": f"{stage}__{main_config.run_name}",
                "project_name": main_config.project_name,
            },
    ) as mlogger:
        mlogger.log_args_and_overrides(args, overrides)
        model_evaluator = PPOEvaluator(main_config, mlogger)
        model_evaluator.eval()
