# specmd

A CLI for authoring, validating, inspecting, rendering, and tracing SPEC.md
documents, implemented per the Specification Set rooted at [SPEC.md](SPEC.md).

## Status: MVP subset

This is an initial, intentionally partial implementation. Implemented:

- `specmd init` — create a minimal Core or Core+Optional SPEC.md.
- `specmd validate` — structural conformance + Trace Pair validation.
- `specmd inspect` — read-only quality/measurement report.
- `specmd render` — HTML rendering (PDF is not implemented; requesting it
  returns exit status `4`).
- `specmd trace create` / `specmd trace update` — generate and reconcile
  `TRACE.md`.
- Deterministic-Only Mode (`--cognitive off|auto|required` is negotiated
  truthfully; no Cognitive Provider or Reviewer Agent is implemented).

Not implemented in this pass (left `TBD`/unclaimed in [TRACE.md](TRACE.md),
not silently assumed): `blackbox`, `test`, `adapt`, `standards`, `help`,
`capabilities`, the Cucumber connector family, an MCP/structured-tool
interface, Direct-Provider/Host-Agent cognitive modes, and Reviewer Agents.

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
