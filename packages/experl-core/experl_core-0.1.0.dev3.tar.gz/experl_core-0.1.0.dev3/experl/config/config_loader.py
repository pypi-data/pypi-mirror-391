from hydra import compose, initialize

from experl.config.schema.config_classes import OrchestratorConfig
from experl.utils.logging_utils import get_logger


log = get_logger(__name__)


class ConfigLoader:

    @staticmethod
    def from_overrides(
        config_name: str, overrides: list[str] = None
    ) -> OrchestratorConfig:
        config_path = "yaml"
        log.debug(f"Config path : {config_path}")
        with initialize(config_path=config_path):
            cfg = compose(config_name=config_name, overrides=overrides or [])
        return cfg

    @staticmethod
    def get_orchestrator_config(
        config_name="ppo", overrides: list[str] = None
    ) -> OrchestratorConfig:
        log.debug(f"config config_name = {config_name}")
        log.debug(f"config overrides = {overrides}")
        return ConfigLoader.from_overrides(config_name=config_name, overrides=overrides)

    @staticmethod
    def get_config(
        config_name="ppo", overrides: list[str] = None
    ) -> OrchestratorConfig:
        config = ConfigLoader.get_orchestrator_config(
            config_name=config_name, overrides=overrides
        )
        return config

    @staticmethod
    def load_config(args, overrides) -> OrchestratorConfig:
        log.debug(f"args.config_name === {args.config_name}")
        config = ConfigLoader.get_config(
            config_name=args.config_name,
            overrides=overrides,
        )
        config.config_name = args.config_name
        return config


if __name__ == "__main__":
    main_config = ConfigLoader.from_overrides(config_name="ppo")
    log.info(f" config = {main_config}")
