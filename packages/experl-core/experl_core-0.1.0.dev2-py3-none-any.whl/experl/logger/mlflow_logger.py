import json
import os
from argparse import Namespace
from datetime import datetime

import mlflow
from mlflow.entities import LoggedModelInput

from experl.utils.logging_utils import get_logger


log = get_logger(__name__)


class MLFlowLogger:

    def __init__(
            self,
            experiment_name: str = "exp",
            tracking_uri: str | None = None,
            run_name: str | None = None,
            tags: dict[str, str] | None = None,
            nested: bool = False,
    ):

        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(experiment_name)
        exp = mlflow.get_experiment_by_name(experiment_name)
        if exp is None:
            self.experiment_id = mlflow.create_experiment(experiment_name)
        else:
            self.experiment_id = exp.experiment_id
        self.run_name = run_name or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.tags = tags or {}
        self.nested = nested
        self.active_run = None

    def end_run(self) -> None:
        if self.active_run:
            mlflow.end_run()
            self.active_run = None
            log.debug(f"MLflow run ended: {self.run_name}")

    def __enter__(self):
        self.active_run = mlflow.start_run(
            run_name=self.run_name,
            nested=self.nested,
            tags=self.tags,
            parent_run_id=os.environ["MLFLOW_PARENT_RUN_ID"] if self.nested else "",
        )
        if self.nested is False:
            os.environ["MLFLOW_PARENT_RUN_ID"] = self.active_run.info.run_id
        mlflow.autolog(log_models=True, disable=False)
        log.info(f"Run ID : {self.active_run.info.run_id}, Name : {self.run_name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_run()
        if self.nested is False:
            os.environ["MLFLOW_PARENT_RUN_ID"] = ""

    @staticmethod
    def log_dataset(dataset, context, model_id) -> None:
        if dataset is None:
            log.warning(f"Dataset not provided to log : {dataset}")
            return
        if model_id is None:
            log.warning(f"Model id not provided to log dataset: {model_id}")
            return
        try:
            _model = LoggedModelInput(model_id=model_id)
            mlflow.log_input(dataset=dataset, context=context, model=_model)
        except Exception as e:
            log.error(f"Failed to log dataset {dataset}: {e}")

    @staticmethod
    def log_dict(metadata: dict, file_name: str) -> None:
        if metadata is None:
            log.warning(f"No metadata provided: {metadata}")
            return
        if file_name is None:
            log.warning(f"No file_name provided: {file_name}")
            return
        mlflow.log_dict(metadata, f"{file_name}")

    @staticmethod
    def log_dataset_metadata(metadata: dict, artifact_subdir: str = "datasets",
                             exclude_tensor_ids: bool = False) -> None:
        try:
            name = metadata['dataset_name']
            preview_dict = metadata['preview_dict']
            if exclude_tensor_ids:
                if isinstance(preview_dict, dict):
                    for field in ["input_ids", "attention_mask", "token_type_ids"]:
                        preview_dict.pop(field, None)
                elif isinstance(preview_dict, list):
                    for sample in preview_dict:
                        for field in ["input_ids", "attention_mask", "token_type_ids"]:
                            sample.pop(field, None)

            mlflow.log_text(
                json.dumps(preview_dict, indent=2, ensure_ascii=False),
                f"datasets/{name}_preview.json",
            )
            if metadata.get('preview_dict'):
                metadata.pop('preview_dict')
            MLFlowLogger.log_dict(metadata, f"{artifact_subdir}/{name}_metadata.json")
        except Exception as e:
            log.error(f"Failed to log dataset metadata - exception {e}")

    @staticmethod
    def log_metrics(metrics: dict[str, float], step: int | None = None) -> None:
        if metrics is None:
            log.warning(f"No metrics provided {metrics}")
            return
        try:
            mlflow.log_metrics(metrics, step=step)
            log.debug(f"Logged metrics: {metrics}")
        except Exception as e:
            log.error(f"Failed to log metrics {metrics}: {e}")

    @staticmethod
    def log_artifact(file_path: str, artifact_path: str | None = None) -> None:
        if os.path.exists(file_path):
            try:
                mlflow.log_artifact(file_path, artifact_path=artifact_path)
                log.debug(f"Logged artifact: {file_path}")
            except Exception as e:
                log.error(f"Failed to log artifact from {file_path}: {e}")
        else:
            log.warning(f"Artifact not found: {file_path}")

    @staticmethod
    def log_artifacts(dir_path: str, artifact_path: str | None = None) -> None:
        if os.path.isdir(dir_path):
            try:
                mlflow.log_artifacts(dir_path, artifact_path=artifact_path)
                log.debug(
                    f"Logged directory contents: {dir_path} to {artifact_path or 'root'}"
                )
            except Exception as e:
                log.error(f"Failed to log artifacts from {dir_path}: {e}")
        elif os.path.exists(dir_path):
            log.warning(
                f"Path exists but is not a directory, cannot log artifacts: {dir_path}"
            )
        else:
            log.warning(f"Artifact directory not found: {dir_path}")

    @staticmethod
    def log_text(text: str, artifact_file: str = "logs/log.txt") -> None:
        if text is None:
            log.warning("Attempted to log None text. Skipping.")
            return
        try:
            mlflow.log_text(text=text, artifact_file=artifact_file)
            log.debug(f"Logged text to artifact: {artifact_file}")
        except Exception as e:
            log.error(
                f"Failed to log text to MLflow artifact {artifact_file}: {e}",
                exc_info=True,
            )

    @staticmethod
    def log_model(final_model_path, final_model_name) -> None:
        try:
            mlflow.transformers.log_model(
                transformers_model=final_model_path,
                name=final_model_name,
                task="text-generation",
            )
        except Exception as e:
            log.error(
                f"Failed to log model : model path - {final_model_path}, model name - {final_model_name}: {e}",
                exc_info=True,
            )

    def log_args_and_overrides(self, args, overrides):
        if isinstance(args, Namespace):
            args_dict = vars(args)
        elif isinstance(args, dict):
            args_dict = args
        else:
            args_dict = None

        overrides_dict = None
        if overrides:
            overrides_dict = {}
            for item in overrides:
                if "=" in item:
                    key, val = item.split("=", 1)
                    overrides_dict[key.strip()] = val.strip()
                else:
                    overrides_dict[item.strip()] = True

        self.log_dict(args_dict, "cli/args.json")
        self.log_dict(overrides_dict, "cli/overrides.json")
        return args_dict, overrides_dict
