import logging
import pathlib

from dynaconf import Dynaconf

CONFIG_PATH = pathlib.Path(__file__).parent

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[CONFIG_PATH / "settings.yaml", CONFIG_PATH / ".secrets.yaml"],
)


class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level
        super(LevelFilter, self).__init__()

    def filter(self, record):
        return record.levelno != self.level


DEBUG = settings.get("DEBUG", False)
LOGGING_LEVEL = settings.get("LOGGING_LEVEL", logging.DEBUG if DEBUG else logging.INFO)
LOGGING_FOLDER = "logs"

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

stream_formatter = logging.Formatter("%(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.addFilter(LevelFilter(logging.ERROR))
root_logger.addHandler(stream_handler)


def add_snake_logger(logfile, rulename):
    logger = logging.getLogger(rulename)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.FileHandler(logfile)
    handler.setFormatter(file_formatter)
    logger.addHandler(handler)
    return logger
