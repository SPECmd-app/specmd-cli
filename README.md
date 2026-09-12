# specmd

A CLI for authoring, validating, inspecting, rendering, and tracing SPEC.md
documents, implemented per the Specification Set rooted at [SPEC.md](SPEC.md).

## Status: intentionally partial implementation

Implemented:

- `specmd init` — create a minimal Core or Core+Optional SPEC.md.
- `specmd validate` — structural conformance + Trace Pair validation, plus
  the Version Alignment Process (SPEC.md §4.14, PORT-006/007/008): an
  unresolvable declared standards version always fails as `indeterminate`
  with a proposed-spec-change remediation, never a silent substitution.
- `specmd inspect` — read-only quality/measurement report.
- `specmd render` — HTML rendering (PDF is not implemented; requesting it
  returns exit status `4`). Deliberately does **not** apply the Version
  Alignment Process — it makes no conformance claim and always displays the
  true declared version, whatever it is.
- `specmd trace create` / `specmd trace update` — generate and reconcile
  `TRACE.md`; also apply the Version Alignment Process.
- `specmd blackbox` — read-only, deterministic Black-Box Contract inventory
  (structural only — no semantic inference, since no Cognitive Provider is
  configured). `--export` writes a JSON report.
- `specmd test` — verification-coverage report (covered/uncovered
  requirement IDs, unreferenced acceptance criteria). `--export` writes a
  JSON test plan; fields that would require semantic extraction
  (preconditions/actions/expected outcomes) are `null`, never invented.
  `--run-integration` is accepted but returns exit `4` — no implementation-test
  integration is configured in this build.
- `specmd adapt <target>` — generates a thin adapter (`codex`, `claude-code`,
  `cursor`, `github-copilot`). Generation only; `--install` returns exit `4`.
- `specmd standards list|show|verify` — reports only the bundled/local
  evidence this build actually has (Core/Optional `0.4.2`); `fetch` and any
  network/repository access are **not implemented** (SPEC.md Open Issue 1,
  the canonical standards registry, is unresolved).
- `specmd capabilities` — reports tool/CLI-ICD/JSON-schema versions,
  supported standards, every command's availability, and why anything is
  unavailable.
- `specmd help [topic]` — real per-command help (syntax-light: see gap below),
  `--search`, `--all` to include unavailable capabilities. Reads the same
  static registry (`command_metadata.py`) `capabilities` does.
- `specmd-mcp` — an MCP (Model Context Protocol) stdio server exposing
  `create`/`validate`/`inspect`/`blackbox`/`trace_create`/`trace_update`/
  `validate_pair`/`propose_patch`/`capabilities` as MCP tools (MCP-001..005).
  **Hand-rolled protocol, not the official SDK**: the `mcp` PyPI package
  requires Python ≥3.10, and this build targets 3.9, so
  [`src/specmd/mcp_server.py`](src/specmd/mcp_server.py) implements the stdio
  JSON-RPC 2.0 wire protocol directly (pure stdlib, no new dependency). Every
  tool wraps the same command module the CLI uses and returns the identical
  JSON envelope. `propose_patch` is an honest stub — no patch-generation
  capability exists in this build, so it always returns an error rather than
  fabricate a diff. Run it as `specmd-mcp` (installed entry point) or
  `python -m specmd.mcp_server`.
- Deterministic-Only Mode (`--cognitive off|auto|required` is negotiated
  truthfully; no Cognitive Provider or Reviewer Agent is implemented).

**Known gaps, disclosed rather than silently claimed:**
- `specmd --help`/`-h` is still argparse's native (low-fidelity) output; it
  is *not* made equivalent in information content to `specmd help` (the ICD
  text calls for that equivalence). Use `specmd help` for the real thing.
- `specmd help`'s per-command detail doesn't print a full command-syntax
  grammar line or example invocations (HELP-001/HELP-005) — it lists
  options/defaults/safety markers instead.
- `blackbox`'s inventory is ID- and section-presence-level, not a full
  actor/trigger/input/output/error/state-effect extraction (would need
  semantic understanding this Deterministic-Only build doesn't have).

Not implemented at all (left `TBD`/unclaimed in [TRACE.md](TRACE.md), not
silently assumed): `standards fetch` and any network access, the Cucumber
connector family, Direct-Provider/Host-Agent cognitive modes, and Reviewer
Agents.

## Important caveat: reconstructed Core/Optional profile

The Specification Set this tool implements declares conformance to **SPEC.md
Core 0.4.2** and **Optional 0.4.2**, but the package it was built from did
not include the actual Core/Optional standard documents — only specmd's own
tool specification, which *uses* Core/Optional.

The structural rules this build validates against (required frontmatter
fields, the eight required section headings, human-only comment delimiter
syntax, BCP14 keyword usage, the recognized `optional_features` set) were
**reconstructed from the one exemplar available** — `SPEC.md`'s own shape —
not from the authoritative standard text. This is isolated in
[`src/specmd/core_profile.py`](src/specmd/core_profile.py) and labeled
`PROFILE_PROVENANCE`, which every `validate`/`inspect`/`trace create` result
surfaces explicitly. Treat conformance results accordingly until the real
Core/Optional documents are available to replace this reconstruction.

## Development

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pip install pytest
.venv/bin/pytest
```

```bash
.venv/bin/specmd --output-format json validate SPEC.md --trace auto
```

```bash
# MCP server: reads/writes newline-delimited JSON-RPC 2.0 on stdio.
.venv/bin/specmd-mcp
```
