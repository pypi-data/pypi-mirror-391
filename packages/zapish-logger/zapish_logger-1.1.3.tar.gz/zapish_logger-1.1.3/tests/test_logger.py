import os
import pytest
from zapish_logger import (
    file_logger,
    read_log_file,
    console_logger,
    file_and_console_logger,
    custom_logger,
    LoggingConfig,
)


def test_file_logger(tmp_path):
    d = tmp_path / "logs"
    d.mkdir()
    path = os.path.join(str(d), "unit-test.log")
    logger = file_logger(path=path, name="unit-test")
    logger.warning("one")
    logger.error("two")
    logger.info("three")
    logger.debug("four")
    logger.critical("five")


def test_read_log_file(log_data_path):
    data = read_log_file(log_data_path)
    assert len(data) == 4


def test_console_logger():
    logger = console_logger("unit-test")
    logger.warning("one")
    logger.error("two")
    logger.info("three")
    logger.debug("four")
    logger.critical("five")


def test_file_and_console_logger(tmp_path):
    d = tmp_path / "logs"
    d.mkdir()
    path = os.path.join(str(d), "unit-test.log")
    logger = file_and_console_logger(path=path, name="unit-test")
    logger.warning("one")
    logger.error("two")
    logger.info("three")
    logger.debug("four")
    logger.critical("five")


def test_custom_logger(tmp_path):
    d = tmp_path / "logs"
    d.mkdir()
    path = os.path.join(str(d), "unit-test.log")

    more_formats = {
        "moo": "MOO: %(name)s %(asctime)s - %(levelname)s - %(message)s",
    }

    logging_config = LoggingConfig(custom_logging_formatters=more_formats)

    logging_config.add_console_handler(log_format="moo")

    logging_config.add_file_handler(path=path, log_format="clean")

    logger = custom_logger(logging_config=logging_config, name="unit-test")
    logger.warning("one")
    logger.error("two")
    logger.info("three")
    logger.debug("four")
    logger.critical("five")


def test_get_config_bad():
    obj = LoggingConfig()
    with pytest.raises(KeyError):
        obj.get_config()


def test_add_file_handler_bad():
    obj = LoggingConfig()
    with pytest.raises(ValueError):
        obj.add_file_handler(path="some_path", log_format="bad")

    with pytest.raises(ValueError):
        obj.add_file_handler(path="some_path", level="BAD")


def test_add_console_handler_bad():
    obj = LoggingConfig()
    with pytest.raises(ValueError):
        obj.add_console_handler(log_format="bad")


def test_add_rotating_file_handler_bad(tmp_path):
    d = tmp_path / "logs"
    d.mkdir()
    path = os.path.join(str(d), "unit-test.log")
    obj = LoggingConfig()
    with pytest.raises(ValueError):
        obj.add_rotating_file_handler(path=path, log_format="bad")

    with pytest.raises(ValueError):
        obj.add_rotating_file_handler(path=path, level="BAD")

    with pytest.raises(ValueError):
        obj.add_rotating_file_handler(path=path, max_file_size="1Y")

    with pytest.raises(AttributeError):
        obj.add_rotating_file_handler(path=path, max_file_size=100)

    with pytest.raises(ValueError):
        obj.add_rotating_file_handler(path=path, max_file_size="1")

    with pytest.raises(TypeError):
        obj.add_rotating_file_handler(path=path, backup_count="1")
