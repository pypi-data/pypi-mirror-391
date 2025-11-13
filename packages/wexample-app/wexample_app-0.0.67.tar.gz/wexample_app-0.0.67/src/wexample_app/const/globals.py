from __future__ import annotations

from pathlib import Path

CORE_COMMAND_NAME: str = "wex"
WORKDIR_SETUP_DIR: Path = Path(f".{CORE_COMMAND_NAME}")

# filestate: python-constant-sort
APP_FILE_APP_CONFIG: str = "config.yml"
APP_FILE_APP_MANAGER: Path = Path("app-manager")
APP_FILE_APP_RUNTIME_CONFIG: str = "config.runtime.yml"
APP_PATH_APP_MANAGER: Path = WORKDIR_SETUP_DIR / "python" / "app_manager"
APP_PATH_BIN_APP_MANAGER: Path = WORKDIR_SETUP_DIR / "bin" / APP_FILE_APP_MANAGER

ENV_VAR_NAME_APP_ENV = "APP_ENV"
