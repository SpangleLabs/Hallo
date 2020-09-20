import hallo.hallo
from hallo.inc import logger


if __name__ == "__main__":
    logger.setup_logging()
    hallo = hallo.hallo.Hallo.load_json()
    hallo.start()
