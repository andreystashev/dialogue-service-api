import logging
from collections import OrderedDict
from datetime import datetime
from logging import LogRecord

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self,
        log_record: OrderedDict,
        record: LogRecord,
        message_dict: dict,
    ):
        super().add_fields(
            log_record,
            record,
            message_dict,
        )

        message = log_record.pop("message")
        extra = {}
        keys = list(log_record.keys())
        for key in keys:
            extra[key] = log_record.pop(key)

        log_record.update(
            dict(
                message=message,
                timestamp=datetime.utcnow().isoformat(),
                filename=record.filename,
                func=record.funcName,
                line=record.lineno,
                process=record.process,
                thread=record.thread,
                thread_name=record.threadName,
                level=record.levelname.lower(),
                extra=extra,
            )
        )


app_logger = logging.getLogger()
app_logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomJsonFormatter())

app_logger.addHandler(stream_handler)
