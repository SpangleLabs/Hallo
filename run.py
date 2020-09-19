import logging
import os

import hallo.hallo
from hallo.inc import logger


def setup_logging() -> None:
    logger.setup_logging()


if __name__ == "__main__":
    hallo = hallo.hallo.Hallo.load_json()
    hallo.start()
