"""`specmd blackbox` (BBX-001..012).

Structural, mostly-deterministic Black-Box Contract inventory: it reports
what the Specification Set's structure explicitly contains, distinguished
from what a Trace Document says about implementation/evidence status
(BBX-007..010), and never touches an implementation (BBX-012). Two checks
(interface I/O facilitation drafting, requirements<->interface cross-
mapping) are genuinely semantic. `specmd` has no Direct-Provider Mode (no
credentials, no outbound network call anywhere on this path) — instead it
supports Host-Agent Mode (COG-001, SPECMD_CLI_ICD.md section 7.2): the
coding agent already driving `specmd` reads the `cognitive_package` a call
returns, reasons over it in its own context, and supplies structured
findings back via `--cognitive-input`/the `cognitive_input` MCP argument.
Until that input is supplied, `--cognitive auto/required` negotiates
honestly (ICD-COG-001..003) and reports the checks as not yet performed
rather than fabricating a result (BBX-004/005).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from specmd import core_profile, exit_codes, host_agent, human_only, module_resolver, structural, trace_pair, writer
from specmd.cognitive import negotiate
from specmd.envelope import build_envelope
from specmd.findings import EVIDENCE_DETERMINISTIC, EVIDENCE_HEURISTIC, Finding
from specmd.frontmatter import strip_leading_numeral
from specmd.ids import extract_acceptance_entries, extract_requirement_ids

# Sections that, per the Core profile, typically carry
# black-box-relevant content: actors/interfaces/errors/state.
_INTERFACE_SECTION_NAMES = ("Interfaces and External Contracts", "System Model")

_SYSTEM_MODEL_SECTION = "System Model"
_INTERFACES_SECTION = "Interfaces and External Contracts"
_REQUIREMENTS_SECTION = "Requirements"

# Disclosed convention (BBX-004): a top-level bullet under System Model of
# the form "- **Name**: ..." or "- **Name** — ...". Deliberately bold-only —
# an earlier version also matched an unbolded leading phrase up to the first
# ":"/"-"/"—" anywhere in the line, which on real documents both swallowed
# whole prose sentences (a bullet whose only delimiter was a colon buried
# deep in the text) and misfired on ID-prefixed bullets ("- INV-001: ...",
# where the hyphen inside the ID satisfied the delimiter). Bold fencing is
# the only signal precise enough to trust deterministically; mirrors the
# documented column-order convention already used by
# trace_pair.row_evidence_map().
_ACTOR_BULLET_RE = re.compile(r"^-\s+\*\*(?P<name>[^*]{1,80})\*\*\s*[:—]")


def _section_body(doc, name: str, *, direct_only: bool = False) -> str | None:
    """Slice a named heading's body text out of `doc.text` using the already
    -parsed (level, text, line_number) heading list; returns None if the
    heading is absent (its absence is separately flagged by BBX-003).

    By default the body extends through nested subsections (stops only at
    the next heading of equal-or-shallower level), matching how the
    existing interface-section-mention search wants to be inclusive.
    `direct_only=True` stops at the very next heading regardless of level —
    used where scanning into unrelated nested subsections (e.g. an
    Invariants subsection under System Model) would produce false matches.
    """
    lines = doc.text.splitlines()
    for i, (level, text, line_no) in enumerate(doc.headings):
        if strip_leading_numeral(text) != name:
            continue
        end = len(lines)
        for level2, _text2, line_no2 in doc.headings[i + 1 :]:
            if direct_only or level2 <= level:
                end = line_no2 - 1
                break
        return "\n".join(lines[line_no:end])
    return None


def _extract_actor_names(section_text: str) -> list[str]:
    names: list[str] = []
    for line in section_text.splitlines():
        m = _ACTOR_BULLET_RE.match(line.strip())
        if not m:
            continue
        name = m.group("name").strip()
        if name and name not in names:
            names.append(name)
    return names


def _actor_operation_check(doc, root_spec_path: Path) -> tuple[dict[str, bool], list[Finding]]:
    """BBX-002/003: does every bold-labeled bullet term named in System
    Model get at least one mention in Interfaces and External Contracts?
    A structural cross-reference, deterministic and reproducible — but text
    matching alone cannot tell a person/system actor from a data entity
    that happens to use the same bold-bullet convention (that distinction
    needs meaning, not pattern-matching), so findings are reported at
    `information` severity and say so explicitly rather than asserting a
    confident gap.
    """
    system_model_body = _section_body(doc, _SYSTEM_MODEL_SECTION, direct_only=True)
    if system_model_body is None:
        return {}, []
    names = _extract_actor_names(system_model_body)
    if not names:
        return {}, []
    interfaces_body = _section_body(doc, _INTERFACES_SECTION)
    search_text = interfaces_body if interfaces_body is not None else doc.text
    search_text_lower = search_text.lower()

    coverage: dict[str, bool] = {}
    findings: list[Finding] = []
    for name in names:
        present = name.lower() in search_text_lower
        coverage[name] = present
        if not present:
            findings.append(
                Finding(
                    rule_id="BBX-003",
                    severity="information",
                    message=(
                        f"'{name}', a bold-labeled bullet term in '{_SYSTEM_MODEL_SECTION}' (an actor or an "
                        f"entity — text matching alone cannot tell which), has no mention in "
                        f"'{_INTERFACES_SECTION}'; if it names an actor, its operation coverage could not be confirmed"
                    ),
                    evidence_type=EVIDENCE_DETERMINISTIC,
                    file=str(root_spec_path),
                )
            )
    return coverage, findings


def _interface_element_names(doc) -> list[str]:
    """BBX-002: named operations/interactions within Interfaces and External
    Contracts — the *immediate* child headings only (level == section level
    + 1), not every heading at any depth. Deliberately narrowed after
    checking against a real example (SPECmd-app/SPEC.md's Judo Club
    walkthrough, examples/judo-club-specmd-0.4.3.md): its single "Contact
    Communication Interface" subsection is itself broken down into
    "Purpose"/"Data Authority"/"Supported Operation"/etc. sub-subsections —
    collecting any depth reported those as five more bogus "interfaces"
    alongside the one real one. An interface's own name is a direct child of
    the section heading; anything deeper is that interface's internal
    breakdown, not a sibling interface. Headings are still a far more
    reliable signal than free-text pattern matching (see
    _extract_actor_names's docstring for why the bullet-based approach was
    narrowed too); this also gives Host-Agent citations something concrete
    to be checked against.
    """
    names: list[str] = []
    for i, (level, text, _line_no) in enumerate(doc.headings):
        if strip_leading_numeral(text) != _INTERFACES_SECTION:
            continue
        for level2, text2, _line_no2 in doc.headings[i + 1 :]:
            if level2 <= level:
                break
            if level2 == level + 1:
                names.append(strip_leading_numeral(text2))
        break
    return names


def _build_cognitive_package(doc, requirement_ids: list[str], interface_elements: list[str]) -> dict:
    """The bounded material a Host-Agent needs for the two semantic checks
    (BBX-004/005) — never the whole repository (CTX-001/004). Human-only
    content is stripped (CTX-003/PROV-004) with the same
    human_only.strip_human_only() render.py already uses. Normative Module
    content is out of scope for this build; the omission is disclosed
    in-band (CTX-005) rather than silently dropped.
    """

    def _stripped(name: str) -> str:
        body = _section_body(doc, name)
        return human_only.strip_human_only(body) if body is not None else ""

    return {
        "analysis_goal": (
            "Reconstruct the expected input -> behavior -> output path for each interface using only the "
            "supplied material. Identify gaps or contradictions. Do not invent missing behavior."
        ),
        "material": {
            "interfaces_and_external_contracts": _stripped(_INTERFACES_SECTION),
            "system_model": _stripped(_SYSTEM_MODEL_SECTION),
            "requirements": _stripped(_REQUIREMENTS_SECTION),
        },
        "known_requirement_ids": requirement_ids,
        "known_interface_elements": interface_elements,
        "response_contract": {
            "interfaces": [
                {
                    "interface": "<one of known_interface_elements, or a name identified from the material>",
                    "input_contract": ["..."],
                    "output_contract": ["..."],
                    "supporting_requirement_ids": ["<must be one of known_requirement_ids>"],
                    "gaps": ["..."],
                    "confidence": "low|medium|high",
                }
            ],
            "requirements_interface_cross_mapping": {
                "unmatched_requirements": ["<must be one of known_requirement_ids>"],
                "unmatched_interface_elements": ["..."],
            },
        },
        "context_omitted": ["Normative Module content is not included in this build's package (root spec only)."],
    }


def run(
    *,
    root_spec_path: Path,
    set_root: Path,
    display_path: str,
    trace_mode: str,
    cognitive_mode: str,
    cognitive_input: dict | None = None,
    export_path: Path | None,
) -> tuple[dict, int]:
    report = structural.analyze(root_spec_path, "auto")
    findings = list(report.findings)

    cog = negotiate(cognitive_mode)
    if cognitive_input is not None and cog.requested == "off":
        raise host_agent.HostAgentInputError(
            "--cognitive-input is invalid when --cognitive is 'off'; nothing would use it"
        )

    version_finding = structural.version_alignment_finding(report, str(root_spec_path))
    if version_finding is not None:
        findings.append(version_finding)

    module_res = module_resolver.resolve_modules(root_spec_path, set_root)
    all_texts = [root_spec_path.read_text(encoding="utf-8")]
    for m in module_res.modules:
        try:
            all_texts.append(m.read_text(encoding="utf-8"))
        except OSError:
            pass

    requirement_ids: list[str] = []
    acceptance_ids: list[str] = []
    for t in all_texts:
        for rid in extract_requirement_ids(t):
            if rid not in requirement_ids:
                requirement_ids.append(rid)
        acceptance_ids += [e.id for e in extract_acceptance_entries(t)]

    # BBX-002/003: inventory explicitly present interface-relevant sections;
    # report absence as a gap rather than guessing content.
    present_sections = {strip_leading_numeral(h[1]) for h in report.doc.headings if h[0] <= 2}
    interface_inventory = {name: (name in present_sections) for name in _INTERFACE_SECTION_NAMES}
    missing_interface_sections = [name for name, present in interface_inventory.items() if not present]
    for name in missing_interface_sections:
        findings.append(
            structural.make_finding(
                "BBX-003",
                "warning",
                f"expected black-box-relevant section '{name}' was not found; interface inventory is incomplete",
                str(root_spec_path),
            )
        )

    actor_operation_coverage, actor_operation_findings = _actor_operation_check(report.doc, root_spec_path)
    findings += actor_operation_findings

    interface_elements = _interface_element_names(report.doc)

    # BBX-002/003/004/005: interface I/O facilitation drafting and
    # requirements<->interface cross-mapping are genuinely semantic checks.
    # specmd has no Direct-Provider Mode in this build; Host-Agent Mode
    # (COG-001) supplies them instead, via `cognitive_input`, once the
    # calling agent has reasoned over a prior call's `cognitive_package`.
    cognitive_results: dict = {}
    cognitive_findings: list[Finding] = []
    cog_used = cog.used
    cog_complete = cog.complete
    cog_exit_override = cog.exit_override

    if cog.requested != "off":
        if cognitive_input is not None:
            host_result = host_agent.validate_and_merge(
                cognitive_input,
                known_requirement_ids=requirement_ids,
                known_interface_elements=interface_elements,
            )
            cognitive_results["io_facilitation_drafts"] = host_result.interfaces
            cognitive_results["requirements_interface_cross_mapping"] = host_result.cross_mapping

            cog_used = "host-agent"
            cog_complete = set(interface_elements) <= host_result.covered_interface_elements
            cog_exit_override = None if cog_complete else cog.exit_override

            for name, entry in host_result.interfaces.items():
                for gap in entry["gaps"]:
                    cognitive_findings.append(
                        Finding(
                            rule_id="BBX-003",
                            severity="information",
                            message=f"Host-Agent gap for interface '{name}': {gap}",
                            evidence_type=EVIDENCE_HEURISTIC,
                            file=str(root_spec_path),
                            reviewers=["host-agent"],
                        )
                    )
            for rid in host_result.cross_mapping["unmatched_requirements"]:
                cognitive_findings.append(
                    Finding(
                        rule_id="BBX-003",
                        severity="information",
                        message=f"Host-Agent: requirement '{rid}' has no corresponding interface element",
                        evidence_type=EVIDENCE_HEURISTIC,
                        file=str(root_spec_path),
                        reviewers=["host-agent"],
                    )
                )
            for rejection in host_result.rejected_citations:
                # A hallucinated citation must be visible, not silently
                # dropped (PROV-006 applied to a Host-Agent's response).
                cognitive_findings.append(
                    Finding(
                        rule_id="BBX-004",
                        severity="warning",
                        message=f"Host-Agent citation rejected: {rejection}",
                        evidence_type=EVIDENCE_HEURISTIC,
                        file=str(root_spec_path),
                        reviewers=["host-agent"],
                    )
                )
            if not cog_complete:
                missing = sorted(set(interface_elements) - host_result.covered_interface_elements)
                cognitive_findings.append(
                    Finding(
                        rule_id="BBX-004",
                        severity="information",
                        message=(
                            "Host-Agent input did not cover every known interface element; missing: "
                            + ", ".join(missing)
                        ),
                        evidence_type=EVIDENCE_HEURISTIC,
                        file=str(root_spec_path),
                        reviewers=["host-agent"],
                    )
                )
        else:
            cognitive_results["cognitive_package"] = _build_cognitive_package(report.doc, requirement_ids, interface_elements)
            if cog.used == "none":
                cognitive_findings.append(
                    Finding(
                        rule_id="BBX-004",
                        severity="information",
                        message=(
                            "Interface I/O facilitation drafting and requirements-to-interface cross-mapping "
                            "were not performed yet; no Cognitive Provider is configured in this build. A "
                            "'cognitive_package' is included for Host-Agent Mode (COG-001) — the calling agent "
                            "may reason over it and resupply this command with --cognitive-input. Deterministic "
                            "completeness results are unaffected."
                        ),
                        evidence_type=EVIDENCE_HEURISTIC,
                        file=str(root_spec_path),
                    )
                )
    findings += cognitive_findings

    # BBX-006/007/009/010: trace correlation, kept as a separate dimension.
    trace_report = trace_pair.validate_pair(
        trace_mode=trace_mode,
        root_spec_path=root_spec_path,
        root_spec_text=report.doc.text,
        root_spec_frontmatter=report.doc.frontmatter or {},
        requirement_ids=requirement_ids,
        acceptance_ids=acceptance_ids,
    )
    findings += trace_report.findings

    implementation_reference_status: dict[str, str] = {}
    executed_evidence_status: dict[str, str] = {}
    trace_available = trace_report.trace_path is not None and trace_report.trace_result == trace_pair.TRACE_RESULT_SUCCESS
    if trace_available:
        trace_text = trace_report.trace_path.read_text(encoding="utf-8")
        row_map = trace_pair.row_evidence_map(trace_text)
        for rid in requirement_ids:
            row = row_map.get(rid)
            if row is None:
                implementation_reference_status[rid] = "unmapped"
                executed_evidence_status[rid] = "unmapped"
                continue
            implementation_reference_status[rid] = "TBD" if trace_pair.is_placeholder(row["implementation"]) else "referenced"
            # Heuristic (disclosed): "executed" requires a non-placeholder
            # Implementation cell that also looks like it names test evidence,
            # or an Evidence-like cell that is itself non-placeholder text —
            # never invented, only read from what the Trace Document states.
            impl = row["implementation"]
            evid = row["evidence"]
            looks_executed = (not trace_pair.is_placeholder(impl) and "test" in impl.lower()) or (
                evid and not trace_pair.is_placeholder(evid)
            )
            executed_evidence_status[rid] = "planned_or_unclear" if trace_pair.is_placeholder(impl) else (
                "likely_executed" if looks_executed else "unclear"
            )

    results = {
        "core_profile": {
            "version": core_profile.CORE_VERSION,
            "optional_version": core_profile.OPTIONAL_VERSION,
            "versions_supported": list(core_profile.SUPPORTED_CORE_VERSIONS),
            "optional_versions_supported": list(core_profile.SUPPORTED_OPTIONAL_VERSIONS),
            "provenance": core_profile.PROFILE_PROVENANCE,
        },
        "requirement_ids": requirement_ids,
        "acceptance_ids": acceptance_ids,
        "interface_section_inventory": interface_inventory,
        # BBX-010: four separate completeness dimensions.
        "completeness": {
            "specification_completeness": {
                "missing_interface_sections": missing_interface_sections,
                # Both severities: since Core §2's missing-section check is a
                # warning (not an error) by design, filtering to errors only
                # would silently drop that signal from completeness reporting.
                "structural_findings": [f.to_dict() for f in report.findings if f.severity in ("error", "warning")],
                "actor_operation_coverage": actor_operation_coverage,
                "interface_elements": interface_elements,
                **cognitive_results,
            },
            "trace_coverage": {
                "available": trace_available,
                "pair_result": trace_report.pair_result,
                "missing_requirement_ids": trace_report.missing_requirement_ids,
                "missing_acceptance_ids": trace_report.missing_acceptance_ids,
            },
            "implementation_reference_completeness": {
                "available": trace_available,
                "by_requirement_id": implementation_reference_status,
            },
            "executed_evidence_completeness": {
                "available": trace_available,
                "by_requirement_id": executed_evidence_status,
                "note": (
                    "heuristic: derived from Trace Document cell text, not from actually running anything "
                    "(BBX-012); 'likely_executed' is a textual signal, not proof"
                ),
            },
        },
    }

    writes = []
    if export_path is not None:
        try:
            write_result = writer.safe_write(export_path, json.dumps(results, indent=2) + "\n", force=True)
            writes.append({"path": write_result.path, "action": write_result.action})
        except writer.WriteRefused as exc:
            writes.append({"path": str(exc.path), "action": "refused"})

    status = "findings" if any(f.severity == "error" for f in findings) else "succeeded"
    if structural.version_unresolved(report):
        status = "indeterminate"
    exit_code = {"succeeded": exit_codes.SUCCESS, "findings": exit_codes.FINDINGS, "indeterminate": exit_codes.INPUT_ERROR}[status]

    if cog_exit_override is not None:
        # COG-009 / ICD-EXIT-001: cognitive mode 'required' but unavailable
        # (and not satisfied by a complete Host-Agent submission) makes the
        # semantic result indeterminate without discarding the deterministic
        # findings already computed above.
        exit_code = cog_exit_override
        status = "indeterminate"

    envelope = build_envelope(
        command="blackbox",
        status=status,
        inputs={
            "root_spec": display_path,
            "trace": trace_mode,
            "cognitive": cognitive_mode,
            "export": str(export_path) if export_path else None,
        },
        results=results,
        findings=findings,
        writes=writes,
        cognitive_requested=cog.requested,
        cognitive_used=cog_used,
        cognitive_complete=cog_complete,
    )
    return envelope, exit_code
