import logging
import pathlib

from dynaconf import Dynaconf
from oemoflex.tools.helpers import load_yaml

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
root_logger.setLevel(LOGGING_LEVEL)

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


LABELS = load_yaml(CONFIG_PATH / "labels" / f"{settings.labels}.yml")
raw_colors = load_yaml(CONFIG_PATH / "colors.yml")
COLORS = {}
for label, color in raw_colors.items():
    if label not in LABELS:
        continue
    COLORS[LABELS[label]] = color
    COLORS[f"{LABELS[label]} in"] = color
    COLORS[f"{LABELS[label]} out"] = color
