---
spec_module: "cli-icd"
part_of_spec: "0.13.0"
status: draft
name: "specmd CLI Interface Control Document"
last_updated: "2026-09-12"
---

# specmd CLI Interface Control Document

This document is a Normative Module of `SPEC.md` version `0.13.0`.

Uppercase **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** use BCP 14 semantics. The Root Specification controls interpretation and precedence.

## 1. Scope

This Interface Control Document defines the public command-line grammar, common options, machine-readable result envelope, exit statuses, input/output rules, and compatibility contract for `specmd`.

## 2. Conventions

```text
<value>   required value
[value]   optional value
...       repeatable value
```

Command names and option values are case-sensitive. Paths MAY be absolute or relative. Relative paths resolve from the current working directory unless a command explicitly states otherwise.

`stdout` contains the requested result. `stderr` contains human-facing diagnostics that are not part of machine-readable output. In JSON mode, `stdout` MUST contain only one valid JSON result envelope.

## 3. Command Grammar

```text
specmd [global-options] <command> [command-options]

standards-options :=
  [--standards-source <auto|repository|local>]
  [--standards-repository <uri|alias>]
  [--standards-dir <path>]
  [--core-document <path>]
  [--optional-document <path>]
  [--offline]

specmd init [output]
  [--profile <core|optional>]
  [--core-version <latest|version>]
  [--optional-version <latest|matching|version>]
  [--feature <name>]...
  [--input-json <path|->]
  [--non-interactive]
  [standards-options]
  [--force]

specmd validate [input]
  [--profile <auto|core|optional>]
  [--trace <path|auto|none>]
  [--cognitive <auto|required|off>]
  [--reviewer <target>]...
  [--review-policy <best-effort|required>]
  [standards-options]
  [--strict]

specmd inspect [input]
  [--profile <auto|core|optional>]
  [--trace <path|auto|none>]
  [--cognitive <auto|required|off>]
  [--reviewer <target>]...
  [--review-policy <best-effort|required>]
  [standards-options]

specmd render [input]
  [--render-format <html|pdf>]
  [--output <path>]
  [--include-human-only]
  [--force]

specmd test [input]
  [--trace <path|auto|none>]
  [--export <path>]
  [--cognitive <auto|required|off>]
  [--reviewer <target>]...
  [--review-policy <best-effort|required>]
  [standards-options]
  [--run-integration <name>]

specmd blackbox [input]
  [--trace <path|auto|none>]
  [--export <path>]
  [--cognitive <auto|required|off>]
  [--reviewer <target>]...
  [--review-policy <best-effort|required>]
  [standards-options]

specmd trace create [input]
  [--output <path>]
  [--enable-optional]
  [--cognitive <auto|required|off>]
  [--reviewer <target>]...
  [--review-policy <best-effort|required>]
  [standards-options]
  [--force]

specmd trace update [input]
  [--trace <path>]
  [--cognitive <auto|required|off>]
  [--reviewer <target>]...
  [--review-policy <best-effort|required>]
  [standards-options]
  [--force]

specmd adapt <target> [input]
  [--output <path>]
  [--install]
  [--cognitive <auto|required|off>]
  [standards-options]
  [--force]

specmd capabilities

specmd help [topic]
  [--search <text>]
  [--all]

specmd standards list
  [--repository <uri|alias>]
  [--channel <stable|prerelease|all>]
  [--offline]

specmd standards show <core|optional> <latest|version>
  [--repository <uri|alias>]
  [--standards-dir <path>]
  [--offline]

specmd standards fetch
  --core-version <latest|version>
  [--optional-version <none|matching|latest|version>]
  [--repository <uri|alias>]
  [--standards-dir <path>]
  [--force]

specmd standards verify
  [--standards-dir <path>]
  [--core-document <path>]
  [--optional-document <path>]

specmd cucumber export [input]
  [--trace <path|auto|none>]
  [--output <path>]
  [--cognitive <auto|required|off>]
  [--reviewer <target>]...
  [--review-policy <best-effort|required>]
  [--force]

specmd cucumber validate <feature>...
  [--runtime <auto|js|jvm|ruby|godog|custom>]
  [--step-definitions <path>]...
  [--timeout <duration>]

specmd cucumber run <feature>...
  --runtime <js|jvm|ruby|godog|custom>
  [--step-definitions <path>]...
  [--report <path>]
  [--report-format <messages|json|junit>]
  [--timeout <duration>]
  [--working-dir <path>]

specmd cucumber import <report> [input]
  [--trace <path|auto|none>]
  [--report-format <auto|messages|json|junit>]
  [--update-trace]
  [--force]

specmd cucumber capabilities
```

