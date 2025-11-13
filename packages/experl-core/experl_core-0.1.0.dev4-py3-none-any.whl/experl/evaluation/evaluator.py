import os
from abc import abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path

from experl.config.schema.config_classes import OrchestratorConfig
from experl.logger.mlflow_logger import MLFlowLogger
from experl.utils.common_utils import get_file_text, get_sys_info
from experl.utils.logging_utils import get_logger
from experl.utils.trainer_utils import create_file_path


log = get_logger(__name__)


@dataclass
class EvaluationResult:
    wins: int
    losses: int
    ties: int
    total: int
    results: []
    metrics: dict


class BaseEvaluator:

    def __init__(
        self,
        trainer_name,
        config: OrchestratorConfig,
        mlflow_logger: MLFlowLogger,
    ):
        self.result_summary_file_path = None
        self.result_file_path = None
        self.output_dir = None
        self.eval_args = None
        self.trainer_name = trainer_name
        self.config = config
        self.mlflow_logger = mlflow_logger
        self.output_dir = os.path.join(
            self.config.run_base_dir,
            self.trainer_name,
        )

    def prepare_args(self) -> None:
        self.eval_args.output_dir = self.output_dir
        self.eval_args.logging_dir = os.path.join(self.output_dir, "runs")
        file_path = Path(create_file_path(self.config, self.trainer_name))
        file_path.mkdir(parents=True, exist_ok=True)
        self.result_file_path = create_file_path(
            self.config,
            f"{self.trainer_name}/{self.eval_args.output_file}",
        )
        file_name = (
            self.config.ppo.eval.summary_file
            if self.config.config_name == "ppo"
            else self.config.dpo.eval.summary_file
        )

        self.result_summary_file_path = create_file_path(
            self.config, f"{self.trainer_name}/{file_name}"
        )

    def eval(self) -> None:
        self.prepare_args()
        self.mlflow_logger.log_dict(get_sys_info(), "system_info.json")
        self.mlflow_logger.log_dict(asdict(self.eval_args), "eval_args.json")

        self.load_model()
        self.load_dataset()
        self.eval_model()
        self.log_eval_results()

    def log_eval_results(self) -> None:
        if self.result_file_path is not None:
            file_name = (
                self.config.ppo.eval.output_file
                if self.config.config_name == "ppo"
                else self.config.dpo.eval.output_file
            )
            final_log_string = get_file_text(self.result_file_path)
            self.mlflow_logger.log_text(
                final_log_string,
                artifact_file=f"eval/{file_name}.txt",
            )

    @abstractmethod
    def eval_model(self):
        pass

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def load_dataset(self):
        pass

    def eval_summary(
        self,
        result: EvaluationResult,
    ):
        win_rate = (result.wins / result.total) * 100
        lose_rate = (result.losses / result.total) * 100
        tie_rate = (result.ties / result.total) * 100
        summary_text = f"""
                -------------------
                Evaluation Summary
                -------------------
                Name : {self.trainer_name}
                Total Prompts Evaluated: {result.total}
                "{self.trainer_name} Wins: {result.wins} ({win_rate:.2f}%)"
                "{self.trainer_name} Losses: {result.losses} ({lose_rate:.2f}%)"
                "Ties: {result.ties} ({tie_rate:.2f}%)"
                -------------------
                Detailed results saved to: {self.result_file_path}
                """
        log.info(summary_text)
        self.mlflow_logger.log_metrics(
            {
                "total_prompts_evaluated": result.total,
                "wins": result.wins,
                "losses": result.losses,
                "result.ties": result.ties,
                "win_rate": win_rate,
                "lose_rate": lose_rate,
                "tie_rate": tie_rate,
            }
        )
        file_name = (
            self.config.ppo.eval.summary_file
            if self.config.config_name == "ppo"
            else self.config.dpo.eval.summary_file
        )

        with open(self.result_summary_file_path, "w") as file:
            file.write(summary_text)
        self.mlflow_logger.log_text(summary_text, artifact_file=f"eval/{file_name}")
