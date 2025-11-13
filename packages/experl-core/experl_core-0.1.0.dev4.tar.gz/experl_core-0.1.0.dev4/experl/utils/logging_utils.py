# https://github.com/skypilot-org/skypilot/blob/86dc0f6283a335e4aa37b3c10716f90999f48ab6/sky/sky_logging.py

import logging
import sys
from logging import StreamHandler


_root_logger = logging.getLogger("experl")
_default_handler: StreamHandler = None


def _setup_logger():
    _root_logger.setLevel(logging.INFO)
    global _default_handler
    if _default_handler is None:
        _default_handler = logging.StreamHandler(sys.stdout)
        _default_handler.flush = sys.stdout.flush  # type: ignore
        _default_handler.setLevel(logging.INFO)
        _root_logger.addHandler(_default_handler)
    _root_logger.propagate = False


_setup_logger()


def get_logger(name: str):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    log.addHandler(_default_handler)
    log.propagate = False
    return log