## 4. Global Options

| Option | Meaning |
|---|---|
| `--output-format <text|json>` | Select human-readable text or the JSON envelope. Default: `text`. |
| `--quiet` | Suppress non-error human-facing output; invalid with JSON mode. |
| `--no-color` | Disable terminal color. Color MUST never appear in JSON. |
| `--cwd <path>` | Resolve default and relative input/output paths from this directory. |
| `--config <path>` | Use an explicitly selected configuration file. |
| `--help` | Show help for the selected command or root command. |
| `--version` | Show the tool version and exit. |

- **ICD-GEN-001:** Unknown commands, options, or enum values MUST be rejected as usage errors.
- **ICD-GEN-002:** An option that would be ignored MUST be rejected unless the option is explicitly documented as universally safe to ignore.
- **ICD-GEN-003:** `-` MUST mean standard input only for options or positions that explicitly advertise `<path|->`.
- **ICD-GEN-004:** A command MUST NOT prompt when `--non-interactive` is set or when standard input is not an interactive terminal.
- **ICD-GEN-005:** In non-interactive mode, missing material input MUST produce a documented failure rather than a guessed value.

### 4.1 Standards Source Options

The `standards-options` production applies only to commands that resolve SPEC.md Core or Optional standards. Exact semantics and trust requirements are defined by `SPECMD_HELP_AND_SOURCES.md`.

The default standards source is `auto`. Existing Root Specifications still require their declared exact standards versions under every source mode.

- **ICD-SRC-001:** `--standards-source auto` MUST prefer explicit documents, then `--standards-dir`, then a verified local cache, and MAY use a configured repository only when local resolution fails and `--offline` is absent.
- **ICD-SRC-002:** `--standards-source local` MUST prohibit repository access and require resolution from explicit documents, `--standards-dir`, or verified cache.
- **ICD-SRC-003:** `--standards-source repository` MUST require an explicit or trusted configured repository and MUST resolve an exact release before use.
- **ICD-SRC-004:** `--core-document` and `--optional-document` MUST select those exact local files and take precedence over directory, cache, or repository candidates for their respective standards.
- **ICD-SRC-005:** `--offline` MUST prevent network access and MUST fail with exit status `4` when the required exact version is not locally resolvable.
- **ICD-SRC-006:** Mutually incompatible source options MUST be rejected with exit status `2`; an option MUST NOT be silently ignored.
- **ICD-SRC-007:** Analytical results MUST report each resolved standard's kind, exact version, source class, path or repository identity, and verified integrity status.

## 5. Common Input Resolution

- **ICD-IN-001:** An explicit input path MUST take precedence over every default.
- **ICD-IN-002:** Without an explicit input path, the default Root Specification path MUST be `SPEC.md` under the effective current directory.
- **ICD-IN-003:** If the default does not exist, the command MUST fail with exit status `3` and identify the need for an explicit path.
- **ICD-IN-004:** The tool MUST NOT select another Markdown file by filename similarity or directory scan.
- **ICD-IN-005:** A Root Specification filename other than `SPEC.md` MUST receive identical processing when explicitly selected.
- **ICD-IN-006:** Every reported path MUST be unambiguous and SHOULD be relative to the effective current directory when that representation is unique.

## 6. Common Output and Write Behavior

