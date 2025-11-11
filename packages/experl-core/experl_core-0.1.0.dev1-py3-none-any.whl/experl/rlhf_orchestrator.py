import os
import random
import time

import numpy as np
import torch
from omegaconf import OmegaConf

from experl.config.config_loader import ConfigLoader
from experl.config.schema.config_classes import OrchestratorConfig
from experl.logger.mlflow_logger import MLFlowLogger
from experl.utils.common_utils import get_sys_info
from experl.utils.logging_utils import get_logger
from experl.utils.process_runner import ProcessRunner
from experl.utils.trainer_utils import (
    generate_run_name,
    get_tracking_path,
    parse_cli_args,
)


log = get_logger(__name__)


class RLHFOrchestrator:

    def __init__(self, config: OrchestratorConfig):
        torch.manual_seed(config.seed)
        np.random.seed(config.seed)
        random.seed(config.seed)
        self.config: OrchestratorConfig = config

    def run_pipeline(self, overrides: list[str] = None):
        common_args = [
            "--config-name",
            f"{self.config.config_name}",
            f"++project_name={self.config.project_name}",
            f"++run_name={self.config.run_name}",
            f"++run_base_dir={self.config.run_base_dir}",
        ]

        if overrides is not None:
            for argument in overrides:
                log.debug(f"overridden argument : {argument}")
                common_args.append(argument)

        for stage_name, stage_config in self.config.stages.items():
            log.debug(f"stage_name = {stage_name}")
            log.debug(f"stage_config = {stage_config}")
            if stage_config["enabled"]:
                self.execute_stage(common_args, stage_config["script"], stage_name)
            else:
                log.info(f"Stage {stage_name} is disabled. Skipping.")

        log.info(
            f"\nRLHF Pipeline for {str(self.config.config_name).upper()} finished successfully!"
        )

    def execute_stage(self, common_args, script_path, stage_name):
        log.info(f"Stage args : {common_args} ")
        ProcessRunner.run_stage(stage_name, script_path, common_args)
        time.sleep(self.config.state_sleep_interval)

    @staticmethod
    def run(args, overrides):
        config: OrchestratorConfig
        config = ConfigLoader.load_config(args, overrides)

        log.info("===" * 40)
        log.info(f"{' ' * 40} Starting RLHF for {str(config.config_name).upper()}")
        log.info("===" * 40)

        stage = "orchestrator"
        if not config.run_name:
            config.run_name = generate_run_name(
                base_name=config.model_name_or_path,
                task=config.exp_name,
                tag=config.config_name,
            )
            config.run_base_dir = os.path.join(
                config.root_dir, config.project_name, config.run_name
            )

        with MLFlowLogger(
            experiment_name=config.project_name,
            tracking_uri=get_tracking_path(config),
            run_name=config.run_name,
            nested=False,
            tags={
                "stage": stage,
                "run_name": config.run_name,
                "project_name": config.project_name,
            },
        ) as mlflow_logger:
            RLHFOrchestrator.log_configurations(config, mlflow_logger, args, overrides)
            orchestrator = RLHFOrchestrator(config)
            orchestrator.run_pipeline(overrides=overrides)
        return config

    @staticmethod
    def log_configurations(
        config: OrchestratorConfig,
        mlflow_logger: MLFlowLogger,
        args,
        overrides,
    ):
        try:
            RLHFOrchestrator.log_deptree(mlflow_logger)
            mlflow_logger.log_args_and_overrides(args, overrides)
            mlflow_logger.log_dict(get_sys_info(), "system_info.json")
            mlflow_logger.log_dict(
                OmegaConf.to_container(config, resolve=True),
                "config.json",
            )
        except Exception as e:
            log.error(f"Failed to log configurations - {e}")

    @staticmethod
    def log_deptree(mlflow_logger):
        if os.path.exists("uv.lock"):
            mlflow_logger.log_artifact("uv.lock")
        elif os.path.exists("poetry.lock"):
            mlflow_logger.log_artifact("poetry.lock")
        elif os.path.exists("requirements.txt"):
            mlflow_logger.log_artifact("requirements.txt")


if __name__ == "__main__":
    cli_args, cli_overrides = parse_cli_args()
    RLHFOrchestrator.run(cli_args, cli_overrides)
