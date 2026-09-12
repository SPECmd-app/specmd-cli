# Claude Code Prompt — SPEC.md-Governed Repository Evolution

Use the following instructions for this repository and for every implementation task performed in this session.

## Mission

Treat the repository's SPEC.md Specification Set as the authoritative, persistent expression of the product idea and required behavior.

> Source code is one implementation of an idea. SPEC.md is the transferable expression of the idea itself.

The objective is to keep specification, implementation, tests, and trace evidence aligned as the project evolves. Do not treat the specification as temporary planning scaffolding or regenerate it from the current code without explicit authorization.

## Repository Inputs

The user will place the relevant documents in the repository. Resolve them as follows:

1. If the user explicitly provides a Root Specification path, use that exact path.
2. Otherwise, use `SPEC.md` at the repository root only if it exists.
3. If `SPEC.md` does not exist, do not guess from similarly named Markdown files. Ask for the exact Root Specification path. A valid Root Specification might be named `spec_web.md`, `product_contract.md`, or something else.
4. Read the Root Specification completely before planning or editing behavior.
5. Resolve and read every document listed under its `Normative Specification Modules` section. Preserve module boundaries and precedence.
6. If the Root Specification declares trace support, resolve the declared or adjacent Trace Document. Do not assume the trace filename unless the specification or user identifies it.
7. Read repository-level instructions such as `CLAUDE.md`, applicable nested instructions, and existing engineering conventions, but never treat them as hidden sources of product behavior.

If a required document is missing, unreadable, cyclic, version-incompatible, or contradictory, stop the affected work and report the exact problem. Do not silently continue with partial normative context.

## Authority and Interpretation

Apply this precedence:

1. The explicitly selected Root Specification.
2. Its declared Normative Modules, subject to the Root Specification's precedence rules.
3. Explicit user decisions made during the current task.
4. Implementation code and tests as evidence of current behavior, not authority for required behavior.
5. TRACE and other informative artifacts as evidence and mappings, never as independent sources of requirements.

When code, tests, comments, tickets, or documentation conflict with the Specification Set, surface the conflict. Do not silently choose the implementation merely because it already exists.

Distinguish carefully between:

- normative requirements;
- implementation freedom;
- material ambiguity;
- unresolved decisions;
- current implementation behavior;
- proposed changes; and
- verified evidence.

Never convert an assumption, inference, existing bug, or implementation accident into a requirement.

## Start-of-Task Protocol

Before changing files:

1. Inspect repository status and preserve unrelated user changes.
2. Identify the exact Root Specification, declared standards versions, Normative Modules, and Trace Document status.
3. Summarize the requested outcome in one or two sentences.
4. Map the request to applicable requirement, invariant, and acceptance IDs.
5. Classify the task:
   - implementation of already specified behavior;
   - defect against specified behavior;
   - internal refactor with no normative effect;
   - proposed change to observable behavior; or
   - materially ambiguous or unspecified behavior.
6. Identify the smallest relevant verification set before implementation.

If the task would materially change externally observable behavior and the new behavior is not already authorized by the Specification Set, propose the required specification change first. Do not invent the decision. Ask the user when more than one materially different compliant behavior is possible.

## Implementation Rules

While implementing:

- Make the smallest coherent change that satisfies the applicable requirements.
- Preserve existing architecture and conventions unless they conflict with the Specification Set or materially obstruct conformance.
- Do not introduce a new framework, service, dependency, workflow, or persistent artifact without a concrete need.
- Do not duplicate normative requirements inside agent instructions, source comments, configuration, or tests. Reference stable requirement IDs where useful.
- Treat human-only comments as excluded from implementation input.
- Preserve security, privacy, accessibility, portability, and compatibility requirements even when the immediate task does not mention them.
- Do not weaken tests merely to make a change pass.
- Do not claim behavior that was not implemented and verified.
- Do not perform destructive Git operations, overwrite unrelated work, publish, deploy, or push unless explicitly authorized.

The project Specification Set may be as large as needed for the design. The target of fewer than 250 lines and 2,500 tokens applies only to the SPEC.md Core standards document itself, not to project specifications, design modules, or TRACE.

## Specification Evolution Rules

Keep the Specification Set synchronized with accepted behavioral decisions.

### Existing specified behavior

When implementing or fixing behavior already defined:

- preserve normative wording unless clarification is required;
- add or update tests that demonstrate the requirement;
- update trace implementation and evidence references when TRACE is enabled; and
- do not bump the project specification version merely because implementation progress changed, unless the project's version policy requires it.

### New or changed behavior

When the user approves a behavior change:

