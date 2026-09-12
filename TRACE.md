---
specmd_trace: "0.4.0"
traces_file: "SPEC.md"
traces_spec: "0.11.0"
status: draft
name: "specmd Tool Traceability"
last_updated: "2026-09-12"
---

# specmd Tool — TRACE.md

## Purpose

This informative companion maps the Specification Set rooted at `SPEC.md` version `0.11.0` to logical design areas and planned verification evidence.

The normative specification remains authoritative. This document does not add, remove, or reinterpret required behavior.

No implementation exists at this stage. Implementation references and executed evidence therefore remain `TBD`. `TBD` in this document identifies missing trace evidence, not an unresolved product requirement.

## Trace Model

```text
Requirement → Logical design area → Implementation reference → Verification evidence
```

Verification methods use:

- **T** — Test
- **A** — Analysis
- **I** — Inspection
- **D** — Demonstration

## Requirements Traceability Matrix

| Requirements | Logical design area | Method | Planned evidence | Implementation |
|---|---|---:|---|---|
| CLI-001, CLI-002, CLI-003 | Command router and input resolver | T, D | Invocation and default-path fixtures | src/specmd/resolver.py (tests/test_validate.py) |
| CLI-004, CLI-005, CLI-006 | Reporting layer and JSON serializer | T, I | Human/JSON output fixtures and schema checks | TBD |
| CLI-007 | Process result mapper | T, I | Exit-status matrix across success and failure cases | src/specmd/exit_codes.py, src/specmd/cli.py (tests/test_cli_contract.py) |
| CLI-008, CLI-009 | Platform abstraction and local resource resolver | T, A | Cross-platform and offline test suites | TBD |
| CLI-010 | Safe output writer | T | Existing-destination preservation fixture | src/specmd/writer.py (tests/test_init.py, tests/test_render.py) |
| CLI-011 | Creation Profile parser | T | Supported and unsupported profile fixtures | src/specmd/cli.py, src/specmd/structural.py (tests/test_validate.py, tests/test_init.py) |
| CLI-012, CLI-013 | Filename-independent input resolver | T, I | Custom-root filename and no-guess discovery fixtures | src/specmd/resolver.py (tests/test_validate.py) |
| INIT-001, INIT-002, INIT-003 | Initializer and Core template provider | T, I | Generated minimal SPEC.md conformance fixture | src/specmd/commands/init.py (tests/test_init.py) |
| INIT-004, INIT-005 | Interactive and structured initialization inputs | T, D | Interactive and non-interactive initialization fixtures | TBD |
| INIT-006 | Decision-boundary handling | T, I | Incomplete-input fixture proving no invented behavior | TBD |
| INIT-007 | Template resolver | T | Selected-template and independent-readability fixtures | TBD |
| INIT-008, INIT-009, INIT-010 | Creation Profile selector and defaults | T, D | Explicit, implicit, and interactive profile fixtures | TBD |
| INIT-011, INIT-012 | Profile-specific frontmatter generator | T, I | Core-only and Core + Optional golden fixtures | src/specmd/commands/init.py (tests/test_init.py) |
| INIT-013, INIT-014, INIT-015 | Optional feature selector | T, I | Exact-feature selection, non-empty selection, and no-unrequested-feature fixtures | src/specmd/commands/init.py (tests/test_init.py) |
| VAL-001 | Version-aware rule engine | T | Per-Core-version validation fixtures | src/specmd/structural.py (tests/test_validate.py) |
| VAL-002 | Parser and validation rules | T | Positive and negative rule catalog fixtures | TBD |
| VAL-003 | Normative consistency analyzer | T, A | Explicit-conflict fixtures | TBD |
| VAL-004 | Finding classifier | T, I | Deterministic/heuristic classification fixtures | src/specmd/findings.py (tests/test_cli_contract.py) |
| VAL-005 | Specification Set reporter | T | Multi-module evaluated-file fixture | src/specmd/commands/validate.py, src/specmd/module_resolver.py (tests/test_validate.py) |
| VAL-006, VAL-007, VAL-008 | Core resolver and result state model | T | Missing-Core and incomplete-check fixtures | src/specmd/structural.py (tests/test_validate.py) |
| VAL-009 | Result presentation | I, T | Structural-pass disclaimer fixture | TBD |
| VAL-010, VAL-011 | Module index parser and safe path resolver | T, A | Valid, cyclic, missing, duplicate, and escaping-path fixtures | src/specmd/module_resolver.py (tests/test_validate.py) |
| VAL-012, VAL-013 | Automatic profile detector | T | Core-only auto-detection and no-warning fixture | src/specmd/structural.py (tests/test_validate.py) |
| VAL-014, VAL-017 | Optional resolver and feature-rule registry | T, I | Supported and unknown Optional feature fixtures | src/specmd/structural.py, src/specmd/core_profile.py (tests/test_validate.py) — VAL-017's "unrecognized feature" is reported as informational, not a defect, per Optional 0.4.2 §44's confirmed open feature set |
| VAL-015, VAL-016 | Explicit profile evaluator | T | Forced-Core and missing-Optional fixtures | TBD |
| TRACE-001, TRACE-002 | Trace command-input parser | T | Explicit and default trace-mode fixtures | src/specmd/trace_pair.py (tests/test_validate.py) |
| TRACE-003, TRACE-004, TRACE-005 | Trace discovery and pair-state resolver | T | Declared, undeclared, present, and missing trace fixtures | TBD |
| TRACE-006 | Pair file and version comparator | T | Matching and mismatching `traces_file` and `traces_spec` fixtures | TBD |
| TRACE-007, TRACE-008, TRACE-009, TRACE-010 | Trace ID and coverage analyzer | T, I | Missing, unknown, explicit, ranged, and acceptance-mapping fixtures | TBD |
| TRACE-011, TRACE-012 | Evidence-status classifier | T, I | `TBD`, `Planned`, and executed-evidence fixtures | TBD |
| TRACE-013, TRACE-014, TRACE-015 | Pair result model | T | Independent specification, trace, and pair result fixtures | TBD |
| TRACE-016 | Trace-skip path | T | Explicit `none` fixture | TBD |
| TRACE-017 | Normative authority boundary | T, I | Conflicting-trace-text fixture | TBD |
| TRACEGEN-001, TRACEGEN-002, TRACEGEN-003 | Trace generator and metadata writer | T, I | Default-path and version-alignment fixtures | src/specmd/commands/trace.py (tests/test_trace.py) |
| TRACEGEN-004, TRACEGEN-005, TRACEGEN-006 | Initial trace mapper | T, I | Complete-ID and no-invented-evidence fixtures | src/specmd/commands/trace.py, src/specmd/ids.py (tests/test_trace.py) |
| TRACEGEN-007, TRACEGEN-008 | Optional trace enabler | T, I | Core-only refusal and explicit-enable fixtures | src/specmd/commands/trace.py (tests/test_trace.py) |
| TRACEGEN-009, TRACEGEN-010 | Trace reconciler | T, I | Add, retain, remove, and manual-content preservation fixtures | src/specmd/commands/trace.py (tests/test_trace.py) |
| TRACEGEN-011, TRACEGEN-012, TRACEGEN-013 | Pair-validation, safe-write, and default-path integration | T | Post-generation pair, failure-integrity, and adjacent-update fixtures | src/specmd/commands/trace.py, src/specmd/trace_pair.py (tests/test_trace.py) |
| INTG-001, INTG-002, INTG-003, INTG-004, INTG-005 | Tool-neutral and capability-discovery integration | T, I | CLI/JSON parity, discovery, custom-path, and caller-equivalence fixtures | TBD |
| COG-001, COG-002, COG-003, COG-004, COG-005 | Cognitive mode and result separation | T, I | Host/direct/off mode and result-label fixtures | TBD |
| COG-006, COG-007, COG-008, COG-009 | Cognitive authority and failure boundaries | T, A | No-invention, proposal, evidence, and provider-failure fixtures | TBD |
| AGENT-001, AGENT-002, AGENT-003 | Coding-agent capability and patch boundary | T, I | Operation availability and propose/apply authorization fixtures | TBD |
| AGENT-004, AGENT-005, AGENT-006, AGENT-007 | Living-spec agent instructions and authority | T, I | Adapter content and conflict fixtures | TBD |
| AGENT-008, AGENT-009 | Adapter target registry | T | Required and unsupported target fixtures | TBD |
| AGENT-010, AGENT-011 | Agent/Cucumber responsibility and execution boundary | T, I | Step-definition ownership and no-implicit-run fixtures | TBD |
| AGENT-012 | Agent standards-version preservation | T, I | Historical repository and explicit-local-source fixtures | TBD |
| ADPI-001, ADPI-002, ADPI-003, ADPI-004 | Adapter generation, installation, and preservation | T, I | Generate/install separation and update-conflict fixtures | TBD |
| MCP-001, MCP-002, MCP-003, MCP-004, MCP-005 | Structured tool interface | T, I | Capability parity, authorization, and discovery contract suite | src/specmd/mcp_server.py (tests/test_mcp_server.py) — hand-rolled stdio JSON-RPC 2.0 protocol (no official SDK: requires Python >=3.10, this build targets 3.9); MCP-002's 9 operations wrap the same command modules the CLI uses (MCP-003); validate_pair is a genuinely distinct pair-only operation, not a validate() alias; propose_patch is an honest stub (no patch-generation capability exists) |
| PROV-001, PROV-002, PROV-003, PROV-004 | Provider configuration, credentials, and transmission boundary | T, A | Secure-config, disclosure, redaction, and comment-exclusion fixtures | TBD |
| PROV-005, PROV-006, PROV-007, PROV-008, PROV-009 | Provider request, response, provenance, and failure behavior | T, I | Structured-response, untrusted-input, provenance, disable, and failure fixtures | TBD |
| CTX-001, CTX-002, CTX-003, CTX-004, CTX-005, CTX-006 | Agent and provider context preparation | T, I | Root/module inclusion, filtering, precedence, truncation, and labeling fixtures | TBD |
| AUTO-001, AUTO-002, AUTO-003, AUTO-004, AUTO-005, AUTO-006 | CI and automation integration | T, A | Non-interactive, JSON, custom-path, policy, and no-auto-apply fixtures | TBD |
| ICOMP-001, ICOMP-002, ICOMP-003, ICOMP-004 | Integration compatibility negotiation | T, I | Version compatibility and capability-rejection fixtures | TBD |
| MREV-001, MREV-002, MREV-003 | Lightweight multi-review coordinator | T, A | Optional reviewer selection and coordinator-boundary fixtures | TBD |
| MREV-004, MREV-005, MREV-006, MREV-007, MREV-008 | Independent review and provenance aggregator | T, I | Equivalent-context, independence, overlap, disagreement, and heuristic-label fixtures | TBD |
| MREV-009, MREV-010, MREV-011, MREV-012 | Reviewer failure, disclosure, discovery, and authorization boundary | T, A | Policy, remote-disclosure, capability, and no-auto-apply fixtures | TBD |
| ICD-GEN-001, ICD-GEN-002, ICD-GEN-003, ICD-GEN-004, ICD-GEN-005 | CLI grammar and interaction rules | T | Invalid, ignored, stdin, and non-interactive fixtures | TBD |
| ICD-IN-001, ICD-IN-002, ICD-IN-003, ICD-IN-004, ICD-IN-005, ICD-IN-006 | CLI input and path resolution | T, I | Explicit/default/custom/no-guess and path-display fixtures | src/specmd/resolver.py (tests/test_validate.py) |
| ICD-OUT-001, ICD-OUT-002, ICD-OUT-003, ICD-OUT-004, ICD-OUT-005, ICD-OUT-006 | CLI output and safe-write behavior | T, A | Authorization, atomicity, failure-state, and read-only fixtures | src/specmd/writer.py (tests/test_init.py, tests/test_render.py) |
| ICD-COG-001, ICD-COG-002, ICD-COG-003 | CLI cognitive-mode behavior | T | Label, requested/used, and disabled-provider fixtures | src/specmd/cognitive.py (tests/test_inspect.py) |
| ICD-REV-001, ICD-REV-002, ICD-REV-003 | Reviewer option parser and applicability rules | T | Exact, duplicate, missing-reviewer, and cognitive-off fixtures | TBD |
| ICD-REV-004, ICD-REV-005, ICD-REV-006, ICD-REV-007, ICD-REV-008 | Reviewer orchestration and policy result mapper | T, I | Authorization, order-independence, policy, and provenance fixtures | TBD |
| ICD-BBX-001, ICD-BBX-002, ICD-BBX-003, ICD-BBX-004 | Black-box CLI and result contract | T, I | Trace-mode, export, result-dimension, and reviewer-provenance fixtures | TBD |
| ICD-CUKE-001, ICD-CUKE-002, ICD-CUKE-003, ICD-CUKE-004, ICD-CUKE-005 | Cucumber CLI routing and execution boundary | T, A | Exact target, export, no-execution, explicit-run, and trusted-config fixtures | TBD |
| ICD-CUKE-006, ICD-CUKE-007, ICD-CUKE-008, ICD-CUKE-009, ICD-CUKE-010 | Cucumber status, import, disclosure, and process controls | T, I | Exit, trace-update, JSON, disclosure, timeout, and cancellation fixtures | TBD |
| ICD-SRC-001, ICD-SRC-002, ICD-SRC-003, ICD-SRC-004, ICD-SRC-005, ICD-SRC-006, ICD-SRC-007 | Common standards-source CLI options | T, I | Auto, repository, local, explicit-file, offline, conflict, and provenance fixtures | TBD |
| ICD-HELP-001, ICD-HELP-002, ICD-HELP-003, ICD-HELP-004, ICD-HELP-005, ICD-HELP-006 | Help CLI and metadata contract | T, I | Root, command, topic, offline, example-safety, and JSON fixtures | src/specmd/commands/help.py, src/specmd/command_metadata.py (tests/test_help.py) — partial: no explicit command-syntax grammar line or example invocations shown yet |
| ICD-STD-001, ICD-STD-002, ICD-STD-003, ICD-STD-004, ICD-STD-005 | Standards catalog, exact/latest resolver, and fetch writer | T, A | Channel, unavailable, latest, Optional compatibility, and overwrite fixtures | TBD |
| ICD-STD-006, ICD-STD-007, ICD-STD-008, ICD-STD-009, ICD-STD-010 | Local verification, trust, privacy, version preservation, and discovery | T, I | Custom-file, trusted-config, no-project-upload, historical-version, and capability fixtures | src/specmd/commands/standards.py (tests/test_standards.py) — ICD-STD-006/009 tested directly; ICD-STD-007/008 hold trivially (no network/repository code path exists at all); ICD-STD-010's standards-specific capability discovery is not separately implemented beyond the global `capabilities` command |
| ICD-JSON-001, ICD-JSON-002, ICD-JSON-003, ICD-JSON-004 | JSON envelope and finding semantics | T, I | Schema and enum fixtures | src/specmd/envelope.py, src/specmd/findings.py (tests/test_cli_contract.py) |
| ICD-JSON-005, ICD-JSON-006, ICD-JSON-007, ICD-JSON-008, ICD-JSON-009 | JSON writes, reviewer metadata, and forward compatibility | T, I | Write-summary, reviewer-status, disagreement, and unknown-property fixtures | TBD |
| ICD-EXIT-001, ICD-EXIT-002, ICD-EXIT-003, ICD-EXIT-004 | Process exit status contract | T, I | Status consistency, pair result, multi-failure, and reserved-code fixtures | TBD |
| ICD-COMP-001, ICD-COMP-002, ICD-COMP-003, ICD-COMP-004 | CLI and schema compatibility | T, I | Independent version, breaking/minor change, and deprecation fixtures | TBD |
| INSP-001 | Inspection orchestrator | T | Source-integrity comparison | src/specmd/commands/inspect.py (tests/test_inspect.py) |
| INSP-002, INSP-003, INSP-004 | Quality analyzers | T, A | Quality-dimension corpus and heuristic review | TBD |
| INSP-005, INSP-006, INSP-007 | Measurement and Core classifier | T | Core/non-Core size-boundary fixtures | src/specmd/structural.py, src/specmd/commands/inspect.py (tests/test_inspect.py) |
| INSP-008 | Optional probabilistic analyzer boundary | T, I | Analyzer-present and analyzer-absent fixtures | src/specmd/cognitive.py, src/specmd/commands/inspect.py (tests/test_inspect.py) |
| REND-001, REND-002, REND-003 | Rendering pipeline and context filter | T, I | Golden render and human-only exclusion fixtures | src/specmd/commands/render.py, src/specmd/human_only.py (tests/test_render.py) |
| REND-004, REND-005 | HTML and PDF renderers | T, D | Format generation and visual inspection | src/specmd/commands/render.py (tests/test_render.py; PDF explicitly unavailable, exit 4) |
| REND-006, REND-007 | Specification Set assembler and provenance header | T, I | Modular render with version identification | TBD |
| REND-008 | Self-contained asset policy | T, I | Offline rendered-output inspection | TBD |
| TEST-001, TEST-002, TEST-003 | Verification coverage analyzer | T | Covered, uncovered, and orphan acceptance fixtures | src/specmd/commands/coverage.py (tests/test_coverage_command.py) |
| TEST-004 | Tool-neutral test-plan exporter | T, I | Export schema and content fixture | src/specmd/commands/coverage.py (tests/test_coverage_command.py) |
| TEST-005, TEST-006, TEST-007 | Implementation-test boundary | T, A | Non-execution, explicit-integration, and claim-label fixtures | src/specmd/commands/coverage.py (tests/test_coverage_command.py) |
| BBX-001, BBX-002, BBX-003, BBX-004, BBX-005 | Black-box contract analyzer | T, A | Interface inventory, gap, ambiguity, and evidence-label corpus | TBD |
| BBX-006, BBX-007, BBX-008, BBX-009, BBX-010 | Trace-aware black-box correlator | T, I | Trace present, absent, conflicting, and four-dimension result fixtures | src/specmd/commands/blackbox.py, src/specmd/trace_pair.py (tests/test_blackbox.py) — BBX-007 correlation is at requirement-ID granularity, not per-interface-element |
| BBX-011, BBX-012 | Black-box exporter and execution boundary | T, I | Tool-neutral export and no-runtime-execution fixtures | src/specmd/commands/blackbox.py (tests/test_blackbox.py) |
| ADAPT-001 | Adapter registry and generator | T | Supported-target generation fixtures | src/specmd/commands/adapt.py (tests/test_adapt.py) |
| ADAPT-002, ADAPT-003, ADAPT-004, ADAPT-005, ADAPT-006 | Canonical adapter policy | T, I | Adapter contract suite for every target | src/specmd/commands/adapt.py (tests/test_adapt.py) |
| ADAPT-007 | Read-only source boundary | T | Byte-for-byte source-integrity comparison | src/specmd/commands/adapt.py (tests/test_adapt.py) |
| ADAPT-008, ADAPT-009 | Target allowlist | T | Supported and unsupported target fixtures | src/specmd/commands/adapt.py (tests/test_adapt.py) |
| SAFE-001, SAFE-002 | Read/write operation boundary | T, A | Mutation audit and replacement-authorization fixtures | TBD |
| SAFE-003, SAFE-004, SAFE-005 | Data-handling and redaction boundary | T, I | Network-denial, consent-display, and redaction fixtures | TBD |
| SAFE-006 | Human-only block parser | T | Malformed and unclosed delimiter fixtures | src/specmd/human_only.py (tests/test_validate.py) |
| SAFE-007 | Derived-artifact provenance | T, I | Generated-file provenance inspection | TBD |
| REL-001 | Set-level failure propagation | T | Unreadable-module fixture | TBD |
| REL-002 | Safe output writer | T, A | Failure-injection and atomicity fixture | TBD |
| REL-003 | Finding sorter | T | Deterministic-order snapshot | TBD |
| REL-004 | Generation result reporter | T | Partial-output failure fixture | TBD |
| PORT-001, PORT-002, PORT-003 | Core compatibility layer | T, I | Multi-version compatibility suite | TBD |
| PORT-004 | Independent artifact versioning | I, T | Schema, adapter, and rule-version checks | TBD |
| PORT-005 | Platform abstraction | T | Normalized cross-platform result comparison | TBD |
| PORT-006, PORT-007, PORT-008 | Version Alignment Process — exact-version resolver and indeterminate/remediation reporter | T, I | Non-substitution, indeterminate-on-unresolved, and first-suggested-remediation fixtures | src/specmd/structural.py (version_unresolved, version_alignment_finding), applied in commands/validate.py, commands/inspect.py, commands/trace.py (tests/test_validate.py, tests/test_inspect.py, tests/test_trace.py) |
| CUKE-001, CUKE-002, CUKE-003, CUKE-004, CUKE-005, CUKE-006 | Optional connector architecture | T, A | Absence, isolation, discovery, invocation, and authority fixtures | TBD |
| CUKE-EXP-001, CUKE-EXP-002, CUKE-EXP-003, CUKE-EXP-004, CUKE-EXP-005, CUKE-EXP-006 | Source-linked Gherkin exporter | T, I | Explicit, incomplete, proposed, provenance, and no-step-code fixtures | TBD |
| CUKE-VAL-001, CUKE-VAL-002, CUKE-VAL-003, CUKE-VAL-004 | Non-executing Gherkin validator | T, A | Syntax, binding, separated-dimension, and no-coherence-claim fixtures | TBD |
| CUKE-RUN-001, CUKE-RUN-002, CUKE-RUN-003, CUKE-RUN-004 | Explicit runtime launcher boundary | T, A | Authorization, typed-config, scope-disclosure, and injection fixtures | TBD |
| CUKE-RUN-005, CUKE-RUN-006, CUKE-RUN-007, CUKE-RUN-008 | Runtime controls and result semantics | T, I | Timeout, cancellation, crash, failure-label, and no-mutation fixtures | TBD |
| CUKE-IMP-001, CUKE-IMP-002, CUKE-IMP-003, CUKE-IMP-004 | Report parser and read-only importer | T, I | Format, provenance, state, malformed-input, and source-integrity fixtures | TBD |
| CUKE-IMP-005, CUKE-IMP-006, CUKE-IMP-007 | Authorized trace evidence updater | T, A | Exact-ID, preservation, pair-validation, and non-passing-evidence fixtures | TBD |
| CUKE-SEC-001, CUKE-SEC-002, CUKE-SEC-003, CUKE-SEC-004, CUKE-SEC-005, CUKE-SEC-006 | Connector licensing, portability, and security boundary | T, A | Disclosure, packaging, offline, discovery, least-authority, and secret fixtures | TBD |
| HELP-001, HELP-002, HELP-003, HELP-004 | Self-contained capability-aware help | T, I | Root, command, subcommand, safety, and availability fixtures | src/specmd/commands/help.py, src/specmd/command_metadata.py (tests/test_help.py) — partial: no explicit command-syntax grammar line shown yet |
| HELP-005, HELP-006, HELP-007, HELP-008 | Offline safe examples and help-schema alignment | T, I | No-external-call, hazard-label, parser parity, and JSON-schema fixtures | TBD |
| SRC-001, SRC-002, SRC-003, SRC-004, SRC-005, SRC-006, SRC-007, SRC-008 | Standards source selector and provenance | T, A | Auto, local, directory, cache, repository, offline, no-fallback, and provenance fixtures | TBD |
| SRC-009, SRC-010, SRC-011, SRC-012, SRC-013, SRC-014, SRC-015 | Latest, historical, withdrawn, and compatible release resolver | T, A | Catalog-channel, alias resolution, historical absence, existing-doc, init, Optional, and withdrawal fixtures | TBD |
| SRC-016, SRC-017, SRC-018, SRC-019, SRC-020, SRC-021, SRC-022, SRC-023 | Local copy, cache, fetch, integrity, privacy, and reproducibility | T, I | Kind/version, mismatch, immutability, atomic fetch, no-project-upload, tamper, metadata-free-local, and digest fixtures | TBD |
| SRC-024, SRC-025, SRC-026, SRC-027, SRC-028 | Standards list, show, fetch, verify, and reporting operations | T, I | Offline and online operation contract suite | TBD |

