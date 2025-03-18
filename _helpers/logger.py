import sys
from _helpers.logbook import Logger, StreamHandler, FileHandler

def init_logger(log_name: str, log_level: str, log_to_file: bool = False) -> Logger:
        """Create a logger instance with the necessary handlers"""
        format_string = '[{record.time:%Y-%m-%d %H:%M:%S.%f}] {record.level_name:<8} : [{record.func_name}] {record.message}'
        logger = Logger(log_name)
        # If the log file option is enabled, create a FileHandler instance
        if log_to_file:
            filehandler = FileHandler(
                  f"applog_{log_name}.txt",
                  level=log_level,
                  bubble=True,
                  format_string=format_string
            )
            logger.handlers.append(filehandler)
            logger.info('-' * 80)

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
