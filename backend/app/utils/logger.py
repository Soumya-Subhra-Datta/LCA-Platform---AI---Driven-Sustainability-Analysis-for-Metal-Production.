import os
import sys
import logging
from pathlib import Path
from loguru import logger

LOG_DIR = Path(__file__).resolve().parent.parent / "outputs" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"), format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add(str(LOG_DIR / "app_{time:YYYY-MM-DD}.log"), rotation="10 MB", retention="30 days", level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")
logger.add(str(LOG_DIR / "errors_{time:YYYY-MM-DD}.log"), rotation="10 MB", retention="90 days", level="ERROR", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.level
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).handlers = []
    logging.getLogger(name).propagate = True