## Acceptance Traceability Matrix

| Acceptance | Requirements verified | Planned evidence | Status |
|---|---|---|---|
| ACC-001 | INIT-001, INIT-002, INIT-003, CLI-010 | Initialization and overwrite-protection test | Planned |
| ACC-002 | INIT-006 | Incomplete-product-input inspection | Planned |
| ACC-003 | VAL-001, VAL-006, VAL-007 | Available- and missing-Core validation tests | Planned |
| ACC-004 | VAL-002, SAFE-006 | Unclosed human-only block test | Planned |
| ACC-005 | INV-003, INSP-005, INSP-006 | 500-line non-Core specification test | Planned |
| ACC-006 | INV-004, INSP-007 | Core compactness-boundary test | Planned |
| ACC-007 | INV-006, ADAPT-005, REND-003 | Human-only exclusion tests | Planned |
| ACC-008 | INV-007, VAL-005 | Missing-module test | Planned |
| ACC-009 | TEST-001, TEST-002, TEST-003 | Partial acceptance-coverage test | Planned |
| ACC-010 | TEST-005, TEST-006 | Embedded-code non-execution test | Planned |
| ACC-011 | ADAPT-001, ADAPT-002, ADAPT-007 | Adapter generation and source-integrity test | Planned |
| ACC-012 | SAFE-003, SAFE-004 | Offline network-denial test | Planned |
| ACC-013 | REND-001, REND-002, REND-007 | HTML golden-render test | Planned |
| ACC-014 | CLI-005, CLI-006, CLI-007 | CI JSON and exit-status test | Planned |
| ACC-015 | VAL-010, VAL-011 | Escaping-module-path test | Planned |
| ACC-016 | REL-002, REL-004 | Authorized-replacement failure injection | Planned |
| ACC-017 | PORT-001, PORT-002, PORT-003 | Multi-Core-version validation test | Planned |
| ACC-018 | INIT-008, INIT-009, INIT-011 | Core-only creation and default-profile test | Planned |
| ACC-019 | INIT-008, INIT-010, INIT-012, INIT-013, INIT-014, INIT-015 | Core + Optional exact-feature creation test | Planned |
| ACC-020 | VAL-012, VAL-013 | Core-only automatic validation test | Planned |
| ACC-021 | VAL-012, VAL-014, VAL-017 | Mixed supported/unknown Optional feature test | Planned |
| ACC-022 | VAL-015 | Explicit Core-only validation test | Planned |
| ACC-023 | VAL-016 | Explicit Optional validation without declaration test | Planned |
| ACC-024 | TRACE-001, TRACE-002, TRACE-003 | Automatic declared-trace pair validation | Planned |
| ACC-025 | TRACE-004, TRACE-016 | Undeclared and explicitly skipped trace validation | Planned |
| ACC-026 | TRACE-005, TRACE-013, TRACE-014 | Missing declared trace with independent specification result | Planned |
| ACC-027 | TRACE-006, TRACE-015 | Pair version-mismatch test | Planned |
| ACC-028 | TRACE-007, TRACE-008, TRACE-009, TRACE-010 | Missing, unknown, and ranged identifier test | Planned |
| ACC-029 | TRACE-011, TRACE-012 | Planned-versus-executed evidence classification | Planned |
| ACC-030 | TRACE-017 | Conflicting trace text authority test | Planned |
| ACC-031 | TRACEGEN-001, TRACEGEN-002, TRACEGEN-003, TRACEGEN-004, TRACEGEN-005, TRACEGEN-006 | Trace creation and truthful placeholder test | Planned |
| ACC-032 | TRACEGEN-007, TRACEGEN-008 | Core-only explicit Optional enablement test | Planned |
| ACC-033 | TRACEGEN-009, TRACEGEN-010, TRACEGEN-011, TRACEGEN-012, TRACEGEN-013 | Trace reconciliation, preservation, default-path, and pair validation test | Planned |
| ACC-034 | CLI-002, CLI-003, CLI-012, CLI-013, TRACE-006, TRACEGEN-003 | Custom Root Specification filename, exact trace binding, and no-guess discovery test | Planned |
| ACC-035 | BBX-001, BBX-002, BBX-003, BBX-004, BBX-005, BBX-006, BBX-007, BBX-008, BBX-009, BBX-010, BBX-011, BBX-012 | Black-box contract inventory, trace-awareness, authority, export, and non-execution test | Planned |
| ACC-036 | PORT-006, PORT-007, PORT-008 | Non-substitution, indeterminate-result, and first-suggested-remediation test | Planned |
| IACC-001 | INTG-001, INTG-002, INTG-004, INTG-005 | Human/agent JSON equivalence test | Planned |
| IACC-002 | COG-002, COG-003, COG-004, COG-005 | Deterministic-only limitation and separation test | Planned |
| IACC-003 | COG-006, COG-007, COG-008 | Proposal, inference, and evidence-truthfulness test | Planned |
| IACC-004 | AGENT-002, AGENT-003, MCP-004 | Proposed-patch no-write authorization test | Planned |
| IACC-005 | AGENT-006, AGENT-007, ADPI-001, ADPI-002 | Adapter authority and generate/install separation test | Planned |
| IACC-006 | PROV-002, PROV-003, PROV-004, PROV-008 | Provider credential, disclosure, and filtering test | Planned |
| IACC-007 | CTX-001, CTX-002, CTX-005 | Incomplete-context semantic-result test | Planned |
| IACC-008 | AUTO-001, AUTO-002, AUTO-003, AUTO-004 | Deterministic custom-path CI test | Planned |
| IACC-009 | ICOMP-001, ICOMP-003, ICOMP-004 | Integration major-version rejection test | Planned |
| IACC-010 | MREV-001, MREV-002, MREV-003 | Optional multi-review and lightweight-coordinator test | Planned |
| IACC-011 | MREV-004, MREV-005, MREV-006, MREV-007, MREV-008 | Independent context, provenance, overlap, disagreement, and evidence-label test | Planned |
| IACC-012 | MREV-009, MREV-010, MREV-011 | Reviewer failure-policy, remote-transmission, and capability-discovery test | Planned |
| IACC-013 | MREV-012, AGENT-002, AGENT-003 | Multi-review Proposed Patch no-write test | Planned |
| IACC-014 | AGENT-010, AGENT-011, AUTO-006 | Coding-agent Cucumber responsibility and explicit-execution test | Planned |
| IACC-015 | AGENT-012, CTX-001, CTX-002 | Coding-agent historical and local standards-source preservation test | Planned |
| CLIACC-001 | ICD-GEN-001, ICD-GEN-002 | Unknown and inapplicable option test | Planned |
| CLIACC-002 | ICD-IN-001, ICD-IN-002, ICD-IN-003, ICD-IN-004, ICD-IN-005 | Custom-root and no-guess CLI test | Planned |
| CLIACC-003 | ICD-OUT-001, ICD-OUT-002, ICD-OUT-003, ICD-OUT-004 | Existing-output authorization and preservation test | Planned |
| CLIACC-004 | ICD-COG-001, ICD-COG-002, ICD-COG-003 | Cognitive-off CLI test | Planned |
| CLIACC-005 | ICD-JSON-001, ICD-JSON-002, ICD-JSON-003, ICD-JSON-004, ICD-JSON-005 | Single-envelope and finding-semantics test | Planned |
| CLIACC-006 | ICD-EXIT-001, ICD-EXIT-002, ICD-EXIT-003 | Misaligned-pair exit and finding-preservation test | Planned |
| CLIACC-007 | ICD-COMP-001, ICD-COMP-002 | Incompatible JSON schema rejection test | Planned |
| CLIACC-008 | ICD-REV-001, ICD-REV-002, ICD-REV-003 | Invalid reviewer-option combination test | Planned |
| CLIACC-009 | ICD-REV-004, ICD-REV-005, ICD-REV-008 | Reviewer authorization, order-independence, provenance, and disagreement test | Planned |
| CLIACC-010 | ICD-REV-006, ICD-REV-007, ICD-JSON-008, ICD-JSON-009 | Best-effort and required reviewer-failure test | Planned |
| CLIACC-011 | ICD-BBX-001, ICD-BBX-002, ICD-BBX-003, ICD-BBX-004 | Trace-aware black-box command and reviewer test | Planned |
| CLIACC-012 | ICD-CUKE-001, ICD-CUKE-003, ICD-CUKE-004, ICD-CUKE-005, ICD-CUKE-009 | Cucumber exact-routing, isolation, and execution-disclosure test | Planned |
| CLIACC-013 | ICD-CUKE-002, ICD-CUKE-008 | Gherkin export and JSON-envelope test | Planned |
| CLIACC-014 | ICD-CUKE-006, ICD-CUKE-010 | Runtime exit-status, timeout, cancellation, and artifact-state test | Planned |
| CLIACC-015 | ICD-CUKE-007, ICD-CUKE-008 | Cucumber report import and authorized Trace update test | Planned |
| CLIACC-016 | ICD-HELP-001, ICD-HELP-002, ICD-HELP-003, ICD-HELP-004, ICD-HELP-005, ICD-HELP-006 | Offline root, command, unknown-topic, example, and JSON help test | Planned |
| CLIACC-017 | ICD-SRC-001, ICD-SRC-002, ICD-SRC-003, ICD-SRC-004, ICD-SRC-005, ICD-SRC-006, ICD-SRC-007 | Standards-source precedence, offline, conflict, and provenance test | Planned |
| CLIACC-018 | ICD-STD-001, ICD-STD-002, ICD-STD-003, ICD-STD-004 | Stable, prerelease, historical, latest, and Optional-match resolution test | Planned |
| CLIACC-019 | ICD-STD-005, ICD-STD-006, ICD-STD-007, ICD-STD-008 | Standards safe-write, custom-local-file, trust, and privacy test | Planned |
| CLIACC-020 | ICD-STD-009, ICD-STD-010 | Existing historical-version preservation and source-capability test | Planned |
| CUKEACC-001 | CUKE-001, CUKE-002, CUKE-003, CUKE-005 | Connector absence, isolation, and discovery test | Planned |
| CUKEACC-002 | CUKE-004, CUKE-006, CUKE-EXP-001, CUKE-EXP-002, CUKE-EXP-003, CUKE-EXP-004 | Source-linked Gherkin export and authority test | Planned |
| CUKEACC-003 | CUKE-EXP-005, CUKE-EXP-006 | Reviewer provenance and no-step-definition-generation test | Planned |
| CUKEACC-004 | CUKE-VAL-001, CUKE-VAL-002, CUKE-VAL-003, CUKE-VAL-004 | Non-executing syntax, binding, and consistency-boundary test | Planned |
| CUKEACC-005 | CUKE-RUN-001, CUKE-RUN-002, CUKE-RUN-003, CUKE-RUN-004, CUKE-RUN-008 | Explicit typed execution and no-side-effect test | Planned |
| CUKEACC-006 | CUKE-RUN-005, CUKE-RUN-006, CUKE-RUN-007 | Runtime control and failure-semantics test | Planned |
| CUKEACC-007 | CUKE-IMP-001, CUKE-IMP-002, CUKE-IMP-003, CUKE-IMP-004, CUKE-IMP-007 | Safe read-only mixed-state report import test | Planned |
| CUKEACC-008 | CUKE-IMP-005, CUKE-IMP-006, CUKE-SEC-001, CUKE-SEC-002, CUKE-SEC-003, CUKE-SEC-004, CUKE-SEC-005, CUKE-SEC-006 | Authorized evidence update, packaging, offline, authority, and secret-handling test | Planned |
| HSACC-001 | HELP-001, HELP-002, HELP-003, HELP-004 | Complete capability-aware help test | Planned |
| HSACC-002 | HELP-005, HELP-006, HELP-007, HELP-008 | Offline help safety, parser parity, and schema test | Planned |
| HSACC-003 | SRC-001, SRC-002, SRC-003, SRC-004, SRC-005, SRC-006, SRC-007, SRC-008 | Multi-source resolution, precedence, offline, and provenance test | Planned |
| HSACC-004 | SRC-009, SRC-010, SRC-011, SRC-012, SRC-013, SRC-015 | Latest, historical, withdrawn, and existing-document preservation test | Planned |
| HSACC-005 | SRC-014, SRC-015, SRC-016, SRC-017 | Optional compatibility, withdrawal, local validation, and mismatch test | Planned |
| HSACC-006 | SRC-018, SRC-019, SRC-020, SRC-021, SRC-023 | Cache immutability, safe fetch, privacy, integrity, and digest test | Planned |
| HSACC-007 | SRC-022, SRC-024, SRC-025, SRC-026, SRC-027, SRC-028 | Complete offline local-copy standards-operations test | Planned |

