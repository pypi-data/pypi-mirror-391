from datasets import load_dataset
from mlflow.data.huggingface_dataset import from_huggingface
from omegaconf import OmegaConf
from transformers import AutoModelForCausalLM, AutoTokenizer

from experl.config.config_loader import ConfigLoader
from experl.config.schema.config_classes import EvalConfig, OrchestratorConfig
from experl.evaluation.evaluator import BaseEvaluator
from experl.evaluation.judge_evaluator import DPOJudgeEvaluator, EvaluationResult
from experl.logger.mlflow_logger import MLFlowLogger
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


class DPOEvaluator(BaseEvaluator):

    def __init__(
            self,
            config: OrchestratorConfig,
            mlflow_logger: MLFlowLogger,
    ):
        self.base_tokenizer = None
        self.base_model = None
        self.dpo_model = None
        self.judge_model = None
        self.judge_tokenizer = None
        self.eval_prompt_dataset = None
        super().__init__(
            trainer_name="eval_dpo",
            config=config,
            mlflow_logger=mlflow_logger,
        )
        self.eval_args = EvalConfig(**OmegaConf.to_container(self.config.dpo.eval))

    def eval_model(self):
        self.judge_tokenizer.padding_side = "left"
        judge_evaluator = DPOJudgeEvaluator(
            self.base_model,
            self.dpo_model,
            self.judge_model,
            self.base_tokenizer,
            self.judge_tokenizer,
            self.config,
            self.result_file_path,
        )
        result: EvaluationResult = judge_evaluator.evaluate(
            self.eval_prompt_dataset, self.eval_args.batch_size
        )
        self.mlflow_logger.log_metrics(result.metrics)
        self.mlflow_logger.log_dict(
            result.results, f"eval/{self.config.dpo.eval.output_file}"
        )
        self.eval_summary(result)

    def load_model(self):
        model_name_or_path = get_model_id(self.config.model_name_or_path)
        base_model_path = create_file_path(
            self.config,
            f"sft_model/final-sft_model-{model_name_or_path}",
        )
        dpo_model_path = create_file_path(
            self.config,
            f"dpo_model/final-dpo_model-{model_name_or_path}",
        )
        self.load_judge_model(self.config.dpo.judge.model_name_or_path)
        self.load_base_model(base_model_path)
        self.load_dpo_model(dpo_model_path)

    def load_judge_model(self, judge_model_id: str) -> None:
        log.debug(f"judge_model_id = {judge_model_id}")
        self.judge_tokenizer = AutoTokenizer.from_pretrained(
            judge_model_id, padding_side=self.config.model.padding_side
        )
        self.judge_model = AutoModelForCausalLM.from_pretrained(
            judge_model_id,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        sanitize_model(self.judge_model, self.judge_tokenizer)
        self.judge_model.to(get_device())

    def load_base_model(self, base_model_path) -> None:
        log.debug(f"base_model_path = {base_model_path}")
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        self.base_tokenizer = get_tokenizer(base_model_path, "left")
        sanitize_model(self.base_model, self.base_tokenizer)
        self.base_model.to(get_device())

    def load_dpo_model(self, dpo_model_path) -> None:
        log.debug(f"[loader] Loading tokenizer from: {dpo_model_path}")
        log.debug(f"[loader] Loading model: {dpo_model_path}")
        self.dpo_model = AutoModelForCausalLM.from_pretrained(
            dpo_model_path,
            dtype=get_dtype(self.config.model.dtype),
            use_cache=False,
            attn_implementation=self.config.model.attn_implementation,
        )
        sanitize_model(self.dpo_model, self.judge_tokenizer)
        self.dpo_model.to(get_device())

    def load_dataset(self):
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
        model_evaluator = DPOEvaluator(main_config, mlogger)
        model_evaluator.eval()
