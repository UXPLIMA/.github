"""Check a pull request title against the conventional commit rules of the repository standard.

    python tools/check_title.py "<title>" <scope> [<scope> ...]

Prints each problem and exits 1 when there is any.
"""

from __future__ import annotations

import re
import sys

TYPES = ("feat", "fix", "perf", "refactor", "docs", "test", "build", "ci", "chore")
MAX_LENGTH = 72
TITLE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[a-z0-9-]+)\))?!?: (?P<summary>\S.*)$")


def problems(title: str, scopes: list[str]) -> list[str]:
    match = TITLE.match(title)
    if match is None:
        return ["not 'type(scope): summary'"]
    found: list[str] = []
    if match["type"] not in TYPES:
        found.append(f"unknown type '{match['type']}'")
    allowed = ", ".join(scopes)
    if match["scope"] is None:
        found.append(f"missing scope; use one of: {allowed}")
    elif match["scope"] not in scopes:
        found.append(f"unknown scope '{match['scope']}'; use one of: {allowed}")
    if match["summary"][0].isupper():
        found.append("summary starts with a capital letter")
    if len(title) > MAX_LENGTH:
        found.append(f"{len(title)} characters, limit {MAX_LENGTH}")
    return found


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: check_title.py <title> <scope> [<scope> ...]", file=sys.stderr)
        return 2
    found = problems(argv[0], argv[1:])
    for problem in found:
        print(problem)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