- **ICD-OUT-001:** A command that creates or changes a file MUST identify every intended output path before an interactive replacement.
- **ICD-OUT-002:** Without `--force` or an equivalent explicit authorization, an existing destination MUST remain unchanged.
- **ICD-OUT-003:** `--force` authorizes replacement only for destinations explicitly selected by that invocation.
- **ICD-OUT-004:** Safe replacement SHOULD be atomic where the underlying environment permits it.
- **ICD-OUT-005:** A failed write MUST identify whether the destination is absent, preserved, replaced, or potentially incomplete.
- **ICD-OUT-006:** Analytical commands MUST NOT alter the Root Specification, Normative Modules, Trace Document, configuration, or adapters.

## 7. Cognitive Option

| Value | Required behavior |
|---|---|
| `off` | Run deterministic capabilities only and report semantic limitations. |
| `auto` | Use an available configured cognitive mode; otherwise complete deterministic work and report omitted cognitive analysis. |
| `required` | Require a configured cognitive mode; if unavailable or incomplete, preserve deterministic results and return exit status `4`. |

The default is `auto` for `init`, `inspect`, `blackbox`, `trace create`, and `trace update`; `off` for `validate`, `render`, and `capabilities`; and `off` for `test` unless cognitive scenario analysis is explicitly requested.

- **ICD-COG-001:** Cognitive findings MUST be labeled heuristic.
- **ICD-COG-002:** An operation MUST report the cognitive mode requested and the mode actually used.
- **ICD-COG-003:** A Cognitive Provider MUST NOT be invoked by commands whose effective mode is `off`.

### 7.1 Additional Reviewer Options

`--reviewer <target>` is repeatable and selects additional configured Reviewer Agent connectors. It is supported by `validate`, `inspect`, `blackbox`, `test`, `trace create`, and `trace update`. No additional reviewer is selected by default.

| `--review-policy` value | Required behavior |
|---|---|
| `best-effort` | Continue when a reviewer is unavailable or incomplete, preserve completed results, and report each failure. This is the default. |
| `required` | Require every selected reviewer to complete with a valid response; otherwise preserve completed results and return exit status `4`. |

- **ICD-REV-001:** Each reviewer target MUST be resolved exactly against configured connectors and capability discovery; duplicate target values in one invocation MUST be rejected with exit status `2`.
- **ICD-REV-002:** `--review-policy` without at least one `--reviewer` MUST be rejected with exit status `2`.
- **ICD-REV-003:** Reviewer options combined with effective cognitive mode `off` MUST be rejected with exit status `2` because they would otherwise be ignored.
- **ICD-REV-004:** Selecting reviewers MUST NOT authorize remote transmission, writes, patch application, or implementation-test execution beyond authorization independently supplied for those actions.
- **ICD-REV-005:** Reviewers SHOULD be dispatched independently and MAY run concurrently, but output semantics MUST NOT depend on completion order.
- **ICD-REV-006:** Under `best-effort`, reviewer failure alone MUST NOT change a successful deterministic result to `failed`; the result MUST identify incomplete review coverage.
- **ICD-REV-007:** Under `required`, any unavailable, timed-out, invalid, or incomplete selected reviewer MUST make the cognitive result incomplete and return exit status `4`.
- **ICD-REV-008:** Human-readable and JSON output MUST identify requested, completed, and failed reviewers and preserve finding origins and material disagreements.

### 7.2 Host-Agent Cognitive Input

Host-Agent Mode (SPECMD_AGENT_INTEGRATIONS.md COG-001) needs no configured Cognitive Provider and makes no outbound network call: the coding agent already invoking the tool supplies semantic analysis directly. A command that offers a `cognitive_package` (currently `blackbox`) accepts that analysis back via `--cognitive-input <path|->` (a JSON file, or `-` for standard input) on the CLI, or the `cognitive_input` argument (an inline object) on a structured tool interface such as MCP.