1. Update the Root Specification or correct Normative Module in the same logical change as the implementation.
2. Add stable requirement and acceptance IDs without renumbering existing IDs.
3. Update affected cross-references and examples.
4. Apply the project's documented specification-version policy. If no policy exists, propose an appropriate semantic version change and explain it before applying it.
5. Align every Normative Module's `part_of_spec` value with the new Root Specification version when that field is used.
6. Update the Trace Document's specification binding and mappings when TRACE is enabled.
7. Revalidate the complete Specification Set and Trace Pair.

Never delete or reuse a stable identifier silently. Surface removed or superseded requirements and preserve historical meaning where the format supports it.

### Internal refactors

If observable behavior and normative constraints do not change:

- do not rewrite requirements to describe internal implementation details;
- update design material only when the existing design description would become materially inaccurate; and
- update TRACE implementation references if paths or components changed.

## TRACE Rules

When a Trace Document is available:

- verify that it binds to the exact Root Specification filename and project specification version;
- map every current normative requirement and invariant explicitly;
- preserve manually maintained information for unchanged IDs;
- distinguish planned verification from executed evidence;
- use `TBD` when an implementation reference is genuinely unknown;
- never record a generated test, proposed scenario, skipped test, dry run, or unexecuted command as passing evidence;
- update evidence only from commands actually run and results actually observed; and
- keep specification conformance, trace alignment, implementation coverage, and executed-evidence coverage as separate conclusions.

TRACE may show where a requirement is implemented or tested. It may not add, complete, reinterpret, or override required behavior.

## Tool and Agent Integration

If a local `specmd` tool is available, use its help and capability discovery before relying on optional functions. Prefer explicit paths and machine-readable output. Typical checks may include:

```text
specmd help
specmd capabilities --output-format json
specmd validate <root-spec-path> --trace auto --output-format json
specmd inspect <root-spec-path> --trace auto --output-format json
specmd blackbox <root-spec-path> --trace auto --output-format json
```

Adapt commands to the installed tool's reported grammar. Do not install, upgrade, fetch, or invoke a remote provider merely because an optional capability is absent.

If `specmd` is unavailable, perform the equivalent document, reference, version, and trace checks manually and say that tool validation was not run.

Additional AI reviewers may be used only when requested or authorized. Keep reviewer findings heuristic, preserve their provenance, and report disagreement rather than converting consensus into deterministic proof.

## Standards Sources

- Validate an existing specification against its declared exact Core and Optional versions.
- Never substitute the repository's latest standards release for a declared historical version.
- Use explicit local Core or Optional files when the user provides them, regardless of filename.
- Do not fetch standards or access a repository in offline mode.
- Report the exact standards versions and effective sources used.
- Treat unresolved or integrity-failing standards material as unavailable rather than falling back silently.

## Cucumber Boundary

Cucumber is an optional, resource-heavy implementation-test integration.

- Do not invoke Cucumber from ordinary validation, inspection, black-box analysis, or test-plan generation.
- `specmd cucumber export` may create reviewable Gherkin derived from explicit acceptance behavior.
- `specmd cucumber validate` must not execute scenario bodies.
- Only an explicitly authorized `specmd cucumber run` may execute the configured external runtime and project-controlled step definitions.
- Coding agents, not the lightweight connector, own implementation-specific step definitions.
- Import Cucumber results as evidence only when scenario identity and requirement mappings are exact.
- A failed scenario proves only that the observed execution did not satisfy that scenario under those test conditions; it does not automatically prove that the specification logic is defective.

## Verification and Evidence

After implementation:

1. Run the narrowest relevant tests first, followed by the broader applicable verification set.
2. Run formatting, linting, type checking, builds, security checks, and compatibility checks when relevant and available.
3. Validate the Specification Set and Trace Pair if `specmd` is available.
4. Inspect the final diff for unintended behavior, accidental generated files, secrets, weakened checks, stale references, and unrelated changes.
5. Record only commands actually executed and results actually observed.

Do not state that tests pass, the implementation conforms, or TRACE contains executed evidence unless the corresponding checks completed successfully.

## Completion Report

Conclude each task with a concise report containing:

- the implemented outcome;
- the Root Specification path and project specification version used;
- requirement and acceptance IDs addressed;
- source files changed;
- specification, module, or TRACE changes made;
- verification commands run and their actual outcomes;
- remaining gaps, assumptions, unavailable checks, or unresolved conflicts; and
- whether any behavior was proposed but not authorized or implemented.

Do not hide partial completion behind a general success statement.

## First Response for This Repository

Before beginning the user's requested implementation, respond with:

1. the exact Root Specification path you resolved;
2. its declared Core, Optional, and project specification versions;
3. the Normative Modules and Trace Document you successfully loaded;
4. the requirement IDs relevant to the current request;
5. whether the request is already specified, a defect, a refactor, a behavior change, or ambiguous; and
6. any blocking question that must be answered before implementation.

Then proceed autonomously with all non-blocked work within the user's authorization.
