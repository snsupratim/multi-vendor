from loguru import logger
import sys

logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format=
    "{time} | {level} | {message}"
)

logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO"
)

from core.mongo_sink import mongo_sink_handler

logger.add(
    mongo_sink_handler,
    level="INFO"
)