import os
import logging
from tvi.solphit.base import SolphitLogger

def test_default_stdout_logger(monkeypatch):
    monkeypatch.delenv("TVI_SOLPHIT_LOG_LEVEL", raising=False)
    monkeypatch.delenv("TVI_SOLPHIT_LOG_DEST", raising=False)

    logger = SolphitLogger.get_logger("tvi.solphit.test.default")
    assert logger.level == logging.INFO
    assert any(h.__class__.__name__ == "StreamHandler" for h in logger.handlers)

def test_file_logger(monkeypatch, tmp_path):
    monkeypatch.setenv("TVI_SOLPHIT_LOG_DEST", "file")
    monkeypatch.setenv("TVI_SOLPHIT_LOG_FILE", str(tmp_path / "test.log"))
    monkeypatch.setenv("TVI_SOLPHIT_LOG_LEVEL", "ERROR")

    logger = SolphitLogger.get_logger("tvi.solphit.test.file")
    logger.error("write to file")
    logger.handlers[0].flush()

    log_file = tmp_path / "test.log"
    assert log_file.exists()
