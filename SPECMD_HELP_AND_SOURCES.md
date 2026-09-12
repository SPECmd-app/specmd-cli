---
spec_module: "help-and-standards-sources"
part_of_spec: "0.11.0"
status: draft
name: "specmd Help and Standards Sources Contract"
last_updated: "2026-09-12"
---

# specmd Help and Standards Sources Contract

This document is a Normative Module of `SPEC.md` version `0.11.0`.

Uppercase **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** use BCP 14 semantics. The Root Specification controls interpretation and precedence.

## 1. Scope

This module defines discoverable help and resolution of SPEC.md Core and Optional standards from latest or historical repository releases, verified caches, standards directories, and explicit local files.

It does not define a canonical repository. Repository identity and trust policy remain deployment configuration until the Root Specification resolves that open issue.

## 2. Definitions

**Standards Repository** — an explicitly selected or trusted configured source that publishes an enumerable catalog of immutable, versioned Core and Optional artifacts plus integrity metadata.

**Exact Version** — a concrete standards version, not a mutable alias such as `latest`.

**Latest** — a selector resolved at operation time to the highest verified stable Exact Version available from the selected source.

**Standards Directory** — a user-selected local directory containing one or more versioned Core or Optional artifacts and their verification metadata when required.

**Explicit Local Document** — a Core or Optional file selected by its exact path, regardless of filename.

**Verified Cache** — local, immutable-by-version repository material whose origin and integrity have been recorded and validated.

## 3. Help Requirements

- **HELP-001:** `specmd help` MUST provide self-contained usage for every required command and every advertised optional capability.
- **HELP-002:** Root, command, subcommand, option, topic-search, and machine-readable help MUST be available without a Specification Set.
- **HELP-003:** Help MUST identify defaults, option applicability and conflicts, input resolution, output and write behavior, network access, cognitive processing, external execution, and exit statuses.
- **HELP-004:** Help MUST distinguish required built-in capabilities from optional, configured, unavailable, or externally supplied capabilities.
- **HELP-005:** Help output MUST remain available offline and MUST NOT invoke repositories, Cognitive Providers, Reviewer Agents, Cucumber runtimes, implementation-test integrations, or project hooks.
- **HELP-006:** Help examples MUST be safe to copy after replacing clearly marked placeholders and MUST visually identify commands that may write files, access a network, or execute project-controlled code.
- **HELP-007:** Help content MUST be version-aligned with the active CLI ICD and capability metadata; stale help that advertises rejected syntax is a conformance error.
- **HELP-008:** Machine-readable help MUST preserve the semantic distinctions present in text help and use a versioned schema.

## 4. Source Selection

- **SRC-001:** A command resolving standards MUST support `auto`, `repository`, and `local` source modes and MUST default to `auto`.
- **SRC-002:** Exact explicit local Core or Optional document paths MUST take precedence for their respective artifact and MUST work regardless of filename.
- **SRC-003:** A selected Standards Directory MUST be searched by declared artifact kind and Exact Version, not by filename similarity.
- **SRC-004:** A Verified Cache MAY satisfy repository or automatic resolution without network access.
- **SRC-005:** Repository access MUST use only an explicit repository or trusted configured alias and MUST report the selected repository identity without credentials.
- **SRC-006:** Offline mode MUST prohibit repository network access and MUST remain able to use explicit local documents, Standards Directories, and Verified Caches.
- **SRC-007:** Failure to resolve the required Exact Version MUST be reported as unavailable; the resolver MUST NOT substitute latest, nearest, matching-major, or any other version.
- **SRC-008:** Every consuming result MUST identify the exact version and effective source of each standards artifact used.

## 5. Latest and Historical Repository Releases

- **SRC-009:** A Standards Repository MUST expose or be adapted to a catalog that distinguishes stable, prerelease, withdrawn, and unavailable releases.
- **SRC-010:** The `latest` selector MUST resolve to an Exact Version before an artifact is parsed or generated, and that resolution MUST be recorded in output.
- **SRC-011:** An exact historical version selector MUST remain exact and MUST NOT fall forward when the requested version is absent.
- **SRC-012:** Validation of an existing Root Specification MUST use its declared Exact Version; repository `latest` is informational and MUST NOT reinterpret or rewrite the document.
- **SRC-013:** Initialization MAY select `latest` or an exact historical Core version; generated frontmatter MUST record the resolved Exact Version, never the word `latest`.
- **SRC-014:** Optional resolution MUST use declared compatibility metadata; `matching` MUST NOT assume that Core and Optional version numbers are identical.
- **SRC-015:** Withdrawn releases MAY be used only by exact selection, with a warning and repository-supplied withdrawal reason when available.

