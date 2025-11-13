from __future__ import annotations

from pathlib import Path

DIR_GIT = Path(".git")

# filestate: python-constant-sort
FILE_EXTENSION_ENV = "env"
FILE_EXTENSION_PYTHON = "py"
FILE_EXTENSION_YAML = "yml"

# filestate: python-constant-sort
FILE_NAME_ENV = Path(f".{FILE_EXTENSION_ENV}")
FILE_NAME_ENV_YAML = Path(f".{FILE_EXTENSION_ENV}.{FILE_EXTENSION_YAML}")

PATH_NAME_PATH = "path"
