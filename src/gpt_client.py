#!/usr/bin/env python3
"""
Minimal OpenAI client wrapper for GPT-based summarization (future use).
Loads configuration from .env and config/openai_settings.json.
Provides a ready-to-use client and settings without making API calls.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# Add src/utils to path for local import
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.utils.env_loader import load_env_file
except ImportError:
    # Fallback for direct module execution
    from utils.env_loader import load_env_file


def load_openai_settings(settings_path: Path = Path("config/openai_settings.json")) -> Dict[str, Any]:
    """
    Load OpenAI settings from a JSON file.

    Parameters
    ----------
    settings_path : Path, optional
        Path to the JSON settings file (default: config/openai_settings.json).

    Returns
    -------
    dict
        The parsed JSON content.

    Raises
    ------
    FileNotFoundError
        If the settings file does not exist.
    json.JSONDecodeError
        If the file is not valid JSON.
    """
    if not settings_path.is_file():
        raise FileNotFoundError(
            f"OpenAI settings file not found: {settings_path}")
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_openai_client_and_settings() -> Tuple[Any, Dict[str, Any]]:
    """
    Load environment variables, settings, and create an OpenAI client.

    Returns
    -------
    tuple (client, settings)
        client : openai.OpenAI instance
        settings : dict with model, temperature, max_output_tokens, etc.

    Raises
    ------
    RuntimeError
        If OPENAI_API_KEY is missing after loading .env.
    """
    # 1. Load .env file (if exists)
    load_env_file()

    # 2. Load settings
    settings = load_openai_settings()

    # 3. Check API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set.\n"
            "Please create a .env file in the project root with:\n"
            "  OPENAI_API_KEY=your_openai_api_key_here\n"
            "Do not commit the .env file to version control."
        )

    # 4. Import openai (only when needed)
    try:
        import openai
    except ImportError:
        raise ImportError(
            "OpenAI package is not installed. Run:\n"
            "  pip install openai"
        )

    # 5. Create client
    client = openai.OpenAI(api_key=api_key)

    return client, settings


def smoke_check() -> None:
    """
    Validate local configuration without making API calls.
    Prints success message or error details.
    """
    try:
        load_env_file()
        settings = load_openai_settings()
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("ERROR: OPENAI_API_KEY is missing.")
            print("  Create a .env file with OPENAI_API_KEY=...")
            print("  See .env.example for reference.")
            sys.exit(1)
        print("OpenAI configuration loaded successfully.")
        print(f"  Model: {settings.get('model', 'unknown')}")
        print(f"  Temperature: {settings.get('temperature', 'unknown')}")
        print(
            f"  Max output tokens: {settings.get('max_output_tokens', 'unknown')}")
        print("  API key: present (not shown)")
    except FileNotFoundError as e:
        print(f"ERROR: Settings file missing: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in settings file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    smoke_check()

