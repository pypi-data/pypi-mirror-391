# tvi-solphit-base

Base utilities for the `tvi.solphit` namespace. This first release provides an environment-driven logging utility that defaults to stdout and can route to a file when configured.

- **Distribution name (PyPI):** `tvi-solphit-base`
- **Import path:** `tvi.solphit.base`
- **Namespace packaging:** PEP 420 implicit namespace (no `__init__.py` in `tvi/` or `tvi/solphit/`)

> **Author:** Tobias Hagenbeek (SolphIT LLC)

---

## Features

- Minimal, reusable **logger** (`SolphitLogger`) with:
  - Standard levels: `DEBUG|INFO|WARNING|ERROR|CRITICAL`
  - Controlled by **environment variables**
  - Defaults to **stdout**; **file** output when configured
  - Idempotent setup (avoids duplicate handlers on repeat calls)

---

## Installation

```bash
pip install tvi-solphit-base
```
> Requires Python >=3.9.

## Quickstart

```python
from tvi.solphit.base import SolphitLogger

log = SolphitLogger.get_logger("tvi.solphit.example")
log.info("Hello, SolphIT!")
```
### Configure the Environment
```bash
# Defaults:
# TVI_SOLPHIT_LOG_LEVEL=INFO
# TVI_SOLPHIT_LOG_DEST=stdout
# TVI_SOLPHIT_LOG_FILE=solphit.log
# TVI_SOLPHIT_LOG_FORMAT="%(asctime)s | %(levelname)s | %(name)s | %(message)s"

export TVI_SOLPHIT_LOG_LEVEL=DEBUG
export TVI_SOLPHIT_LOG_DEST=file
export TVI_SOLPHIT_LOG_FILE=/var/log/solphit/base.log
python your_script.py
```
### Override via code
```python
log = SolphitLogger.get_logger(
    "tvi.solphit.example",
    level="WARNING",
    dest="file",
    file_path="local.log",
    fmt="%(levelname)s | %(message)s"
)
```

## Versioning

This project uses Semantic Versioning. See the CHANGELOG.