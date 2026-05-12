#!/usr/bin/env python3
"""
Runtime environment helpers for source and frozen modes.
"""

from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    """Return True when running from a PyInstaller frozen executable."""
    return bool(getattr(sys, "frozen", False))


def get_app_base_dir() -> Path:
    """
    Return app base directory.

    Source mode: repository root.
    Frozen mode: directory containing current executable.
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def ensure_app_cwd() -> None:
    """In frozen mode, switch cwd to app base dir."""
    if is_frozen():
        base_dir = get_app_base_dir()
        if base_dir.is_dir():
            try:
                Path.cwd()
                # chdir only in frozen mode to make relative paths deterministic.
                import os

                os.chdir(base_dir)
            except OSError:
                pass


def get_runner_executable() -> Path:
    """Return path to frozen module runner executable."""
    return get_app_base_dir() / "GPTCourseKnowledgeRunner.exe"


def build_module_command(module_name: str, *args: str) -> list[str]:
    """
    Build subprocess command for running an internal module.

    Source mode:
      [sys.executable, "-m", module_name, *args]
    Frozen mode:
      [GPTCourseKnowledgeRunner.exe, module_name, *args]
    """
    if is_frozen():
        runner = get_runner_executable()
        return [str(runner), module_name, *args]
    return [sys.executable, "-m", module_name, *args]
