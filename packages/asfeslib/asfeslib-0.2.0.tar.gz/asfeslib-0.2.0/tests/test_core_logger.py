import io
import sys
from asfeslib.core.logger import Logger

def test_logger_basic(capsys):
    log = Logger(name="pytest-test")
    log.info("Test info")
    log.debug("Test debug")
    log.error("Test error")

    captured = capsys.readouterr()
    output = captured.err or captured.out

    assert "Test info" in output
    assert "Test error" in output
    assert "[INFO]" in output
