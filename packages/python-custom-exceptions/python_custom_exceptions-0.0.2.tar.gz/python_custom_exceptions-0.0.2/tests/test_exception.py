import pytest
from custom_python_logger import build_logger

from python_custom_exceptions import ConnectionException

logger = build_logger(project_name="custom_exceptions_test")


def test_connection_exception():
    with pytest.raises(ConnectionException) as exc_info:
        raise ConnectionException(
            host="Database",
            message="Connection failed",
            diagnostic_info={"host": "db.example.com"},
        )
    logger.info(f"\n{exc_info.value}")  # noqa


def test_connection_exception_without_message():
    with pytest.raises(ConnectionException) as exc_info:
        raise ConnectionException(host="Database", diagnostic_info={"host": "db.example.com"})
    logger.info(f"\n{exc_info.value}")  # noqa
