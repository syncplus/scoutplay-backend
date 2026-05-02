import logging
import os
import re

from context import correlationId
from pythonjsonlogger import jsonlogger

log_level_mapping = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

log_level_name = os.environ.get('LOG_LEVEL', 'INFO')
log_level = log_level_mapping.get(log_level_name.upper(), logging.INFO)

logger = logging.getLogger("scoutplay_api")
logger.setLevel(log_level)


class ContextJsonFormatter(jsonlogger.JsonFormatter):
    def format(self, record):
        _id = correlationId.get()
        if _id:
            _id = str(_id)
            _id = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', _id)
            _id = _id[:100]
        else:
            _id = ""
        record.correlationId = _id

        self._required_fields = [
            "asctime",
            "timestamp",
            "levelname",
            "message",
            "correlationId",
        ]
        return super().format(record)


fmt = ContextJsonFormatter(
    "%(asctime)s %(correlationId)s %(levelname)s %(message)s",
    rename_fields={"asctime": "timestamp"},
    datefmt='%Y-%m-%dT%H:%M:%SZ',
)

ch = logging.StreamHandler()
ch.setFormatter(fmt)
logger.addHandler(ch)

# Redireciona uvicorn para o mesmo formato JSON
logging.getLogger("uvicorn").handlers.clear()
logging.getLogger("uvicorn.error").handlers.clear()
logging.getLogger("uvicorn.access").handlers.clear()

fmt_uvicorn = jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(message)s",
    rename_fields={"asctime": "timestamp"},
    datefmt='%Y-%m-%dT%H:%M:%SZ',
)

uvicorn_handler = logging.StreamHandler()
uvicorn_handler.setFormatter(fmt_uvicorn)
logging.getLogger("uvicorn.error").addHandler(uvicorn_handler)
