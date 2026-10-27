"""Write or check the files every UXPLIMA repository keeps identical to this one.

    python tools/sync.py --write <repo-root>
    python tools/sync.py --check <repo-root>

`--check` prints each drifted path and exits 1 when any file differs or is missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parent.parent

# Canonical path in this repository -> path in a synced repository.
SHARED: dict[str, str] = {
    "docs/internals/uxm-conventions.md": "docs/internals/uxm-conventions.md",
    "shared/.editorconfig": ".editorconfig",
    "shared/.gitattributes": ".gitattributes",
}


def write(target: Path) -> None:
    for source, destination in SHARED.items():
        path = target / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((SOURCE_ROOT / source).read_bytes())


def drifted(target: Path) -> list[str]:
    return [
        destination
        for source, destination in SHARED.items()
        if not (target / destination).is_file()
        or (target / destination).read_bytes() != (SOURCE_ROOT / source).read_bytes()
    ]


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] not in ("--write", "--check"):
        print("usage: sync.py --write|--check <repo-root>", file=sys.stderr)
        return 2
    target = Path(argv[1])
    if argv[0] == "--write":
        write(target)
        return 0
    paths = drifted(target)
    for path in paths:
        print(f"{path}: differs from UXPLIMA/.github")
    return 1 if paths else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