- **ICD-HOSTIN-001:** `--cognitive-input`/`cognitive_input` MUST be rejected with exit status `2` when combined with effective cognitive mode `off`, for the same reason `--reviewer` is (ICD-REV-003): it would otherwise be ignored.
- **ICD-HOSTIN-002:** A malformed payload (invalid JSON, wrong top-level type, or a missing required field on an entry) MUST be rejected with exit status `2` and MUST NOT be partially applied.
- **ICD-HOSTIN-003:** A well-formed entry that cites an identifier (e.g. a requirement ID) the tool cannot verify against material it already extracted deterministically MUST have that specific citation dropped and reported; the rest of the entry MUST be preserved (mirrors PROV-009: a partial problem must not erase results that are still good).
- **ICD-HOSTIN-004:** When accepted, the JSON `cognitive` block's `used` value MUST read `host-agent`, distinguishing it from Direct-Provider Mode's provider-identifying values (PROV-007) and from `none`.
- **ICD-HOSTIN-005:** `complete` MUST reflect whether the supplied analysis covers every element the tool identified as needing it; under `--cognitive required`, incomplete coverage MUST return exit status `4` (COG-009), listing what remains uncovered.

## 8. Command Contracts

### 8.1 `init`

- Default output: `SPEC.md`.
- Default profile: `core`.
- `--profile optional` requires at least one `--feature` in non-interactive mode.
- `--input-json` supplies author decisions as structured input; `-` reads it from standard input.
- `--optional-version` is invalid under the Core-only profile.
- `--feature` is invalid under the Core-only profile.
- A generated specification starts at `spec_version: "0.1.0"` unless structured input explicitly establishes an existing versioned design.

### 8.2 `validate`

- Default input: `SPEC.md`.
- Default profile: `auto`.
- Default trace mode: `auto`.
- `--strict` promotes warnings to a non-successful command result but MUST NOT reclassify warnings as deterministic conformance errors.
- Text and JSON output MUST report specification, trace, pair, deterministic, and cognitive results when applicable.

### 8.3 `inspect`

- Inspection is read-only.
- Trace inspection follows the same `auto`, explicit path, and `none` semantics as validation.
- Output MUST distinguish measurements, deterministic findings, and cognitive findings.

### 8.4 `render`

- Default render format: `html`.
- Default output: the input basename plus `.html` or `.pdf`.
- HTML support is required. PDF support is conditional until advertised by `specmd capabilities`; selecting PDF when unavailable MUST return exit status `4`.
- `--include-human-only` is permitted only for a clearly labeled editorial rendering and MUST NOT be used for implementation-facing output.
- Rendering MUST NOT invoke a Cognitive Provider.

### 8.5 `test`

- Without `--run-integration`, the command evaluates specification verification coverage and MUST NOT execute implementation code.
- `--run-integration` requires an explicitly configured integration and authorization applicable to that invocation.
- Exported plans MUST distinguish planned checks from executed evidence.

### 8.6 `trace create`

- Default Trace Document output: `TRACE.md` beside the Root Specification.
- The generated Trace Document MUST bind `traces_file` and `traces_spec` to the exact Root Specification.
- `--enable-optional` explicitly authorizes the required Optional declaration and specification-version update before trace generation.
- Cognitive reasoning MAY propose logical relationships but MUST NOT invent implementation or executed-evidence references.

### 8.7 `trace update`

- Default Trace Document: `TRACE.md` beside the Root Specification.
- Update MUST retain manual information associated with unchanged IDs.
- Removed or changed IDs MUST be surfaced for review rather than silently deleted.
- A successful update MUST run pair validation.

### 8.8 `adapt`

- `<target>` is required and MUST be resolved exactly.
- Generation does not imply installation.
- `--install` explicitly authorizes installation to the target's documented paths.
- `--force` does not broaden authorization beyond those paths.

### 8.9 `capabilities`

The command is read-only, requires no Specification Set, and MUST support JSON. It MUST report:

- tool version;
- CLI ICD version;
- JSON schema version;
- supported Core and Optional versions;
- commands and options;
- Cognitive Provider modes;
- available configured cognitive modes without exposing credentials;
- adapter targets and adapter-format versions;
- structured tool interfaces when available;
- implementation-test integrations when available; and
- Reviewer Agent targets, connector versions, locality when known, and supported review operations.

