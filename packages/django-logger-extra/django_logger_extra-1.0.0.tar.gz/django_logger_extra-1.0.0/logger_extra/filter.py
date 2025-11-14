import logging

from logger_extra.logger_context import get_logger_context
from logger_extra.utils import is_builtin_attr, json_serialize


class LoggerContextFilter(logging.Filter):
    """
    This filter merges user-provided extras with the active logger context variables.

    Values are written directly into the LogRecord's __dict__, the same place native
    extra fields are stored. This ensures that all formatters can access these context
    fields seamlessly, treating them just like native `extra` fields.

    For example, the following snippet stores both `greet` and `who` in the LogRecord:

    ```python
    with logger_context({"greet": "Hello"}) as ctx:
        logger.info("Lorem Ipsum...", extra={"who": "World"})
    ```
    """

    def __init__(self, name: str = ""):
        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        logger_context = get_logger_context()

        for key, value in logger_context.items():
            if is_builtin_attr(key):
                continue

            record.__dict__[key] = json_serialize(value)

        return True
