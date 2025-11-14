import logging
from datetime import date, datetime
from socket import socket
from typing import Any
from uuid import UUID

from django.http import HttpRequest

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}


def is_builtin_attr(key: str) -> bool:
    return key in LOG_RECORD_BUILTIN_ATTRS


def parse_log_record_extra(record: logging.LogRecord) -> dict[str, str]:
    """
    Logger's `extra` fields are stored inside record's __dict__.
    This method extracts those as separate dictionary.
    """

    extra: dict[str, Any] = {}

    for key in record.__dict__:
        if is_builtin_attr(key):
            continue

        extra[key] = record.__dict__[key]

    return extra


def json_serialize(input: object):
    """Custom serializer for objects that are not serializable by default"""

    if isinstance(input, (datetime, date)):
        return input.isoformat()

    if isinstance(input, socket):
        return {
            "source": "socket",
            "socket": input.getsockname(),
            "peer": input.getpeername(),
        }

    if isinstance(input, HttpRequest):
        return {
            "source": "http",
            "method": input.method,
            "path": input.path,
        }

    if isinstance(input, UUID):
        return str(input)

    # If you see this TypeError related to object not being serializable,
    # it means that it should be most likely handled in here.
    return input
