#!/usr/bin/env python3
"""
Fix bare URLs (markdownlint MD034) in Markdown files by wrapping them in angle brackets.

Rules:
- Skip fenced code blocks (```) and inline code segments (`code`).
- Do not modify URLs already inside angle brackets <...> or Markdown links [text](url).

Usage:
  python scripts/fix_md_bare_urls.py [root_dir]

If root_dir is not provided, the script uses the repository root (current working directory).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


URL_PATTERN = re.compile(r"https?://[^\s<>()\[\]{}]+")


def wrap_bare_urls_in_segment(segment: str) -> str:
    """Wrap bare URLs in a text segment that is known to be outside inline code.

    Skips URLs that are already part of a Markdown link ([...](...)) or enclosed in <...>.
    """

    def replacer(match: re.Match[str]) -> str:
        url = match.group(0)
        start = match.start()
        end = match.end()

        # Check char before/after within the segment
        before = segment[start - 1] if start - 1 >= 0 else ""
        after = segment[end] if end < len(segment) else ""

        # Already enclosed in angle brackets
        if before == "<" and after == ">":
            return url

        # If inside a markdown link target: [text](url)
        # Heuristic: immediately preceded by '(' and not preceded by '<'
        if before == "(":
            return url

        # Otherwise, wrap
        return f"<{url}>"

    return URL_PATTERN.sub(replacer, segment)


def fix_line_outside_inline_code(line: str) -> str:
    """Process a single line, preserving inline code (`...`)."""
    if "`" not in line:
        return wrap_bare_urls_in_segment(line)

    out: list[str] = []
    in_code = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "`":
            # Toggle inline code; copy the backtick
            in_code = not in_code
            out.append(ch)
            i += 1
            continue
        if in_code:
            out.append(ch)
            i += 1
            continue

        # Collect until next backtick or end
        j = i
        while j < len(line) and line[j] != "`":
            j += 1
        segment = line[i:j]
        out.append(wrap_bare_urls_in_segment(segment))
        i = j

    return "".join(out)


def fix_markdown_text(text: str) -> str:
    lines = text.splitlines(keepends=False)
    fixed_lines: list[str] = []
    in_fence = False
    fence_marker = None

    fence_re = re.compile(r"^\s*(```+|~~~+)")

    for line in lines:
        if fence_re.match(line):
            # Toggle fence state when encountering a fence marker at line start
            marker = fence_re.match(line).group(1)  # type: ignore[assignment]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            else:
                # Only close if matching fence marker type (``` vs ~~~)
                if fence_marker and fence_marker[0] == marker[0]:
                    in_fence = False
                    fence_marker = None
            fixed_lines.append(line)
            continue

        if in_fence:
            fixed_lines.append(line)
            continue

        fixed_lines.append(fix_line_outside_inline_code(line))

    return "\n".join(fixed_lines) + ("\n" if text.endswith("\n") else "")


def iter_markdown_files(root: Path):
    ignore_dirs = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fname in filenames:
            if fname.lower().endswith(".md"):
                yield Path(dirpath) / fname


def main():
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    changed = 0
    scanned = 0

    paths: list[Path] = []
    if target.is_file():
        if target.suffix.lower() != ".md":
            print(f"Skipping non-Markdown file: {target}")
            return
        paths = [target]
    else:
        paths = list(iter_markdown_files(target))

    for path in paths:
        scanned += 1
        original = path.read_text(encoding="utf-8")
        fixed = fix_markdown_text(original)
        if fixed != original:
            path.write_text(fixed, encoding="utf-8")
            changed += 1
            print(f"Fixed MD034 bare URLs: {path}")

    print(f"Scanned {scanned} Markdown files, updated {changed}.")


if __name__ == "__main__":
    main()
