"""Shim wrapper for `scripts/dev/show_auth_state.py`.

This file exists for backward compatibility. The real implementation lives
under `scripts/dev/`. Running this file will execute the developer helper.

Example:
  .venv/bin/python scripts/show_auth_state.py --state auth_state.json --url https://x.com
"""
import os
import runpy
import sys


def main() -> None:
    HERE = os.path.dirname(__file__)
    TARGET = os.path.join(HERE, "dev", "show_auth_state.py")

    if not os.path.exists(TARGET):
        print(f"Expected dev script not found: {TARGET}")
        sys.exit(2)

    # Delegate entirely to the dev helper so we keep a single implementation
    runpy.run_path(TARGET, run_name="__main__")


if __name__ == "__main__":
    main()