### 8.10 `blackbox`

- Default input: `SPEC.md`.
- Default trace mode: `auto`.
- The command is read-only except for an explicitly selected `--export` destination, which follows Common Output and Write Behavior.
- Output MUST inventory specified actors, operations or interactions, triggers, inputs, outputs, externally observable errors, state effects, and constraints, and MUST identify missing or ambiguous elements.
- Deterministically extracted facts, heuristic inferences, and proposed contract additions MUST remain distinguishable.
- When TRACE is resolved, output MUST correlate relevant mappings and evidence states without treating TRACE as normative authority.
- Without TRACE, contract analysis MUST proceed and report trace, implementation-reference, and evidence coverage as unavailable.
- The command MUST NOT exercise an implementation or execute generated tests.

- **ICD-BBX-001:** `--trace` MUST accept `auto`, `none`, or an exact path and MUST follow the pair-resolution semantics used by `validate`.
- **ICD-BBX-002:** `--export` MUST produce a tool-neutral structured report and MUST NOT convert heuristic or trace-derived information into normative facts.
- **ICD-BBX-003:** Black-box output MUST represent specification completeness, trace coverage, implementation-reference completeness, and verification-evidence completeness as separate result dimensions.
- **ICD-BBX-004:** Reviewer options on `blackbox` MUST follow the Additional Reviewer Options contract and MUST preserve reviewer provenance for inferred gaps and proposed additions.
- **ICD-BBX-005:** When effective cognitive mode is not `off` and no `--cognitive-input` is supplied, output MUST include a bounded `cognitive_package` (Section 7.2) built from the resolved Root Specification's own material, never the whole repository.

### 8.11 `cucumber`

The `cucumber` family is an optional, separately discoverable integration governed by `SPECMD_CUCUMBER_CONNECTOR.md`. If the connector is unavailable, invoking this family MUST return exit status `4`. Ordinary commands MUST NOT invoke it implicitly.

- `export` derives reviewable Gherkin feature files from explicit specification behavior and acceptance examples; cognitive or reviewer additions remain proposals.
- `validate` checks Gherkin syntax and, when a runtime and step-definition paths are supplied, binding completeness without executing scenario bodies.
- `run` invokes only an explicitly configured external Cucumber runtime and MAY execute project code through step definitions.
- `import` normalizes a previously produced report; it is read-only unless `--update-trace` explicitly authorizes a safe Trace Document evidence update.
- `capabilities` reports connector and runtime availability without loading or launching a runtime.

- **ICD-CUKE-001:** The subcommand and every runtime target MUST be resolved exactly; unsupported or unavailable values MUST NOT be substituted.
- **ICD-CUKE-002:** `export` MUST follow common input, cognitive, reviewer, trace-resolution, output, and safe-write rules.
- **ICD-CUKE-003:** `validate` MUST NOT execute scenario bodies, application code, hooks, or external test suites.
- **ICD-CUKE-004:** Only the exact `run` subcommand MAY launch a Cucumber runtime; no SPEC.md, TRACE.md, feature-file content, configuration discovery, or other `specmd` command may cause it implicitly.
- **ICD-CUKE-005:** Runtime executables, working directories, step-definition paths, environment exposure, time limits, and report paths MUST come from explicit arguments or trusted configuration, never executable text found in a specification or Trace Document.
- **ICD-CUKE-006:** A scenario failure MUST return exit status `1`; unavailable runtime capability MUST return `4`; unsafe or unauthorized execution MUST return `5`; all available normalized findings MUST be preserved.
- **ICD-CUKE-007:** `import --update-trace` MUST require a resolved Trace Pair, exact scenario-to-requirement identifiers, and replacement authorization, and MUST run pair validation after the update.
- **ICD-CUKE-008:** `cucumber` JSON output MUST use the common envelope and distinguish export, syntax, binding, execution, import, and trace-update results.
- **ICD-CUKE-009:** Help and capability output MUST state that Cucumber and project step definitions are external dependencies and that `run` may execute arbitrary project-controlled code.
- **ICD-CUKE-010:** The connector MUST provide cancellation and configurable time limits for external runtime processes and MUST report whether a terminated process may have produced incomplete artifacts.

