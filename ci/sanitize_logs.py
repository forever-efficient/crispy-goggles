#!/usr/bin/env python3
"""Simple log sanitizer used by CI to redact secrets and truncate large logs.

Usage:
  python ci/sanitize_logs.py input.txt output-sanitized.txt

This script applies a set of regex rules to replace sensitive patterns with
placeholders, then truncates the output to a maximum size.
"""

import re
import sys

RULES = [
    # Authorization headers and bearer tokens
    (
        re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9\-\._~\+\/=]+"),
        "Authorization: [REDACTED]",
    ),
    (re.compile(r"(?i)authorization:\s*[^\s]+"), "Authorization: [REDACTED]"),
    # Common secret patterns like API_KEY=xxx or SECRET: 'xxx'
    (
        re.compile(
            r"(?i)(api[_-]?key|access[_-]?token|secret|password|passwd)[\s'\"]*[:=][\s'\"]*[^\s'\"]+",
        ),
        "\1: [REDACTED]",
    ),
    # Credentials in URLs
    (re.compile(r"https?://[^/@\s]+:[^/@\s]+@"), "https://<redacted>@"),
    # Long hex blobs (likely keys)
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), "[REDACTED_HEX]"),
    # Email addresses
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[redacted-email]"),
    # Home dirs / user paths
    (re.compile(r"/home/[^\s]+"), "/home/<redacted>"),
]

MAX_BYTES = 32_000


def sanitize(text: str) -> str:
    for pat, repl in RULES:
        text = pat.sub(repl, text)
    if len(text.encode("utf-8")) > MAX_BYTES:
        # Truncate safely at character boundary
        encoded = text.encode("utf-8")[:MAX_BYTES]
        text = encoded.decode("utf-8", errors="ignore") + "\n\n...log truncated...\n"
    return text


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: ci/sanitize_logs.py input.txt output-sanitized.txt", file=sys.stderr,
        )
        sys.exit(2)
    inp = sys.argv[1]
    out = sys.argv[2]
    with open(inp, "rb") as f:
        raw = f.read().decode("utf-8", errors="replace")
    sanitized = sanitize(raw)
    with open(out, "w", encoding="utf-8") as f:
        f.write(sanitized)


if __name__ == "__main__":
    main()
