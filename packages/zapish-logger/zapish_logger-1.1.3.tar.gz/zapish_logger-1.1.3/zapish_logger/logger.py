"""
The JSON logger
"""

from typing import List, Dict, Optional
import json
import logging
import logging.config
import sys
import re


SCHEMA = '{"level": "%(levelname)s", "ts": "%(asctime)s", "caller": "%(name)s", "msg": "%(message)s"}'


class _ExcludeErrorsFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Callback class to exclude ERROR level records"""

    def filter(self, record: logging.LogRecord) -> bool:
        """filter ERROR level records

        :type record: logging.LogRecord
        :param record: The record to check for level

        :rtype: Boolean
        :returns: True if record is less than ERROR False if it is not
        """
        return record.levelno < logging.ERROR


class LoggingConfig:
    """Class to build a dictionary logging config

    :type log_format: str = 'json'
    :param log_format: Set the default log format
    :type custom_logging_formatters: Optional[Dict[str, str]] = None
    :param custom_logging_formatters: Logging formatters example: {'the_name': 'the format'}

    :rtype: None
    :returns: Nothing
    """

    FORMAT_OPTIONS = {
        "json": {
            "json": {
                "format": '{"level": "%(levelname)s", "ts": "%(asctime)s", "caller": "%(name)s", "msg": "%(message)s"}'
            }
        },
        "simple": {"simple": {"format": "%(asctime)s: %(name)s - %(levelname)s - %(message)s"}},
        "clean": {"clean": {"format": "[%(asctime)s] %(levelname)s:%(name)s - %(message)s"}},
    }

    LEVEL_OPTIONS = (
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
        "NOTSET",
    )

    FILE_SIZE_OPTIONS = {
        "B": 1,
        "K": 1000,
        "M": 1000000,
        "G": 1000000000,
    }

    def __init__(self, log_format: str = "json", custom_logging_formatters: Optional[Dict[str, str]] = None) -> None:
        if custom_logging_formatters:
            self.__add_formatters(logging_formatters=custom_logging_formatters)

        all_formatters = {}
        for value in self.FORMAT_OPTIONS.values():
            all_formatters.update(value)

        self._config = {
            "version": 1,
            "filters": {"exclude_errors": {"()": _ExcludeErrorsFilter}},
            "formatters": all_formatters,
            "handlers": {},
            "root": {"level": "NOTSET", "handlers": []},
            "disable_existing_loggers": False,
        }

        self._formatter_option = self._log_format(name=log_format)

    def _log_format(self, name: str = "json") -> str:
        """Protected method to validate and set the log format

        :type name: str = 'json'
        :param name: The format name

        :rtype: String
        :returns: The format name

        :raises ValueError: If name is not a valid format
        """
        if not self.FORMAT_OPTIONS.get(name):
            raise ValueError(f'"{name}" is not a log format option.  the options are "{self.FORMAT_OPTIONS.keys()}"')

        return name

    @classmethod
    def __add_formatters(cls, logging_formatters: Dict[str, str]) -> None:
        """Protected method to add custom formatters

        :type logging_formatters: Dict[str, str]
        :param logging_formatters: A formatter example: {'the_name': 'the format'}

        :rtype: None
        :returns: Nothing it adds fomatters
        """
        for name, logging_format in logging_formatters.items():
            cls.FORMAT_OPTIONS[name] = {f"{name}": {"format": logging_format}}

    def add_console_handler(self, log_format: Optional[str] = None) -> None:
        """Add a console logger

        :type log_format: Optional[str] = None
        :param log_format: To override the instantiated log_format

        :rtype: None
        :returns: Nothing it adds a console logger

        :raises ValueError: If log_format is not a valid format
        """
        if log_format:
            formatter = self._log_format(name=log_format)

        else:
            formatter = self._formatter_option

        stderr_handler = {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": formatter,
            "stream": sys.stderr,
        }
        stdout_handler = {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": formatter,
            "filters": ["exclude_errors"],
            "stream": sys.stdout,
        }

        self._config["handlers"]["console_stderr"] = stderr_handler  # type: ignore[index]
        self._config["root"]["handlers"].append("console_stderr")  # type: ignore[index]
        self._config["handlers"]["console_stdout"] = stdout_handler  # type: ignore[index]
        self._config["root"]["handlers"].append("console_stdout")  # type: ignore[index]

    def add_rotating_file_handler(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        path: str,
        level: str = "INFO",
        log_format: Optional[str] = None,
        max_file_size: str = "5M",
        backup_count: int = 3,
    ) -> None:
        """Add a rotating file logger

        :type path: String
        :param path: The full path to the log file Example: /tmp/some_log.log
        :type level: str = 'INFO'
        :param level: To set the logging level
        :type log_format: Optional[str] = None
        :param log_format: To override the instantiated log_format
        :type max_file_size: max_file_size: str = '5M'
        :param max_file_size: Maximum file size before rotation
        :type backup_count: backup_count: int = 3
        :param backup_count: The number of backup files to keep

        :rtype: None
        :returns: Nothing it adds a file logger

        :raises ValueError: If level is not a valid option
        :raises ValueError: If log_format is not a valid format
        :raises ValueError: If max_file_size is not formatted properly
        :raises TypeError: If backup_count is not an integer
        """
        max_file_size_regex = re.compile(r"^[1-9]\d*(B|K|M|G)$")

        if log_format:
            formatter = self._log_format(name=log_format)

        else:
            formatter = self._formatter_option

        if level not in self.LEVEL_OPTIONS:
            raise ValueError(f'"{level}" is not a valid logging level.  the valid levels are "{self.LEVEL_OPTIONS}"')

        if not max_file_size_regex.match(max_file_size.upper()):
            raise ValueError(
                f'"{max_file_size_regex}" is not a valid file size. it should be a number with 1 '
                f"of the following B, K, M, G example: 1b, 20B, 5K, 15k"
            )

        if not isinstance(backup_count, int):
            raise TypeError("backup count must be an integer.")

        max_file_size_int = int(max_file_size[:-1])
        max_file_size_opt = max_file_size[-1:].upper()

        handler = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": formatter,
            "filename": path,
            "encoding": "utf8",
            "maxBytes": max_file_size_int * self.FILE_SIZE_OPTIONS[max_file_size_opt],
            "backupCount": backup_count,
        }

        self._config["handlers"]["file"] = handler  # type: ignore[index]
        self._config["root"]["handlers"].append("file")  # type: ignore[index]

    def add_file_handler(self, path: str, level: str = "INFO", log_format: Optional[str] = None) -> None:
        """Add a file logger

        :type path: String
        :param path: The full path to the log file Example: /tmp/some_log.log
        :type level: Optional[str] = 'INFO'
        :param level: To set the logging level
        :type log_format: Optional[str] = None
        :param log_format: To override the instantiated log_format

        :rtype: None
        :returns: Nothing it adds a file logger

        :raises ValueError: If level is not a valid option
        :raises ValueError: If log_format is not a valid format
        """
        if log_format:
            formatter = self._log_format(name=log_format)

        else:
            formatter = self._formatter_option

        if level not in self.LEVEL_OPTIONS:
            raise ValueError(f'"{level}" is not a valid logging level.  the valid levels are "{self.LEVEL_OPTIONS}"')

        handler = {
            "class": "logging.FileHandler",
            "level": level,
            "formatter": formatter,
            "filename": path,
            "encoding": "utf8",
        }

        self._config["handlers"]["file"] = handler  # type: ignore[index]
        self._config["root"]["handlers"].append("file")  # type: ignore[index]

    def _validate_handlers(self) -> None:
        """Validate if a handler has been added

        :rtype: None
        :returns: Nothing it validates

        :raises KeyError: If handlers don't exist
        """
        if not self._config["handlers"]:
            raise KeyError("no handlers have been added!")

        if not self._config["root"]["handlers"]:  # type: ignore[index]
            raise KeyError("no handlers have been added!")

    def get_config(self) -> dict:
        """Get the configuration

        :rtype: Dict
        :returns: A logging configuration
        """
        self._validate_handlers()
        return self._config


def file_logger(path: str, name: str, level: str = "INFO", log_format: str = "json") -> logging.Logger:
    """Function to get a file logger

    :type path: String
    :param path: The full path to the log file Example: /tmp/some_log.log
    :type level: str = 'INFO'
    :param level: To set the logging level
    :type name: String
    :param name: The name of the logger
    :type log_format: str = 'json'
    :param log_format: Set the log format

    :rtype: logging.Logger
    :returns: The logger
    """
    logging_config = LoggingConfig(log_format=log_format)
    logging_config.add_rotating_file_handler(path=path, level=level)
    logging.config.dictConfig(logging_config.get_config())
    this_logger = logging.getLogger(name)
    return this_logger


def console_logger(name: str, log_format: str = "json") -> logging.Logger:
    """Function to get a console logger

    :type name: String
    :param name: The name of the logger
    :type log_format: str = 'json'
    :param log_format: Set the log format

    :rtype: logging.Logger
    :returns: The logger
    """
    logging_config = LoggingConfig(log_format=log_format)
    logging_config.add_console_handler()
    logging.config.dictConfig(logging_config.get_config())
    this_logger = logging.getLogger(name)
    return this_logger


def file_and_console_logger(path: str, name: str, level: str = "INFO", log_format: str = "json") -> logging.Logger:
    """Function to get a rotating file and console logger

    :type path: String
    :param path: The full path to the log file Example: /tmp/some_log.log
    :type level: str = 'INFO'
    :param level: To set the logging level
    :type name: String
    :param name: The name of the logger
    :type log_format: str = 'json'
    :param log_format: Set the log format

    :rtype: logging.Logger
    :returns: The logger
    """
    logging_config = LoggingConfig(log_format=log_format)
    logging_config.add_rotating_file_handler(path=path, level=level)
    logging_config.add_console_handler()
    logging.config.dictConfig(logging_config.get_config())
    this_logger = logging.getLogger(name)
    return this_logger


def custom_logger(logging_config: LoggingConfig, name: str) -> logging.Logger:
    """Function to get a custom logger

    :type logging_config: zapish_logger.LoggingConfig
    :param logging_config: The logging config
    :type name: String
    :param name: The name of the logger

    :rtype: logging.Logger
    :returns: The logger
    """
    logging.config.dictConfig(logging_config.get_config())
    this_logger = logging.getLogger(name)
    return this_logger


def process_log_file(data: str) -> List[Dict[str, str]]:
    """Function that converts log entries to dicts and appends to list, also handles non-json log entries
    the key will be 'msg' if the log entry is not json

    :type data: String
    :param data: The log data

    :rtype: List[Dict[str, str]]
    :returns: Te log data as python objects
    """
    final_data = []
    data_split = data.splitlines()
    for line in data_split:
        try:
            final_data.append(json.loads(line))

        except json.JSONDecodeError:
            final_data.append({"msg": line})

    return final_data


def read_log_file(path: str) -> List[Dict[str, str]]:
    """Function that reads log data and converts log entries to dicts and appends to list

    :type path: String
    :param path: The full path to the log file Example: /tmp/some_log.log

    :rtype: List[Dict[str, str]]
    :returns: Te log data as python objects
    """

    with open(path, "r", encoding="utf-8") as file:
        log_file = file.read()

    return process_log_file(log_file)
