#!/usr/bin/env python3
"""
Frozen-compatible module runner.

Usage:
  GPTCourseKnowledgeRunner.exe src.some_module arg1 arg2
"""

from __future__ import annotations

import runpy
import sys


def main() -> None:
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
