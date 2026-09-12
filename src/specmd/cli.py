"""specmd CLI — argparse grammar subset (SPECMD_CLI_ICD.md section 3),
global options, dispatch, text/JSON rendering.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from specmd import __version__, exit_codes
from specmd.cognitive import AUTO, OFF, REQUIRED, VALID_MODES
from specmd.commands import init as cmd_init
from specmd.commands import inspect as cmd_inspect
from specmd.commands import render as cmd_render
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

    return parser


def _print_text(envelope: dict, *, quiet: bool) -> None:
    if not quiet:
        print(f"specmd {envelope['command']}: {envelope['status']}")
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

    if args.command in ("validate", "inspect", "render"):
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
        else:  # render
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

    parser.error(f"unknown command {args.command!r}")
    return exit_codes.USAGE_ERROR


if __name__ == "__main__":
    sys.exit(main())
