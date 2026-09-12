"""specmd CLI — argparse grammar subset (SPECMD_CLI_ICD.md section 3),
global options, dispatch, text/JSON rendering.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from specmd import __version__, exit_codes, host_agent
from specmd.cognitive import AUTO, OFF, REQUIRED, VALID_MODES
from specmd.commands import adapt as cmd_adapt
from specmd.commands import blackbox as cmd_blackbox
from specmd.commands import capabilities as cmd_capabilities
from specmd.commands import coverage as cmd_coverage
from specmd.commands import help as cmd_help
from specmd.commands import init as cmd_init
from specmd.commands import inspect as cmd_inspect
from specmd.commands import render as cmd_render
from specmd.commands import standards as cmd_standards
from specmd.commands import trace as cmd_trace
from specmd.commands import validate as cmd_validate
from specmd.resolver import InputResolutionError, display_path, resolve_root_spec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="specmd", description="Author, validate, inspect, render, and trace SPEC.md documents.")
    parser.add_argument("--version", action="version", version=f"specmd {__version__}")
    parser.add_argument("--output-format", choices=["text", "json"], default="text")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--cwd", default=None)
    parser.add_argument("--config", default=None)

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("output", nargs="?", default="SPEC.md")
    p_init.add_argument("--profile", choices=["core", "optional"], default=None)
    p_init.add_argument("--feature", action="append", default=[])
    p_init.add_argument("--input-json", default=None)
    p_init.add_argument("--non-interactive", action="store_true")
    p_init.add_argument("--force", action="store_true")

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("input", nargs="?", default=None)
    p_validate.add_argument("--profile", choices=["auto", "core", "optional"], default="auto")
    p_validate.add_argument("--trace", default="auto")
    p_validate.add_argument("--cognitive", choices=VALID_MODES, default=OFF)
    p_validate.add_argument("--strict", action="store_true")

    p_inspect = sub.add_parser("inspect")
    p_inspect.add_argument("input", nargs="?", default=None)
    p_inspect.add_argument("--profile", choices=["auto", "core", "optional"], default="auto")
    p_inspect.add_argument("--trace", default="auto")
    p_inspect.add_argument("--cognitive", choices=VALID_MODES, default=AUTO)

    p_render = sub.add_parser("render")
    p_render.add_argument("input", nargs="?", default=None)
    p_render.add_argument("--render-format", choices=["html", "pdf"], default="html")
    p_render.add_argument("--output", default=None)
    p_render.add_argument("--include-human-only", action="store_true")
    p_render.add_argument("--force", action="store_true")

    p_trace = sub.add_parser("trace")
    trace_sub = p_trace.add_subparsers(dest="trace_command", required=True)

    p_trace_create = trace_sub.add_parser("create")
    p_trace_create.add_argument("input", nargs="?", default=None)
    p_trace_create.add_argument("--output", default=None)
    p_trace_create.add_argument("--enable-optional", action="store_true")
    p_trace_create.add_argument("--cognitive", choices=VALID_MODES, default=AUTO)
    p_trace_create.add_argument("--force", action="store_true")

    p_trace_update = trace_sub.add_parser("update")
    p_trace_update.add_argument("input", nargs="?", default=None)
    p_trace_update.add_argument("--trace", default=None)
    p_trace_update.add_argument("--cognitive", choices=VALID_MODES, default=AUTO)
    p_trace_update.add_argument("--force", action="store_true")

    p_blackbox = sub.add_parser("blackbox")
    p_blackbox.add_argument("input", nargs="?", default=None)
    p_blackbox.add_argument("--trace", default="auto")
    p_blackbox.add_argument("--cognitive", choices=VALID_MODES, default=AUTO)
    p_blackbox.add_argument("--cognitive-input", default=None)
    p_blackbox.add_argument("--export", default=None)

    p_test = sub.add_parser("test")
    p_test.add_argument("input", nargs="?", default=None)
    p_test.add_argument("--trace", default="auto")
    p_test.add_argument("--export", default=None)
    p_test.add_argument("--run-integration", default=None)

    p_adapt = sub.add_parser("adapt")
    p_adapt.add_argument("target")
    p_adapt.add_argument("input", nargs="?", default=None)
    p_adapt.add_argument("--output", default=None)
    p_adapt.add_argument("--install", action="store_true")
    p_adapt.add_argument("--force", action="store_true")

    sub.add_parser("capabilities")

    p_help = sub.add_parser("help")
    p_help.add_argument("topic", nargs="?", default=None)
    p_help.add_argument("--search", default=None)
    p_help.add_argument("--all", dest="all_", action="store_true")

    p_standards = sub.add_parser("standards")
    standards_sub = p_standards.add_subparsers(dest="standards_command", required=True)

    standards_sub.add_parser("list")

    p_std_show = standards_sub.add_parser("show")
    p_std_show.add_argument("kind", choices=["core", "optional"])
    p_std_show.add_argument("version")

    p_std_verify = standards_sub.add_parser("verify")
    p_std_verify.add_argument("--core-document", default=None)
    p_std_verify.add_argument("--optional-document", default=None)

    return parser


def _print_results_summary(envelope: dict) -> None:
    """The generic findings/writes rendering below is enough for
    validate/inspect/render/trace/adapt, whose important content is in
    `findings`/`writes`. capabilities/help/standards/blackbox/test communicate
    mainly through `results`, so give those a real text summary too instead
    of only ever emitting a bare status line in text mode.
    """
    command = envelope["command"]
    r = envelope["results"]

    if command == "capabilities":
        print(f"  tool_version: {r['tool_version']}  cli_icd_version: {r['cli_icd_version']}")
        print(f"  core: {r['core_versions_supported']}  optional: {r['optional_versions_supported']}")
        for c in r["commands"]:
            mark = "available" if c["available"] else f"unavailable ({c['unavailable_reason']})"
            print(f"  - {c['name']:<18} {mark}")

    elif command == "help":
        if "unknown_topic" in r:
            print(f"  unknown topic '{r['unknown_topic']}'; did you mean: {', '.join(r['suggestions'])}")
        elif "topic" in r:
            t = r["topic"]
            print(f"  {t['name']} — {t['summary']}")
            print(f"  safety: {', '.join(t['safety'])}   exit statuses: {t['exit_statuses']}")
            for o in t["options"]:
                print(f"    {o['name']:<24} default={o['default'] or '-'}  {o['description']}")
        else:
            for t in r["topics"]:
                avail = "" if t["available"] else "  [unavailable]"
                print(f"  {t['name']:<18} {t['summary']}{avail}")

    elif command in ("standards_list", "standards_show", "standards_verify"):
        if command == "standards_list":
            for v in r["versions"]:
                print(f"  {v['kind']:<10} {v['version']:<10} source={v['source']}")
        elif command == "standards_show" and "resolved_version" in r:
            print(f"  {r['kind']} {r['resolved_version']} (source={r['source']})")
            print(f"  provenance: {r['provenance']}")
        elif command == "standards_verify" and "checks" in r:
            for c in r["checks"]:
                print(f"  {c['kind']:<10} {c['path']}: {'OK' if c['ok'] else 'MISMATCH — ' + str(c.get('reason'))}")
        if "reason" in r:
            print(f"  {r['reason']}")

    elif command == "blackbox":
        comp = r["completeness"]
        print(f"  requirement IDs: {len(r['requirement_ids'])}  acceptance IDs: {len(r['acceptance_ids'])}")
        print(f"  trace coverage available: {comp['trace_coverage']['available']}  pair_result: {comp['trace_coverage']['pair_result']}")
        print(f"  implementation-reference completeness available: {comp['implementation_reference_completeness']['available']}")
        print(f"  executed-evidence completeness available: {comp['executed_evidence_completeness']['available']}")

    elif command == "test":
        print(f"  covered: {len(r['covered_requirement_ids'])}  uncovered: {len(r['uncovered_requirement_ids'])}")
        if r["uncovered_requirement_ids"]:
            print(f"    uncovered: {', '.join(r['uncovered_requirement_ids'])}")
        if r["unreferenced_acceptance_ids"]:
            print(f"    unreferenced acceptance IDs: {', '.join(r['unreferenced_acceptance_ids'])}")

    elif command == "adapt":
        if "reason" in r:
            print(f"  {r['reason']}")
        elif "adapter_format_version" in r:
            print(f"  adapter_format_version: {r['adapter_format_version']}  included_modules: {r['included_modules']}")


def _print_text(envelope: dict, *, quiet: bool) -> None:
    if not quiet:
        print(f"specmd {envelope['command']}: {envelope['status']}")
        _print_results_summary(envelope)
    for finding in envelope["findings"]:
        loc = ""
        if finding.get("file"):
            loc = f" [{finding['file']}" + (f":{finding['line']}" if finding.get("line") else "") + "]"
        print(f"  {finding['severity'].upper():<5} {finding['rule_id']:<16} {finding['message']}{loc}")
    if not envelope["cognitive"]["complete"] and not quiet:
        print(f"  NOTE  cognitive analysis incomplete (requested={envelope['cognitive']['requested']})")
    for w in envelope["writes"]:
        if not quiet:
            print(f"  write: {w['action']} {w['path']}")


def _emit(envelope: dict, exit_code: int, *, output_format: str, quiet: bool) -> int:
    if output_format == "json":
        sys.stdout.write(json.dumps(envelope, indent=2) + "\n")
    else:
        _print_text(envelope, quiet=quiet)
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()

    if args.command == "init":
        output_path = (cwd / args.output) if not Path(args.output).is_absolute() else Path(args.output)
        profile = args.profile or "core"
        input_json = None
        try:
            if args.input_json:
                stdin_text = sys.stdin.read() if args.input_json == "-" else None
                input_json = cmd_init.load_input_json(args.input_json, stdin_text)
            envelope, code = cmd_init.run(
                output_path=output_path, profile=profile, features=args.feature, input_json=input_json, force=args.force
            )
        except cmd_init.InitUsageError as exc:
            print(f"usage error: {exc}", file=sys.stderr)
            return exit_codes.USAGE_ERROR
        return _emit(envelope, code, output_format=args.output_format, quiet=args.quiet)

    if args.command in ("validate", "inspect", "render", "blackbox", "test"):
        try:
            resolved = resolve_root_spec(args.input, cwd)
        except InputResolutionError as exc:
            print(str(exc), file=sys.stderr)
            return exit_codes.INPUT_ERROR
        set_root = resolved.path.parent
        disp = display_path(resolved.path, cwd)

        if args.command == "validate":
            envelope, code = cmd_validate.run(
                root_spec_path=resolved.path,
                set_root=set_root,
                display_path=disp,
                profile=args.profile,
                trace_mode=args.trace,
                cognitive_mode=args.cognitive,
                strict=args.strict,
            )
        elif args.command == "inspect":
            envelope, code = cmd_inspect.run(
                root_spec_path=resolved.path,
                set_root=set_root,
                display_path=disp,
                profile=args.profile,
                trace_mode=args.trace,
                cognitive_mode=args.cognitive,
            )
        elif args.command == "render":
            output_path = Path(args.output) if args.output else resolved.path.with_suffix(f".{args.render_format}")
            if not output_path.is_absolute():
                output_path = cwd / output_path
            envelope, code = cmd_render.run(
                root_spec_path=resolved.path,
                set_root=set_root,
                display_path=disp,
                output_path=output_path,
                render_format=args.render_format,
                include_human_only=args.include_human_only,
                force=args.force,
            )
        elif args.command == "blackbox":
            export_path = Path(args.export) if args.export else None
            if export_path and not export_path.is_absolute():
                export_path = cwd / export_path
            try:
                cognitive_input = None
                if args.cognitive_input:
                    stdin_text = sys.stdin.read() if args.cognitive_input == "-" else None
                    cognitive_input = host_agent.load_cognitive_input(args.cognitive_input, stdin_text)
                envelope, code = cmd_blackbox.run(
                    root_spec_path=resolved.path,
                    set_root=set_root,
                    display_path=disp,
                    trace_mode=args.trace,
                    cognitive_mode=args.cognitive,
                    cognitive_input=cognitive_input,
                    export_path=export_path,
                )
            except host_agent.HostAgentInputError as exc:
                print(f"usage error: {exc}", file=sys.stderr)
                return exit_codes.USAGE_ERROR
        else:  # test
            export_path = Path(args.export) if args.export else None
            if export_path and not export_path.is_absolute():
                export_path = cwd / export_path
            envelope, code = cmd_coverage.run(
                root_spec_path=resolved.path,
                set_root=set_root,
                display_path=disp,
                trace_mode=args.trace,
                export_path=export_path,
                run_integration=args.run_integration,
            )
        return _emit(envelope, code, output_format=args.output_format, quiet=args.quiet)

    if args.command == "trace":
        try:
            resolved = resolve_root_spec(args.input, cwd)
        except InputResolutionError as exc:
            print(str(exc), file=sys.stderr)
            return exit_codes.INPUT_ERROR
        set_root = resolved.path.parent
        disp = display_path(resolved.path, cwd)

        if args.trace_command == "create":
            output_path = Path(args.output) if args.output else None
            if output_path and not output_path.is_absolute():
                output_path = cwd / output_path
            envelope, code = cmd_trace.create(
                root_spec_path=resolved.path,
                set_root=set_root,
                display_path=disp,
                output_path=output_path,
                enable_optional=args.enable_optional,
                force=args.force,
            )
        else:  # update
            trace_path = Path(args.trace) if args.trace else None
            if trace_path and not trace_path.is_absolute():
                trace_path = cwd / trace_path
            envelope, code = cmd_trace.update(
                root_spec_path=resolved.path,
                set_root=set_root,
                display_path=disp,
                trace_path=trace_path,
                force=args.force,
            )
        return _emit(envelope, code, output_format=args.output_format, quiet=args.quiet)

    if args.command == "adapt":
        try:
            resolved = resolve_root_spec(args.input, cwd)
        except InputResolutionError as exc:
            print(str(exc), file=sys.stderr)
            return exit_codes.INPUT_ERROR
        set_root = resolved.path.parent
        disp = display_path(resolved.path, cwd)
        output_path = Path(args.output) if args.output else None
        if output_path and not output_path.is_absolute():
            output_path = cwd / output_path
        envelope, code = cmd_adapt.run(
            target=args.target,
            root_spec_path=resolved.path,
            set_root=set_root,
            display_path=disp,
            output_path=output_path,
            cwd=cwd,
            install=args.install,
            force=args.force,
        )
        return _emit(envelope, code, output_format=args.output_format, quiet=args.quiet)

    if args.command == "capabilities":
        envelope, code = cmd_capabilities.run()
        return _emit(envelope, code, output_format=args.output_format, quiet=args.quiet)

    if args.command == "help":
        envelope, code = cmd_help.run(topic=args.topic, search=args.search, show_all=args.all_)
        return _emit(envelope, code, output_format=args.output_format, quiet=args.quiet)

    if args.command == "standards":
        if args.standards_command == "list":
            envelope, code = cmd_standards.list_()
        elif args.standards_command == "show":
            envelope, code = cmd_standards.show(args.kind, args.version)
        else:  # verify
            core_doc = Path(args.core_document) if args.core_document else None
            optional_doc = Path(args.optional_document) if args.optional_document else None
            if core_doc and not core_doc.is_absolute():
                core_doc = cwd / core_doc
            if optional_doc and not optional_doc.is_absolute():
                optional_doc = cwd / optional_doc
            envelope, code = cmd_standards.verify(core_doc, optional_doc)
        return _emit(envelope, code, output_format=args.output_format, quiet=args.quiet)

    parser.error(f"unknown command {args.command!r}")
    return exit_codes.USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())
