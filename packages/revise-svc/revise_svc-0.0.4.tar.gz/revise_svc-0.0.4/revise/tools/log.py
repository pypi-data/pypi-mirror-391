import logging
import threading
from typing import Optional


class Logger:
    _instance = None
    _lock = threading.Lock()  # Ensure thread safety

    def __new__(cls, *args, **kwargs):
        # Double-checked locking
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Logger, cls).__new__(cls)
                    cls._instance._init_logger(*args, **kwargs)
        return cls._instance

    def _init_logger(self, name='GlobalLogger', log_file='app.log', level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # If handler already exists, don't add duplicate
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Console output
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # File output
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger


def ensure_logger(logger: Optional[logging.Logger] = None) -> logging.Logger:
    """
    Return the provided logger or fall back to the global singleton.

    This helper avoids scattering `if logger is None` checks throughout the
    codebase and ensures logging always has a valid sink.
    """
    if logger is not None:
        return logger
    return Logger().get_logger()
