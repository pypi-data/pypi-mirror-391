import logging
import colorlog
from pathlib import Path


class Logger:
    def __init__(
        self,
        name: str = "asfeslib",
        log_to_file: bool = False,
        log_file: str = "asfeslib.log"
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        log_format = "%(log_color)s[%(asctime)s] [%(levelname)s]%(reset)s %(message)s"
        formatter = colorlog.ColoredFormatter(
            log_format,
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.log_to_file = log_to_file
        self.log_file = Path(log_file)
        if self.log_to_file:
            self._log_to_file()

    def _log_to_file(self):
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)
