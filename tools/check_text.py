"""Check a repository's documentation files and text against the repository standard.

    python tools/check_text.py <repo-root>

Prints one `path:line: rule: detail` line per finding and exits 1 when there is any.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

SKIPPED_DIRS = {".git", "vendor", "build", ".gradle", "node_modules", "run", ".idea"}
# profile/README.md is where GitHub reads an organization profile from.
ROOT_MARKDOWN = {"README.md", "AGENTS.md", "CLAUDE.md", "CHANGELOG.md", "profile/README.md"}
DOC_FOLDERS = ("docs/user/", "docs/internals/", "docs/operations/")
FREE_FOLDERS = (".agents/", ".github/")
# Release tooling writes the changelog; its dates and wording are not ours to check.
UNCHECKED_TEXT = {"CHANGELOG.md"}

COMMENT_SUFFIXES = {
    ".java", ".kt", ".kts", ".gradle", ".py", ".sh", ".yml", ".yaml", ".toml",
    ".properties", ".conf", ".ps1", ".js", ".ts",
}
COMMENT_STARTS = ("//", "#", "*", "/*", "<!--", "--")

EN_DASH, EM_DASH = chr(0x2013), chr(0x2014)
DASH = re.compile(f"[{EN_DASH}{EM_DASH}]")
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
DECISION_ID = re.compile(r"\bADR-\d+\b|\b[DFW]\d{2,}\b")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
# A date inside quotes is an example of a value an operator writes, not a note.
QUOTED = re.compile(r"\"[^\"]*\"|'[^']*'")

AGENTS_MAX_LINES = 200
PAGE_MAX_LINES = 400
SKILL_MAX_LINES = 500


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.detail}"


def check(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _files(root):
        text = _read_text(root / path)
        if text is None:
            continue
        lines = text.replace("\r\n", "\n").split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        if path.endswith(".md"):
            findings += _check_markdown_file(root, path, text, lines)
        if path not in UNCHECKED_TEXT:
            findings += _check_lines(path, lines)
    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: check_text.py <repo-root>", file=sys.stderr)
        return 2
    findings = check(Path(argv[0]))
    for finding in findings:
        print(finding)
    return 1 if findings else 0


def _files(root: Path) -> list[str]:
    tracked = _git_files(root)
    if tracked is None:
        tracked = []
        for directory, subdirs, names in os.walk(root):
            subdirs[:] = sorted(d for d in subdirs if d not in SKIPPED_DIRS)
            for name in names:
                tracked.append(Path(directory, name).relative_to(root).as_posix())
    return sorted(p for p in tracked if not SKIPPED_DIRS.intersection(PurePosixPath(p).parts[:-1]))


def _git_files(root: Path) -> list[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            capture_output=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return [p for p in out.decode("utf-8").split("\0") if p and (root / p).is_file()]


def _read_text(file: Path) -> str | None:
    data = file.read_bytes()
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _markdown_allowed(path: str) -> bool:
    name = PurePosixPath(path).name
    if path in ROOT_MARKDOWN or path == "docs/README.md" or ("/" not in path and name.startswith("LICENSE")):
        return True
    return path.startswith(DOC_FOLDERS) or path.startswith(FREE_FOLDERS)


def _check_markdown_file(root: Path, path: str, text: str, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    if not _markdown_allowed(path):
        findings.append(Finding(path, 1, "files", "documentation file the standard does not allow"))
    if path == "CLAUDE.md" and text.replace("\r\n", "\n").strip() != "@AGENTS.md":
        findings.append(Finding(path, 1, "claude-md", "CLAUDE.md must be exactly @AGENTS.md"))
    limit = _line_limit(path)
    if limit is not None and len(lines) > limit:
        findings.append(Finding(path, len(lines), "length", f"{len(lines)} lines, limit {limit}"))
    if path not in UNCHECKED_TEXT:
        findings += _check_links(root, path, lines)
    return findings


def _line_limit(path: str) -> int | None:
    if path == "AGENTS.md":
        return AGENTS_MAX_LINES
    if PurePosixPath(path).name == "SKILL.md":
        return SKILL_MAX_LINES
    if path == "CLAUDE.md" or path.startswith(".github/"):
        return None
    return PAGE_MAX_LINES


def _check_links(root: Path, path: str, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    base = (root / path).parent
    for number, line in _prose_lines(lines):
        for target in LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local = target.split("#", 1)[0]
            if local and not (base / local).exists():
                findings.append(Finding(path, number, "link", f"{target} does not exist"))
    return findings


def _check_lines(path: str, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in enumerate(lines, start=1):
        if DASH.search(line):
            findings.append(Finding(path, number, "dash", "em or en dash; use a colon, comma or full stop"))
    for number, line in _commentary_lines(path, lines):
        if DATE.search(QUOTED.sub("", line)):
            findings.append(Finding(path, number, "date", "a date in documentation or a comment; git keeps history"))
        for match in DECISION_ID.finditer(line):
            findings.append(Finding(path, number, "decision-id", f"{match.group(0)}: write the reasoning, not a record number"))
    return findings


def _commentary_lines(path: str, lines: list[str]) -> list[tuple[int, str]]:
    if path.endswith(".md"):
        return _prose_lines(lines)
    if PurePosixPath(path).suffix not in COMMENT_SUFFIXES:
        return []
    return [(n, line) for n, line in enumerate(lines, start=1) if line.lstrip().startswith(COMMENT_STARTS)]


def _prose_lines(lines: list[str]) -> list[tuple[int, str]]:
    prose: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            prose.append((number, line))
    return prose


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