### 8.12 `help`

- The command is read-only, requires no Specification Set, and MUST support text and JSON output.
- `specmd --help` without a selected command MUST be equivalent to `specmd help` in information content.
- `specmd <command> --help` MUST be equivalent to `specmd help <command>` in information content.
- `--search` filters help entries by documented terms; `--all` includes optional and unavailable capabilities.

- **ICD-HELP-001:** Help MUST identify command syntax, option applicability, defaults, side effects, network behavior, execution behavior, exit statuses, and whether a capability is required, optional, installed, or unavailable.
- **ICD-HELP-002:** Help MUST be generated from or verified against the same command and capability metadata used by parsing and capability discovery.
- **ICD-HELP-003:** Help MUST NOT read a Specification Set, access a repository or network, invoke a Cognitive Provider, load Cucumber, or modify files.
- **ICD-HELP-004:** An unknown topic MUST return exit status `2`, identify the unknown value, and list or suggest only existing topics without silently selecting one.
- **ICD-HELP-005:** Examples MUST use explicit placeholders and MUST distinguish read-only commands from commands that may write, fetch, or execute code.
- **ICD-HELP-006:** JSON help MUST use the common envelope and expose structured commands, subcommands, options, topics, availability, and safety characteristics.

### 8.13 `standards`

The `standards` family is read-only except `fetch`, which writes only to its selected standards directory or cache and follows safe-write rules.

- `list` enumerates available exact versions from the selected repository or local verified cache.
- `show` resolves and displays one exact version; `latest` is resolved and reported as an exact version.
- `fetch` retrieves exact standards artifacts into a local standards directory or cache.
- `verify` validates local standards metadata, version declarations, compatibility, and integrity without network access.

- **ICD-STD-001:** `list` MUST distinguish stable, prerelease, cached, and remotely available versions and MUST identify whether results may be stale under `--offline`.
- **ICD-STD-002:** `show` and `fetch` MUST accept `latest` or an exact supported version; an unavailable exact version MUST return exit status `4` and MUST NOT fall back to another version.
- **ICD-STD-003:** `latest` MUST mean the highest verified stable release available from the selected source unless a different channel is explicitly selected, and the resolved exact version MUST be reported.
- **ICD-STD-004:** `--optional-version matching` MUST select the verified Optional release declared compatible with the exact selected Core; it MUST NOT merely assume equal version numbers.
- **ICD-STD-005:** `fetch` MUST NOT overwrite or mutate an existing cached version unless `--force` authorizes the exact destination and integrity verification succeeds before activation.
- **ICD-STD-006:** `verify` MUST accept explicit local Core and Optional files even when their filenames or containing directory are nonstandard.
- **ICD-STD-007:** Repository aliases, locations, trust roots, and cache locations MUST come from explicit arguments or trusted configuration, not from a processed Specification Set.
- **ICD-STD-008:** No `standards` subcommand may transmit a project Specification Set, TRACE.md, credentials, or human-only content to a repository.
- **ICD-STD-009:** Existing specifications MUST be resolved under their declared exact standards versions; selecting or fetching `latest` MUST NOT silently rewrite or reinterpret them.
- **ICD-STD-010:** Capability discovery MUST report supported source classes, configured repository aliases without credentials, local cache status, verification mechanisms, and offline availability.

## 9. JSON Result Envelope 1.1.0

Every JSON-mode command MUST return one object with these properties:

```json
{
  "schema_version": "1.1.0",
  "tool_version": "<semver>",
  "command": "<canonical command name>",
  "status": "succeeded | findings | indeterminate | failed",
  "inputs": {},
  "results": {},
  "findings": [],
  "writes": [],
  "cognitive": {
    "requested": "off | auto | required",
    "used": "none | host-agent | direct-provider",
    "complete": true,
    "reviewers": {
      "policy": "best-effort | required",
      "requested": [],
      "completed": [],
      "failed": []
    }
  }
}
```

