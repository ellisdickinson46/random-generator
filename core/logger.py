from datetime import datetime, timezone, timedelta
import os
import sys
from core.__info__ import LOGS_DIR
from libs.logbook import Logger, StreamHandler, FileHandler


class TimeStr:
    fmt: str = "%Y%m%d_%H-%M-%S"

    @classmethod
    def utc(cls) -> str:
        """Return the current UTC timestamp as a formatted string"""
        now_utc = datetime.now(timezone.utc)
        return now_utc.strftime(cls.fmt)

    @classmethod
    def local(cls, tz: timezone = None) -> str:
        """
        Return the current timestamp as a formatted string in the given timezone.
        If tz is None, uses the system’s local timezone.
        """
        now_utc = datetime.now(timezone.utc)
        target = now_utc.astimezone(tz) if tz else now_utc.astimezone()
        return target.strftime(cls.fmt)

    @classmethod
    def fixed_offset(cls, hours: int, minutes: int = 0, name: str = None) -> str:
        """
        Return the current time as a formatted stringin a fixed-offset
        timezone (e.g. UTC+5:30).
        """
        now_utc = datetime.now(timezone.utc)
        tz = timezone(timedelta(hours=hours, minutes=minutes), name=name)
        return now_utc.astimezone(tz).strftime(cls.fmt)


def init_logger(log_name: str, log_level: str, log_to_file: bool = False) -> Logger:
    """Create a logger instance with the necessary handlers"""
    format_string = '[{record.time:%Y-%m-%d %H:%M:%S.%f}] {record.level_name:<8} : [{record.func_name}] {record.message}'
    logger = Logger(log_name)
    
    # If the log file option is enabled, create a FileHandler instance
    if log_to_file:
        os.makedirs(LOGS_DIR, exist_ok=True)
        filehandler = FileHandler(
                f"{LOGS_DIR}/{TimeStr.local()}_applog_{log_name}.txt",
                level=log_level,
                bubble=True,
                format_string=format_string
        )
        logger.handlers.append(filehandler)

    # If the script is attached to a terminal, create a StreamHandler instance
    if sys.stdout:
        streamhandler = StreamHandler(
            sys.stdout,
            level=log_level,
            bubble=True,
            format_string=format_string
        )
        logger.handlers.append(streamhandler)
    return logger