import logging
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler

from spotkit.config import CONFIG_DIR

# Config
LOG_FILE = CONFIG_DIR / "spotkit.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Default formatter structure
FILE_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(module)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Handlers
console_handler = RichHandler(
    level=logging.WARN,
    markup=True,
    rich_tracebacks=True,
)

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=3,
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(FILE_FORMAT, DATE_FORMAT))

# Root logger config
logging.basicConfig(
    level=logging.DEBUG,
    format=FILE_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[console_handler, file_handler],
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