## 6. Local Copies, Caching, and Integrity

- **SRC-016:** Local Core and Optional documents MUST be validated for artifact kind, declared version, parseability, and applicable integrity policy before use.
- **SRC-017:** An explicit local document whose declared version differs from the version required by the Root Specification or command MUST be rejected, not relabeled.
- **SRC-018:** Cached repository artifacts MUST be immutable by repository identity, artifact kind, and Exact Version unless an authorized repair replaces a failed-integrity entry.
- **SRC-019:** Fetch MUST write to a user-selected Standards Directory or documented cache location and MUST obey safe-write and atomicity requirements.
- **SRC-020:** Fetch and discovery MUST NOT transmit project Specification Sets, Trace Documents, human-only content, or credentials not required to authenticate the selected repository.
- **SRC-021:** Repository content MUST be treated as untrusted until its declared version, expected artifact kind, and configured integrity or authenticity checks succeed.
- **SRC-022:** Local-only operation MUST not require repository metadata when the selected files contain sufficient version and compatibility declarations under the applicable standards.
- **SRC-023:** Result metadata SHOULD include a content digest so humans, agents, and CI can reproduce the exact standards input.

## 7. Repository and Local-Copy Operations

- **SRC-024:** `specmd standards list` MUST enumerate available Exact Versions and their channel and local/remote availability.
- **SRC-025:** `specmd standards show` MUST display the selected standards artifact and resolution metadata without changing cache or project files.
- **SRC-026:** `specmd standards fetch` MUST retrieve only the selected exact artifacts and integrity metadata; it MUST NOT install tools, adapters, dependencies, or hooks.
- **SRC-027:** `specmd standards verify` MUST verify explicitly selected files or a Standards Directory without network access.
- **SRC-028:** Standards operations MUST support machine-readable results and deterministic ordering.

## 8. Verification and Acceptance

- **HSACC-001 — HELP-001/002/003/004:** Given required, optional installed, optional unavailable, and external capabilities, when root and command help run, then syntax, defaults, safety behavior, and availability are complete and correctly distinguished.
- **HSACC-002 — HELP-005/006/007/008:** Given offline JSON and text help, when examples and command metadata are compared with the parser, then no external system is invoked, hazardous examples are marked, syntax is aligned, and both formats preserve equivalent meaning.
- **HSACC-003 — SRC-001/002/003/004/005/006/007/008:** Given explicit custom-named files, a Standards Directory, cache, and repository, when every source mode and offline mode is exercised, then precedence is exact, no filename guessing or fallback occurs, and provenance is reported.
- **HSACC-004 — SRC-009/010/011/012/013/015:** Given a repository with stable latest, prerelease, withdrawn, and earlier versions, when initialization and existing-document validation run, then latest resolves to an exact stable version, historical selection remains exact, withdrawn use warns, and existing declarations are unchanged.
- **HSACC-005 — SRC-014/015/016/017:** Given Optional compatibility metadata, a withdrawn release, and a mismatched local file, when resolution runs, then compatibility is evaluated from metadata, withdrawal is disclosed, and mismatched content is rejected.
- **HSACC-006 — SRC-018/019/020/021/023:** Given a cached artifact, occupied destination, tampered repository response, and project content, when fetch runs, then immutability and safe-write rules hold, tampering is rejected, project content is not transmitted, and reproducibility metadata is returned.
- **HSACC-007 — SRC-022/024/025/026/027/028:** Given complete local copies and no network, when list, show, fetch-to-local, verify, and consuming commands run, then local-only workflows remain usable, operations are deterministic, and no dependency or hook is installed.

## 9. Notes

“Latest” is a convenience for starting new work, not an instruction to upgrade existing specifications. A portable Specification Set records exact versions so another human or agent can resolve the same standards later.

Local copies are first-class authoritative inputs for an invocation when explicitly selected and successfully verified. Their filenames are irrelevant; their declared kind, version, compatibility, and integrity determine usability.
