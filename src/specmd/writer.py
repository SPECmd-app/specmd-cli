"""Safe, atomic file writing (CLI-010, ICD-OUT-001..006, REL-002)."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WriteResult:
    path: str
    action: str  # "created" | "would_overwrite" | "replaced"
    completed: bool


class WriteRefused(Exception):
    def __init__(self, path: Path):
        super().__init__(
            f"'{path}' already exists and --force was not given; refusing to overwrite"
        )
        self.path = path


def safe_write(path: Path, content: str, *, force: bool, dry_run: bool = False) -> WriteResult:
    existed = path.exists()
    if existed and not force:
        # ICD-OUT-002: without --force, an existing destination stays unchanged.
        raise WriteRefused(path)

    action = "replaced" if existed else "created"
    if dry_run:
        return WriteResult(path=str(path), action=("would_overwrite" if existed else action), completed=False)

    path.parent.mkdir(parents=True, exist_ok=True)
    # ICD-OUT-004: atomic replacement where the environment permits it.
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_name, path)
    except OSError:
        # REL-002: a failed write must not leave the destination partially
        # replaced when atomic replacement is available; the temp file never
        # touched `path`, so the original (or its absence) is preserved.
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise

    return WriteResult(path=str(path), action=action, completed=True)
