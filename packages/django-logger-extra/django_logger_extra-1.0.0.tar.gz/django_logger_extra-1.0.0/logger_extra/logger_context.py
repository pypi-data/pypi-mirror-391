from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Any

LoggerContext = dict[str, Any]

_logger_context: ContextVar[LoggerContext] = ContextVar("LoggerContext", default=None)


@contextmanager
def logger_context(ctx: LoggerContext):
    token: Token[LoggerContext]

    try:
        merged = get_logger_context() | ctx
        token = _logger_context.set(merged)
        yield merged
    finally:
        _logger_context.reset(token)


def get_logger_context() -> LoggerContext:
    return _logger_context.get({})
