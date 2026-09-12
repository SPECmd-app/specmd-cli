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
- `specmd blackbox` — read-only Black-Box Contract inventory. Structural
  checks (interface-section inventory, named interface-element inventory,
  actor<->operation cross-reference) are fully deterministic.
  `--cognitive off|auto|required` (default `auto`, per the CLI ICD) is
  negotiated the same way `validate`/`inspect` do. The two genuinely
  semantic checks (interface I/O facilitation drafting, requirements
  <->interface cross-mapping) run via **Host-Agent Mode** (COG-001,
  [SPECMD_CLI_ICD.md](SPECMD_CLI_ICD.md) section 7.2) — no Direct-Provider
  Mode exists in this build (no credentials, no outbound network call
  anywhere on the path), so instead a call with no `--cognitive-input`
  returns a bounded `cognitive_package`; the calling agent reasons over it
  and resupplies the command with `--cognitive-input` (a file path, or `-`
  for stdin) or the `cognitive_input` MCP argument. Every requirement-ID
  citation in that
  input is checked against IDs this tool already extracted deterministically
  — an unrecognized citation is dropped and reported (never silently
  trusted), and the rest of the entry is kept. `--export` writes a JSON
  report.
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
- Deterministic-Only Mode by default (`--cognitive off|auto|required` is
  negotiated truthfully); `blackbox` additionally supports **Host-Agent
  Mode** (no Direct-Provider Mode or Reviewer Agent is implemented).

**Known gaps, disclosed rather than silently claimed:**
- `specmd --help`/`-h` is still argparse's native (low-fidelity) output; it
  is *not* made equivalent in information content to `specmd help` (the ICD
  text calls for that equivalence). Use `specmd help` for the real thing.
- `specmd help`'s per-command detail doesn't print a full command-syntax
  grammar line or example invocations (HELP-001/HELP-005) — it lists
  options/defaults/safety markers instead.
- `blackbox`'s deterministic checks are ID-, section-presence-, named-
  interface-element-, and actor-mention-level, not a full
  trigger/input/output/error/state-effect extraction. The actor-mention
  check only recognizes one convention (`- **Name**: ...`/`- **Name** —
  ...`) and, being text matching rather than semantic understanding, cannot
  tell a person/system actor from a same-convention data entity — its
  findings say so explicitly and are reported at `information` severity
  rather than asserted as a confident gap. The two checks that need real
  semantic understanding (interface I/O facilitation drafting,
  requirements<->interface cross-mapping) run only when the calling agent
  supplies `--cognitive-input` (Host-Agent Mode); without it, a call
  returns a `cognitive_package` and reports the checks as not yet
  performed rather than fabricating a result. Citation-verification is
  mechanical (ID must exist in what was already extracted deterministically)
  — it cannot verify that the reasoning *content* itself is correct, only
  that it isn't inventing IDs. The `cognitive_package` also excludes
  Normative Module content (root spec only), which it discloses in-band
  rather than silently omitting.

Not implemented at all (left `TBD`/unclaimed in [TRACE.md](TRACE.md), not
silently assumed): `standards fetch` and any network access, the Cucumber
connector family, Direct-Provider Mode (`PROV-001..009`: no credentials, no
outbound network call anywhere in this build), and Reviewer Agents.
Host-Agent Mode is implemented for `blackbox` only.

## Core/Optional profile: reconciled against the authoritative standard

The Specification Set this tool implements declares conformance to **SPEC.md
Core 0.4.2** and **Optional 0.4.2**. The structural rules this build
validates against were originally *reconstructed* from a single exemplar
(this tool's own `SPEC.md`), because the package this project was built from
did not include the authoritative standard text.

That gap has since been closed. The authoritative standard is published at
[`SPECmd-app/SPEC.md`](https://github.com/SPECmd-app/SPEC.md)'s
[`docs/standard/0.4.2.md`](https://github.com/SPECmd-app/SPEC.md/blob/main/docs/standard/0.4.2.md)
and
[`0.4.2-optional.md`](https://github.com/SPECmd-app/SPEC.md/blob/main/docs/standard/0.4.2-optional.md),
and [`src/specmd/core_profile.py`](src/specmd/core_profile.py) has been
reconciled against that text directly. Four real discrepancies were found
and fixed:

- **"Specification Contract" is a SHOULD, not a MUST** (Core §1) — its
  absence is now a warning, not a conformance error.
- **A missing required top-level section is now a warning, not an error**
  — Core §2 lists the eight sections as what "a conforming SPEC.md uses,"
  immediately followed by "Empty subsections MAY be omitted." Read as
  permitting a genuinely-empty section to be omitted too (a deliberate
  product decision, since the standard's wording doesn't fully settle it),
  a document missing one can still be `conforming`.
- **Module declarations can use a bare backtick-quoted path, not only a
  Markdown link** — Optional §10's own example uses `` - `spec/identity.md` ``
  with no link syntax at all. `module_resolver.py` now recognizes both forms.
- **`optional_features` is an open, extensible set, not a closed enum** —
  Optional §44 explicitly frames its feature list as a "Suggested...
  Example." An unlisted feature name is now reported as informational, not
  a warning.

One figure remains unconfirmed: the `250 lines` / `2,500 tokens` Core
compactness target appears nowhere in the authoritative Core or Optional
text, or on the standard's own site — it came from this tool's own governing
spec prose. It's kept (still plausibly accurate) but explicitly flagged as
unconfirmed (`CORE_COMPACTNESS_PROVENANCE` in `core_profile.py`), separately
from the rest of the now-reconciled profile.

Every `validate`/`inspect`/`trace create` result still cites
`core_profile.PROFILE_PROVENANCE` explicitly, so this claim is checkable
rather than taken on faith.

## License

[Apache-2.0](LICENSE)

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
