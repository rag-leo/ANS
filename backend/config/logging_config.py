import json
import logging
import sys
from datetime import datetime, timezone

# Standard LogRecord attributes, used to separate caller-supplied
# `extra={...}` fields from the record's own bookkeeping fields.
_LOG_RECORD_RESERVED_ATTRS = set(
    logging.LogRecord(
        "dummy", logging.INFO, "", 0, "", (), None
    ).__dict__.keys()
) | {"message"}


class JsonFormatter(logging.Formatter):

    def format(self, record):

        payload = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(
                record.exc_info
            )

        if record.stack_info:
            payload["stack_info"] = self.formatStack(
                record.stack_info
            )

        extra = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _LOG_RECORD_RESERVED_ATTRS
        }

        if extra:
            payload["extra"] = extra

        return json.dumps(payload, default=str)


def configure_logging(log_level="INFO"):

    root_logger = logging.getLogger()

    root_logger.setLevel(log_level)

    if root_logger.handlers:
        root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())

    root_logger.addHandler(console_handler)


def get_logger(name: str):
    return logging.getLogger(name)
