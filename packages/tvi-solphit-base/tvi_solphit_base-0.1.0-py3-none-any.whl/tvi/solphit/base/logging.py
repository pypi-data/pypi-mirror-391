from __future__ import annotations

import logging
import os
import sys
from typing import Optional

_VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

_DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_ENV_LEVEL = "TVI_SOLPHIT_LOG_LEVEL"
_ENV_DEST = "TVI_SOLPHIT_LOG_DEST"
_ENV_FILE = "TVI_SOLPHIT_LOG_FILE"
_ENV_FMT = "TVI_SOLPHIT_LOG_FORMAT"

class SolphitLogger:
    """
    A simple env-configurable logger with stdout or file destination.

    Priority order for configuration:
      1) kwargs provided to get_logger()
      2) environment variables
      3) built-in defaults
    """

    @staticmethod
    def _resolve_level(level: Optional[str]) -> int:
        # normalize and validate
        if level is None:
            level = os.getenv(_ENV_LEVEL, "INFO")
        level = str(level).upper()
        if level not in _VALID_LEVELS:
            level = "INFO"
        return getattr(logging, level)

    @staticmethod
    def _resolve_dest(dest: Optional[str]) -> str:
        if dest is None:
            dest = os.getenv(_ENV_DEST, "stdout")
        dest = dest.lower()
        return "file" if dest == "file" else "stdout"

    @staticmethod
    def _resolve_format(fmt: Optional[str]) -> str:
        if fmt is None:
            fmt = os.getenv(_ENV_FMT, _DEFAULT_FORMAT)
        return fmt

    @staticmethod
    def _resolve_file(file_path: Optional[str]) -> Optional[str]:
        if file_path is None:
            file_path = os.getenv(_ENV_FILE, "solphit.log")
        return file_path

    @classmethod
    def get_logger(
        cls,
        name: str = "tvi.solphit",
        *,
        level: Optional[str] = None,
        dest: Optional[str] = None,
        file_path: Optional[str] = None,
        fmt: Optional[str] = None,
        propagate: bool = False,
    ) -> logging.Logger:
        """
        Get or configure a logger. This is idempotent per logger name.
        """
        logger = logging.getLogger(name)
        logger.setLevel(cls._resolve_level(level))
        logger.propagate = propagate

        # Avoid adding duplicate handlers on repeated calls
        if logger.handlers:
            return logger

        dest_resolved = cls._resolve_dest(dest)
        fmt_resolved = cls._resolve_format(fmt)
        formatter = logging.Formatter(fmt_resolved)

        if dest_resolved == "file":
            file_name = cls._resolve_file(file_path)
            fh = logging.FileHandler(file_name, encoding="utf-8")
            fh.setLevel(logger.level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        else:
            sh = logging.StreamHandler(stream=sys.stdout)
            sh.setLevel(logger.level)
            sh.setFormatter(formatter)
            logger.addHandler(sh)

        return logger
