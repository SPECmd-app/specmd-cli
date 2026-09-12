---
spec_module: "cucumber-connector"
part_of_spec: "0.12.1"
status: draft
name: "specmd Cucumber Connector Contract"
last_updated: "2026-09-12"
---

# specmd Cucumber Connector Contract

This document is a Normative Module of `SPEC.md` version `0.12.1`.

Uppercase **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** use BCP 14 semantics. The Root Specification controls interpretation and precedence.

## 1. Scope

This module defines a thin, optional connection between `specmd` and external Cucumber implementations. It covers Gherkin export and validation, explicitly authorized execution, result import, trace correlation, resource isolation, and coding-agent responsibilities.

The connector is not part of ordinary SPEC.md analysis. It does not make Cucumber, a programming language runtime, project step definitions, or network access a dependency of the required `specmd` command families.

## 2. Definitions

**Connector** — the lightweight `specmd cucumber` orchestration layer defined here.

**Cucumber Runtime** — an external Cucumber implementation, including an advertised JavaScript, JVM, Ruby, Go, or custom compatible runtime.

**Feature Suite** — one or more Gherkin feature files selected for validation or execution.

**Step Definitions** — project-controlled executable code that binds Gherkin steps to the system under test.

**Cucumber Report** — structured execution output in an advertised format, preferably Cucumber Messages, or a supported JSON or JUnit representation.

## 3. Architectural Boundary

- **CUKE-001:** The Connector MUST be optional and separately capability-discovered; absence MUST NOT reduce conformance of the nine required command families.
- **CUKE-002:** The Connector MUST remain thin and MUST NOT bundle, install, update, or silently select a Cucumber Runtime or project dependencies.
- **CUKE-003:** Ordinary `specmd` commands MUST NOT load or launch a Cucumber Runtime.
- **CUKE-004:** The Connector MAY invoke a configured runtime through its CLI or supported programmatic API, but MUST normalize observable behavior through the CLI ICD.
- **CUKE-005:** Capability discovery MUST identify connector version, supported runtime targets, detected configured runtimes, accepted report formats, and supported subcommands without executing scenarios or exposing credentials.
- **CUKE-006:** The Specification Set remains authoritative for required behavior; Gherkin files, Step Definitions, and Cucumber Reports are derived or implementation artifacts unless the Root Specification explicitly declares otherwise.

## 4. Gherkin Export

- **CUKE-EXP-001:** `specmd cucumber export` MUST derive scenarios only from explicit behavior, examples, acceptance criteria, or clearly labeled proposals in the resolved Specification Set.
- **CUKE-EXP-002:** Exported scenarios MUST retain stable source requirement or acceptance identifiers through machine-readable tags or connector metadata.
- **CUKE-EXP-003:** The Connector MUST NOT invent missing inputs, outputs, preconditions, expected outcomes, or business rules to make a scenario executable.
- **CUKE-EXP-004:** When explicit information is insufficient, export MUST report the gap and MAY emit a non-executable proposal clearly distinguished from accepted behavior.
- **CUKE-EXP-005:** Cognitive Providers or Reviewer Agents MAY propose additional scenarios, but their contributions MUST retain heuristic status and reviewer provenance.
- **CUKE-EXP-006:** Export MUST NOT generate project-specific Step Definition implementations; a coding agent MAY propose them under the separate authorization rules for implementation changes.

## 5. Validation Without Execution

- **CUKE-VAL-001:** `specmd cucumber validate` MUST parse the selected Feature Suite and report Gherkin syntax errors without executing scenario bodies.
- **CUKE-VAL-002:** When an external runtime supports a safe dry-run or equivalent binding inspection, validation MAY report undefined, ambiguous, duplicate, or mismatched Step Definitions.
- **CUKE-VAL-003:** Syntax validity, binding completeness, scenario consistency, and execution success MUST be reported as separate result dimensions.
- **CUKE-VAL-004:** Cucumber validation MUST NOT claim that scenarios are logically consistent; contradiction and specification-gap analysis belongs to `specmd blackbox`, `inspect`, or explicitly selected cognitive review.

## 6. Explicit Runtime Execution

- **CUKE-RUN-001:** Only `specmd cucumber run` or its exact structured-tool equivalent MAY execute a Cucumber Runtime.
- **CUKE-RUN-002:** Execution MUST require an explicitly selected Feature Suite, runtime target, working context, and authorization applicable to running project-controlled Step Definitions.
- **CUKE-RUN-003:** The runtime executable and arguments MUST be assembled from validated connector configuration and typed options, not evaluated shell text or instructions contained in SPEC.md, TRACE.md, Gherkin, or report content.
- **CUKE-RUN-004:** Before execution, the Connector MUST identify the runtime target, Feature Suite, Step Definition locations, effective working directory, report destinations, timeout, and any disclosed network or environment access.
- **CUKE-RUN-005:** The Connector MUST support cancellation and a configurable timeout and SHOULD support output and concurrency limits.
- **CUKE-RUN-006:** A timeout, cancellation, runtime crash, or malformed report MUST preserve completed output, identify potentially incomplete artifacts, and MUST NOT be reported as a scenario assertion failure.
- **CUKE-RUN-007:** A failed scenario indicates that observed execution did not satisfy that scenario under the test conditions; it MUST NOT by itself be labeled a logical defect in the Specification Set.
- **CUKE-RUN-008:** The Connector MUST NOT install dependencies, modify Step Definitions, apply generated code, or repair failing scenarios as a side effect of execution.