## Invariant Traceability Matrix

| Invariant | Enforced by | Verified by | Status |
|---|---|---|---|
| INV-001 | Plain-Markdown inputs and outputs; no runtime dependency in the document | Inspection of generated and processed samples | Planned |
| INV-002 | Read-only analytical command boundary | Source-integrity tests | Planned |
| INV-003 | Non-Core measurement policy | ACC-005 | Planned |
| INV-004 | Core artifact classifier | ACC-006 | Planned |
| INV-005 | Adapter policy | ACC-011 and adapter contract suite | Planned |
| INV-006 | Context filter | ACC-007 | Planned |
| INV-007 | Module resolver and consistency checks | ACC-008 and module-resolution fixtures | Planned |
| INV-008 | Non-executing parser and default test boundary | ACC-010 and embedded-code fixtures | Planned |

## Open Trace Gaps

1. Implementation references remain unavailable until an implementation design and source tree exist.
2. Executed evidence remains unavailable until the verification suite exists.
3. Core registry integrity evidence depends on resolution of Open Issue 1 in the Root Specification.
4. Adapter installation-path evidence depends on resolution of Open Issue 3.
5. Direct-Provider implementation evidence depends on resolution of Open Issue 4.
6. Stable rule-catalog evidence depends on resolution of Open Issue 5.
7. `FLW-001` and `FLW-002` (Behavioral Flow headings, section 3.3) are currently untraced, making `specmd validate --trace auto` report this pair as `misaligned`. This is a genuine, currently-open classification question, not an extraction bug: the implementation's requirement-ID extractor (`src/specmd/ids.py`) recognizes any `#### PREFIX-NNN — Title` heading as a candidate requirement/invariant identifier, and Behavioral Flow headings share that shape without necessarily being RFC2119 requirements themselves (they are process illustrations referencing requirements defined elsewhere). No authoritative Core 0.4.2 text was available to this project to settle whether Behavioral Flow IDs fall under TRACE-007's "every current normative requirement ID and invariant ID." Decide per document rather than hardcoding a rule; for this Root Specification, resolve by either (a) explicitly mapping FLW-001/002 in the matrix below once their trace-worthiness is confirmed, or (b) recording here that they are out of TRACE-007's scope, with rationale.

## Maintenance Rules

- Update this matrix in the same change when a normative requirement is added, changed, or retired.
- Keep requirement IDs aligned with the normative specification; do not reassign removed IDs.
- Replace `TBD` cells with precise source references when implementation begins.
- Replace or supplement planned evidence with immutable evidence references where practical after verification runs.
- Resolve any conflict in favor of `SPEC.md`.
