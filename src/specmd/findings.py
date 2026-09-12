"""Finding model shared by validate/inspect/render/trace (ICD-JSON-002/003/004)."""

from __future__ import annotations

from dataclasses import dataclass, field


SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFORMATION = "information"

EVIDENCE_DETERMINISTIC = "deterministic"
EVIDENCE_HEURISTIC = "heuristic"


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    evidence_type: str = EVIDENCE_DETERMINISTIC
    file: str | None = None
    line: int | None = None
    column: int | None = None
    reviewers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "evidence_type": self.evidence_type,
            "message": self.message,
            "reviewers": list(self.reviewers),
            "file": self.file,
            "line": self.line,
            "column": self.column,
        }


def sort_key(finding: Finding):
    # REL-003: deterministic order — file, location, severity, then rule ID.
    severity_rank = {SEVERITY_ERROR: 0, SEVERITY_WARNING: 1, SEVERITY_INFORMATION: 2}
    return (
        finding.file or "",
        finding.line if finding.line is not None else -1,
        finding.column if finding.column is not None else -1,
        severity_rank.get(finding.severity, 3),
        finding.rule_id,
    )


def sorted_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=sort_key)
