import json
import logging

from django.utils import timezone

from logger_extra.utils import json_serialize, parse_log_record_extra


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        extra = parse_log_record_extra(record)
        extra.pop("response", None)

        if record.exc_info:
            extra["exc_info"] = self.formatException(record.exc_info)

        formatted = {
            "message": record.getMessage(),
            "level": record.levelname,
            "name": record.name,
            "time": timezone.now().isoformat(),
            "context": extra,
        }

        return json.dumps(formatted, default=json_serialize)
