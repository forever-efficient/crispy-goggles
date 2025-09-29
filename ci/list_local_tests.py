#!/usr/bin/env python3
"""
List tests marked with @pytest.mark.local so maintainers can see which tests are excluded from CI.

This script is invoked from the CI workflow instead of embedding a Python heredoc which
can confuse some YAML parsers / editors.
"""
import sys
import pytest

def main(argv):
    # Run pytest in collection-only mode and print a short message for visibility.
    # Keep arguments minimal to avoid running tests.
    print('Collected tests (CI excludes tests marked local)')
    # Use pytest's collection to surface tests; we intentionally don't parse the output here.
    # This keeps behavior identical to the previous inline script while avoiding YAML heredocs.
    return pytest.main(['--collect-only', '-q'] + argv)

if __name__ == '__main__':
    rc = main(sys.argv[1:])
    # Ensure exit code is propagated so CI can be aware of collection failures.
    sys.exit(rc)