- **ICD-JSON-001:** All properties shown above MUST be present; empty arrays or objects MUST be used when applicable data is absent.
- **ICD-JSON-002:** `findings` MUST contain objects with `rule_id`, `severity`, `evidence_type`, `message`, `reviewers`, and nullable `file`, `line`, and `column`; `reviewers` MUST be an array of originating reviewer identities and MUST be empty for findings without reviewer origin.
- **ICD-JSON-003:** `severity` MUST be `error`, `warning`, or `information`.
- **ICD-JSON-004:** `evidence_type` MUST be `deterministic` or `heuristic`.
- **ICD-JSON-005:** `writes` MUST identify intended and completed file changes without including file content unless explicitly requested.
- **ICD-JSON-006:** Additional properties MAY be added compatibly within schema major version 1; existing property meanings MUST NOT change.
- **ICD-JSON-007:** Consumers MUST ignore unknown properties within a supported schema major version.
- **ICD-JSON-008:** Each completed or failed reviewer entry MUST identify the exact requested target, connector version when available, outcome, and available provider/model metadata; a failed entry MUST include a failure category without exposing credentials.
- **ICD-JSON-009:** Grouped findings MUST list every contributing reviewer, and material reviewer disagreement MUST be represented without discarding either conclusion.

## 10. Exit Status Contract

| Status | Meaning |
|---:|---|
| `0` | Requested operation succeeded with no policy-failing findings. |
| `1` | Operation completed, but conformance, alignment, strict-warning, or configured policy findings make the result non-successful. |
| `2` | Invalid command usage or unsupported option/value combination. |
| `3` | Input, parsing, path-resolution, or required local-artifact failure. |
| `4` | Required Core, Optional, Cognitive Provider, adapter target, or other declared capability is unavailable or incompatible. |
| `5` | Write was not authorized, conflicted, or could not be completed safely. |
| `6` | Unexpected internal failure. |

- **ICD-EXIT-001:** Exit status and JSON `status` MUST be consistent.
- **ICD-EXIT-002:** A Trace Pair result of `misaligned` MUST return `1`; `indeterminate` caused by unavailable declared material MUST return `3` or `4` according to the unavailable item.
- **ICD-EXIT-003:** Multiple failures MUST return the most specific status representing the operation's primary failure; every detected failure MUST remain in `findings`.
- **ICD-EXIT-004:** Exit statuses `7` through `63` are reserved for future specification use.

## 11. Compatibility and Versioning

- **ICD-COMP-001:** The CLI ICD, JSON schema, adapter formats, and tool release MUST be independently versioned.
- **ICD-COMP-002:** A breaking command grammar, option semantic, JSON meaning, or exit-status change requires a new major CLI ICD or JSON schema version as applicable.
- **ICD-COMP-003:** New optional commands, options, findings, or JSON properties MAY be added in a minor compatible revision.
- **ICD-COMP-004:** Help and capability output MUST identify deprecated commands or options before removal in a later major version.

## 12. Verification and Acceptance

