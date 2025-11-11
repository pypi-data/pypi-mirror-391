import sys
from argparse import Namespace

from experl.rlhf_orchestrator import RLHFOrchestrator
from experl.utils.logging_utils import get_logger


log = get_logger(__name__)


def main():
    try:
        args = sys.argv[1:]
        if args[0] == "ppo":
            cli_args = Namespace(config_name="ppo")
        else:
            cli_args = Namespace(config_name="dpo")

        cli_overrides = sys.argv[2:] if len(sys.argv) > 2 else []
        log.info(f" args = {args}")
        log.info(f" cli_overrides = {cli_overrides}")

        RLHFOrchestrator.run(cli_args, cli_overrides)
    except Exception as e:
        log.error(f"Exception during RLHF Orchestrator execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
