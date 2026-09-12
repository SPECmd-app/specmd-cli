"""`specmd help` (ICD-CLI section 8.12, HELP-001..008).

Reads the same static command_metadata.py registry `capabilities` reads
(ICD-HELP-002) and never touches a Specification Set, the network, or a
Cognitive Provider (ICD-HELP-003, HELP-005).
"""

from __future__ import annotations

from specmd import exit_codes
from specmd.command_metadata import COMMANDS, find
from specmd.envelope import build_envelope


class UnknownTopic(Exception):
    def __init__(self, topic: str, suggestions: list[str]):
        super().__init__(f"unknown help topic '{topic}'")
        self.topic = topic
        self.suggestions = suggestions


def _safety_markers(c) -> list[str]:
    markers = []
    markers.append("read-only" if c.read_only else "writes")
    if c.network:
        markers.append("network")
    if c.executes_code:
        markers.append("executes-code")
    if not c.available:
        markers.append("unavailable")
    return markers


def _command_to_dict(c) -> dict:
    return {
        "name": c.name,
        "summary": c.summary,
        "available": c.available,
        "unavailable_reason": c.unavailable_reason or None,
        "safety": _safety_markers(c),
        "exit_statuses": c.exit_statuses,
        "options": [{"name": o.name, "default": o.default, "description": o.description} for o in c.options],
    }


def run(*, topic: str | None, search: str | None, show_all: bool) -> tuple[dict, int]:
    universe = list(COMMANDS) if show_all else [c for c in COMMANDS if c.available]

    if search:
        needle = search.lower()

        def matches(c) -> bool:
            haystack = " ".join([c.name, c.summary] + [o.name + o.description for o in c.options]).lower()
            return needle in haystack

        universe = [c for c in universe if matches(c)]

    if topic is None:
        results = {"topics": [_command_to_dict(c) for c in universe]}
        exit_code = exit_codes.SUCCESS
        status = "succeeded"
    else:
        match = find(topic)
        if match is None or (not show_all and not match.available):
            available_names = sorted(c.name for c in COMMANDS if show_all or c.available)
            suggestions = [n for n in available_names if topic.lower() in n.lower()] or available_names
            results = {"unknown_topic": topic, "suggestions": suggestions}
            exit_code = exit_codes.USAGE_ERROR
            status = "failed"
        else:
            results = {"topic": _command_to_dict(match)}
            exit_code = exit_codes.SUCCESS
            status = "succeeded"

    envelope = build_envelope(
        command="help",
        status=status,
        inputs={"topic": topic, "search": search, "all": show_all},
        results=results,
        findings=[],
        writes=[],
        cognitive_requested="off",
        cognitive_used="none",
        cognitive_complete=True,
    )
    return envelope, exit_code
