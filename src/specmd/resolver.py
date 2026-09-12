"""Input path resolution (ICD-IN-001..006, CLI-002/003/012/013)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT_SPEC_NAME = "SPEC.md"


@dataclass
class ResolvedInput:
    path: Path
    was_explicit: bool


class InputResolutionError(Exception):
    pass


def resolve_root_spec(explicit_path: str | None, cwd: Path) -> ResolvedInput:
    # ICD-IN-001: explicit input path always wins.
    if explicit_path:
        path = (cwd / explicit_path).resolve() if not Path(explicit_path).is_absolute() else Path(explicit_path)
        return ResolvedInput(path=path, was_explicit=True)

    # ICD-IN-002: default is SPEC.md under the effective current directory.
    default_path = cwd / DEFAULT_ROOT_SPEC_NAME
    if not default_path.exists():
        # ICD-IN-003/004: fail rather than guess among other Markdown files.
        raise InputResolutionError(
            f"no input path was supplied and '{DEFAULT_ROOT_SPEC_NAME}' does not exist in "
            f"{cwd}; pass an explicit Root Specification path"
        )
    return ResolvedInput(path=default_path, was_explicit=False)


def display_path(path: Path, cwd: Path) -> str:
    # ICD-IN-006: report unambiguously, relative to effective cwd when unique.
    try:
        return str(path.relative_to(cwd))
    except ValueError:
        return str(path)
