import logging
import pathlib
import sys

import yaml
from dynaconf import Dynaconf

CONFIG_PATH = pathlib.Path(__file__).parent
ROOT_DIR = CONFIG_PATH.parent.parent

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

root_logger = logging.getLogger()
root_logger.setLevel(LOGGING_LEVEL)

stream_formatter = logging.Formatter("%(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.addFilter(LevelFilter(logging.ERROR))
root_logger.addHandler(stream_handler)

DEFAULT_LOGFILE = "snake.log"


def add_snake_logger(rulename):
    """
    Adds logging to file

    Logfile is read from input parameters, ending with ".log"
    This is done in order to add loggers for subprocesses (like data_preprocessing.py),
    where logfile is unknown.
    """
    logger = logging.getLogger(rulename)
    logfile = next(
        (item for item in sys.argv if item.endswith(".log")), DEFAULT_LOGFILE
    )
    handler = logging.FileHandler(logfile)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(file_formatter)
    logger.addHandler(handler)
    return logger


def load_yaml(file_path):
    with open(file_path, "r") as yaml_file:
        yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)

    return yaml_data


LABELS = load_yaml(CONFIG_PATH / "labels" / f"{settings.labels}.yml")
raw_colors = load_yaml(CONFIG_PATH / "colors.yml")
COLORS = {}
for label, color in raw_colors.items():
    if label not in LABELS:
        continue
    COLORS[LABELS[label]] = color
    COLORS[f"{LABELS[label]} in"] = color
    COLORS[f"{LABELS[label]} out"] = color
