"""The `vault` command: note-size hook, card mover, stream sweep and hygiene check."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import hook, hygiene, sweep, sync
from .board import Repo, VaultError, find_root, find_vault, load_config, move_and_push, prepare


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vault", description=__doc__)
    parser.add_argument("--vault", type=Path, default=None, help="vault root (default: found from cwd)")
    commands = parser.add_subparsers(dest="command", required=True)

    gate = commands.add_parser("hook", help="the pre-commit note-size gate")
    gate.add_argument("action", choices=("install", "check"))
    gate.add_argument("--force", action="store_true", help="replace an existing pre-commit hook")

    mover = commands.add_parser("move", help="move one card into another column and push")
    mover.add_argument("card")
    mover.add_argument("column")
    mover.add_argument("--drop", action="append", default=[], metavar="TAG", help="tag to drop")

    stream = commands.add_parser("sweep", help="promote or delete a merged stream")
    stream.add_argument("stream")
    stream.add_argument("--root", type=Path, default=None, help="root holding the canonical clones")
    phase = stream.add_mutually_exclusive_group(required=True)
    phase.add_argument("--to-promotion", action="store_true")
    phase.add_argument("--execute", action="store_true")

    syncer = commands.add_parser("sync", help="derive each stream's status from git and write it back")
    syncer.add_argument("--root", type=Path, default=None, help="root holding the canonical clones")
    syncer.add_argument("--local", action="store_true", help="offline: run hygiene only, write no status")

    clean = commands.add_parser("hygiene", help="check the root and vault for leftovers")
    clean.add_argument("--root", type=Path, default=None, help="root holding the canonical clones")
    clean.add_argument("--report-only", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        vault = (args.vault or find_vault()).resolve()
        config = load_config(vault)
        root = (getattr(args, "root", None) or find_root(vault, config)).resolve()
        if args.command == "hook":
            if args.action == "install":
                print(f"installed {hook.install(vault, args.force)}")
                return 0
            breaches = hook.staged_breaches(Repo(vault), config)
            refusals = "\n".join(f"REFUSED {breach}" for breach in breaches)
            print(refusals or "ok: no staged note grew past its cap")
            return 1 if breaches else 0
        if args.command == "move":
            repo = prepare(vault, [config.board])
            print(move_and_push(repo, config, args.card, args.column, args.drop))
            return 0
        if args.command == "sweep":
            action = sweep.to_promotion if args.to_promotion else sweep.execute
            print(action(vault, config, root, args.stream))
            return 0
        if args.command == "sync":
            report = sync.run(vault, config, root, args.local)
            for notice in report.notices:
                print(f"    note  {notice}")
            print(hygiene.render(report.rows))
            return 0
        rows = hygiene.check(vault, config, root)
        print(hygiene.render(rows))
        return 0 if args.report_only else int(hygiene.blocked(rows))
    except VaultError as error:
        print(f"vault {args.command}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
