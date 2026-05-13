#!/usr/bin/env python3
"""
Frozen-compatible module runner.

Usage:
  GPTCourseKnowledgeRunner.exe src.some_module arg1 arg2
"""

from __future__ import annotations

import contextlib
import os
import runpy
import sys


def main() -> None:
    stdout_path = os.environ.get("GPTCKE_STDOUT_FILE")
    stderr_path = os.environ.get("GPTCKE_STDERR_FILE")
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    with contextlib.ExitStack() as stack:
        if stdout_path:
            stdout_file = stack.enter_context(open(stdout_path, "w", encoding="utf-8", errors="replace"))
            sys.stdout = stdout_file
        if stderr_path:
            stderr_file = stack.enter_context(open(stderr_path, "w", encoding="utf-8", errors="replace"))
            sys.stderr = stderr_file

        try:
            _run_main()
        finally:
            try:
                sys.stdout.flush()
            except Exception:
                pass
            try:
                sys.stderr.flush()
            except Exception:
                pass
            sys.stdout = original_stdout
            sys.stderr = original_stderr


def _run_main() -> None:
    if len(sys.argv) < 2:
        print(
            "Error: module name is required.\n"
            "Usage: GPTCourseKnowledgeRunner.exe <module_name> [args...]",
            file=sys.stderr,
        )
        sys.exit(2)

    module_name = sys.argv[1]
    module_args = sys.argv[2:]
    sys.argv = [module_name, *module_args]

    try:
        runpy.run_module(module_name, run_name="__main__")
    except SystemExit as exc:
        code = exc.code
        if isinstance(code, int):
            sys.exit(code)
        if code is None:
            sys.exit(0)
        print(str(code), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: failed to execute module '{module_name}': {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