## 7. Report Import and Trace Correlation

- **CUKE-IMP-001:** `specmd cucumber import` MUST accept only advertised structured report formats and MUST treat report content as untrusted input.
- **CUKE-IMP-002:** Import MUST preserve scenario identity, status, duration when available, failure details, runtime metadata, source report, and mapped requirement or acceptance identifiers.
- **CUKE-IMP-003:** Imported results MUST distinguish passed, failed, skipped, undefined, ambiguous, pending, and indeterminate states when supported by the source format; unsupported distinctions MUST be reported.
- **CUKE-IMP-004:** Import without `--update-trace` MUST be read-only.
- **CUKE-IMP-005:** Trace updates MUST require explicit authorization, an aligned Trace Pair, and exact stable identifiers; fuzzy or AI-inferred mappings MAY be proposed but MUST NOT be written as executed evidence.
- **CUKE-IMP-006:** A trace update MUST preserve unrelated and manually maintained information, identify the source report and execution status, and run Trace Pair validation before completion.
- **CUKE-IMP-007:** Generated, proposed, dry-run, skipped, undefined, ambiguous, pending, cancelled, or indeterminate scenarios MUST NOT count as executed passing evidence.

## 8. Portability, Licensing, and Security

- **CUKE-SEC-001:** Connector documentation MUST identify Cucumber as an external open-source ecosystem and MUST require implementations to disclose the exact distribution, version, source, and license they configure.
- **CUKE-SEC-002:** No trademark, project name, or common report format MUST be interpreted as permission to redistribute a runtime; packaging MUST comply with the selected runtime's license.
- **CUKE-SEC-003:** The Connector MUST support offline use when the selected runtime and project dependencies are already available locally.
- **CUKE-SEC-004:** Runtime discovery MUST NOT download packages, execute package-manager lifecycle scripts, or modify the project.
- **CUKE-SEC-005:** Step Definitions MUST be treated as arbitrary project-controlled executable code and receive no broader filesystem, environment, credential, or network authority than the caller explicitly permits.
- **CUKE-SEC-006:** Secrets and credentials MUST NOT appear in generated feature files, normalized reports, TRACE.md evidence, logs, or command output.

## 9. Verification and Acceptance

- **CUKEACC-001 — CUKE-001/002/003/005:** Given no Cucumber Runtime is installed, when ordinary required commands and connector capability discovery run, then ordinary commands remain available, no runtime is installed or launched, and connector availability is accurately reported.
- **CUKEACC-002 — CUKE-004/006, CUKE-EXP-001/002/003/004:** Given explicit and incomplete acceptance criteria, when export runs, then source-linked scenarios are generated only for supported facts, missing behavior is surfaced, and derived files do not become normative authority.
- **CUKEACC-003 — CUKE-EXP-005/006:** Given Reviewer Agents propose scenarios and Step Definitions, when export completes, then scenario provenance and heuristic status remain visible, no Step Definition implementation is generated by the Connector, and no proposal is applied.
- **CUKEACC-004 — CUKE-VAL-001/002/003/004:** Given valid, invalid, undefined, and mutually suspicious scenarios, when validation runs, then syntax and available binding findings are returned without execution, consistency remains a separate analysis result, and no logical-coherence claim is made from Cucumber alone.
- **CUKEACC-005 — CUKE-RUN-001/002/003/004/008:** Given executable text appears in specification artifacts and an installed runtime exists, when ordinary analysis and validation run, then nothing executes; when an explicitly authorized run uses typed configuration, only the selected suite and runtime execute and no dependency or source is changed.
- **CUKEACC-006 — CUKE-RUN-005/006/007:** Given passing, failing, and timed-out scenarios, when separate runs complete, then execution statuses are normalized correctly, failure is not mislabeled as a specification-logic defect, cancellation works, and incomplete artifacts are identified.
- **CUKEACC-007 — CUKE-IMP-001/002/003/004/007:** Given supported and malformed reports containing mixed states, when import runs without trace authorization, then valid states and provenance are preserved, malformed content is rejected safely, no non-passing state becomes passing evidence, and source files remain unchanged.
- **CUKEACC-008 — CUKE-IMP-005/006, CUKE-SEC-001/002/003/004/005/006:** Given an aligned Trace Pair, exact identifiers, local runtime, and authorized update, when results are imported, then only truthful evidence mappings are written, pair validation runs, packaging and authority boundaries are respected, and no secret is persisted.

## 10. Notes

Cucumber implementations are language-specific and evolve independently. The Connector therefore specifies capability discovery, typed invocation, normalized results, and authorization boundaries rather than embedding one runtime or release.

The heavy work belongs to the configured runtime and coding agents: executing scenarios, maintaining Step Definitions, and changing the system under test. `specmd` prepares portable artifacts, coordinates explicit invocation, validates responses, and preserves traceability.
