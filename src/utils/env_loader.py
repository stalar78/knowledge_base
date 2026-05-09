#!/usr/bin/env python3
"""
Minimal environment file loader.
Reads a .env file and sets environment variables (if not already set).
Uses only the Python standard library.
"""

import os
import sys
from pathlib import Path
from typing import Optional


def load_env_file(env_path: Path = Path(".env")) -> None:
    """
    Load environment variables from a .env file.

    The file is expected to be UTF‑8 encoded, with lines in the format:
        KEY=VALUE
    Empty lines and lines starting with '#' are ignored.
    If a variable is already set in the environment, it is NOT overwritten.

    Parameters
    ----------
    env_path : Path, optional
        Path to the .env file (default: .env in the current working directory).

    Returns
    -------
    None
    """
    if not env_path.is_file():
        # No .env file – nothing to do
        return

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Split at the first '=' (value may contain '=')
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Set only if not already present
                    if key and key not in os.environ:
                        os.environ[key] = value
    except (OSError, UnicodeDecodeError) as e:
        print(f"Warning: could not read {env_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    # Simple test: load .env and print what was loaded
    import json
    load_env_file()
    # Print all environment variables that contain "OPENAI"
    for k, v in os.environ.items():
        if "OPENAI" in k.upper():
            print(f"{k}={v}")
    if not any("OPENAI" in k.upper() for k in os.environ):
        print("No OPENAI_* variables found.")
