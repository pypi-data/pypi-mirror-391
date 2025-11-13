import logging
import sys
from logging import config
from typing import Optional

_dev_handler = logging.StreamHandler(sys.stdout)
_dev_handler.setLevel(logging.DEBUG)

_FORMAT = "[%(levelname)s %(process)d %(asctime)s %(filename)s:%(lineno)d] %(message)s"
_DATE_FORMAT = "%m-%d %H:%M:%S"

DEFAULT_LOGGING_CONFIG = {
    "formatters": {
        "standard": {
            "datefmt": _DATE_FORMAT,
            "format": _FORMAT,
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "version": 1,
}


def _configure_vllm_root_logger() -> None:
    logging_config: Optional[dict] = None
    logging_config = DEFAULT_LOGGING_CONFIG

    if logging_config:
        config.dictConfig(logging_config)

def init_logger(name: str):
    return logging.getLogger(name)

_configure_vllm_root_logger()
