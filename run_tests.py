#!/usr/bin/env python3
"""Simple test runner that prints clear terminal indications and runs pytest.

Usage:
  python run_tests.py [path]

If no path provided, defaults to `scrk3/test`.
"""
import os
import sys
import subprocess

DEFAULT_TARGET = "scrk3/test"


def run_pytest(target: str) -> int:
    print("\n=== Running tests for: {} ===".format(target))
    cmd = [sys.executable, "-m", "pytest", "-q", target]
    try:
        proc = subprocess.run(cmd)
        rc = proc.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user.")
        return 130
    except Exception as e:
        print(f"\nFailed to run pytest: {e}")
        return 2

    if rc == 0:
        print("\n=== All tests passed for: {} ===\n".format(target))
    else:
        print("\n=== Some tests failed for: {} (exit code {}) ===\n".format(target, rc))
    return rc


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET
    # normalize path
    target = os.path.normpath(target)
    exit_code = run_pytest(target)
    sys.exit(exit_code)