- **CLIACC-001 — ICD-GEN-001/002:** Given an unknown option and an inapplicable known option, when each is invoked, then each is rejected with exit status `2` and a specific diagnostic.
- **CLIACC-002 — ICD-IN-001/002/003/004/005:** Given `spec_web.md` exists but `SPEC.md` does not, when validation runs without input, then it returns `3`; when `spec_web.md` is explicit, it is processed normally.
- **CLIACC-003 — ICD-OUT-001/002/003/004:** Given an existing output without replacement authorization, when a write command runs, then it returns `5` and preserves the existing file.
- **CLIACC-004 — ICD-COG-001/002/003:** Given cognitive mode `off`, when inspection runs, then no provider is invoked and semantic limitations are reported distinctly from deterministic results.
- **CLIACC-005 — ICD-JSON-001/002/003/004/005:** Given JSON mode, when any command completes, then stdout contains exactly one valid envelope and findings identify severity and evidence type.
- **CLIACC-006 — ICD-EXIT-001/002/003:** Given a misaligned Trace Pair, when validation completes, then it returns `1`, reports `misaligned`, and preserves all findings.
- **CLIACC-007 — ICD-COMP-001/002:** Given a consumer supporting JSON schema 1, when a future incompatible schema is selected, then invocation fails before the consumer interprets changed property meanings.
- **CLIACC-008 — ICD-REV-001/002/003:** Given duplicate reviewers, a policy without a reviewer, or reviewers with cognitive mode off, when invoked, then the CLI rejects the combination with exit status `2` and a specific diagnostic.
- **CLIACC-009 — ICD-REV-004/005/008:** Given two selected reviewers return in different orders with overlapping and conflicting findings, when results are produced, then no extra authority is granted, aggregation is order-independent, all origins are preserved, and disagreement is visible.
- **CLIACC-010 — ICD-REV-006/007, ICD-JSON-008/009:** Given one of two selected reviewers fails, when each review policy is exercised, then completed findings remain present, reviewer status is structured, best-effort reports incomplete coverage without failing solely for that reviewer, and required returns `4`.
- **CLIACC-011 — ICD-BBX-001/002/003/004:** Given a Specification Set with incomplete interface definitions and an optional partially populated Trace Document, when black-box analysis runs with and without TRACE and additional reviewers, then the report preserves normative authority, separates all four completeness dimensions, retains reviewer provenance, and does not execute the implementation.
- **CLIACC-012 — ICD-CUKE-001/003/004/005/009:** Given an installed connector and feature files containing executable-looking text, when ordinary commands or `cucumber validate` run, then no scenario body executes; only an explicitly configured `cucumber run` may launch the disclosed runtime and project step definitions.
- **CLIACC-013 — ICD-CUKE-002/008:** Given explicit acceptance examples and reviewer-proposed additions, when `cucumber export` runs in JSON mode, then the feature output preserves requirement identity, proposals remain distinguishable, and the result uses the common envelope.
- **CLIACC-014 — ICD-CUKE-006/010:** Given a missing runtime, a failing scenario, and a timed-out runtime in separate invocations, when `cucumber run` executes, then each receives its specified exit status, completed findings are retained, the process is cancellable, and incomplete artifacts are identified.
- **CLIACC-015 — ICD-CUKE-007/008:** Given an execution report with exact requirement identifiers and an aligned Trace Pair, when import runs with and without authorized trace update, then the report is normalized in both cases, only the authorized invocation changes TRACE, and pair validation follows that change.
- **CLIACC-016 — ICD-HELP-001/002/003/004/005/006:** Given root, command, unknown-topic, and JSON help requests, when help runs offline, then syntax and safety metadata match parser capabilities, no external or project resource is accessed, unknown input is rejected, and structured output is complete.
- **CLIACC-017 — ICD-SRC-001/002/003/004/005/006/007:** Given explicit local files, a standards directory, a verified cache, and a configured repository, when each source mode is selected, then precedence and offline behavior are exact, conflicts are rejected, and the resolved source is reported.
- **CLIACC-018 — ICD-STD-001/002/003/004:** Given stable, prerelease, cached, latest, matching Optional, and unavailable historical releases, when list, show, and fetch run, then categories and exact resolutions are reported and no fallback occurs.
- **CLIACC-019 — ICD-STD-005/006/007/008:** Given custom-named local standards files, an occupied cache destination, and repository configuration, when verify and fetch run, then local files verify by content, overwrite protection holds, configuration remains trusted, and project content is not transmitted.
- **CLIACC-020 — ICD-STD-009/010:** Given an existing Root Specification declares an earlier Core version while the repository advertises a newer release, when validation and capability discovery run, then the earlier exact version is used and available source capabilities are reported without reinterpretation.

## 13. Notes

This ICD specifies behavior, not the implementation language or command-parser library. Long and short option aliases beyond those defined here are implementation freedom, but documented aliases become part of the implementation's compatibility surface.
