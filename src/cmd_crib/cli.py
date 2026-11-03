"""Command-line entry point for ``crib``."""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

from . import __version__
from .add import add_entry
from .notes import Entry, load_dir
from .search import search


def default_notes_dir() -> Path:
    """``$CRIB_DIR``, else ``$XDG_CONFIG_HOME/crib/notes``, else ``~/.config/crib/notes``."""
    if os.environ.get("CRIB_DIR"):
        return Path(os.environ["CRIB_DIR"]).expanduser()
    config = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(config) / "crib" / "notes"


def format_entry(number: int, entry: Entry) -> str:
    lines = [f"{number}. {entry.topic} / {entry.title}  ({entry.path.name}:{entry.line})"]
    for command in entry.commands:
        lines.extend("     " + part for part in command.splitlines())
    for note in entry.notes.splitlines():
        if note.strip():
            lines.append("     # " + note.strip())
    return "\n".join(lines)


def lookup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crib",
        description="Look up commands in your Markdown cheatsheet notes.",
        epilog="Run 'crib add -h' to see how to add an entry.",
    )
    parser.add_argument("query", nargs="*", help="words that must all match")
    parser.add_argument("-t", "--topic", help="only search this topic (file name without .md)")
    parser.add_argument("-n", "--limit", type=int, default=10, metavar="N",
                        help="show at most N results (default 10, 0 for all)")
    parser.add_argument("-c", "--command", action="store_true",
                        help="print only the command(s) of the best match")
    parser.add_argument("--topics", action="store_true", help="list topics and entry counts")
    parser.add_argument("--dir", type=Path, help="notes folder (default: $CRIB_DIR or ~/.config/crib/notes)")
    parser.add_argument("--version", action="version", version=f"crib {__version__}")
    return parser


def notes_dir_or_exit(given: Path | None) -> Path:
    notes_dir = given.expanduser() if given else default_notes_dir()
    if not notes_dir.is_dir():
        sys.exit(f"crib: notes folder not found: {notes_dir}\n"
                 "Create it, set CRIB_DIR, or pass --dir.")
    return notes_dir


def run_lookup(argv: list[str]) -> int:
    args = lookup_parser().parse_args(argv)
    entries = load_dir(notes_dir_or_exit(args.dir))

    if args.topics:
        counts = Counter(e.topic for e in entries)
        width = max((len(t) for t in counts), default=0)
        for topic in sorted(counts):
            print(f"{topic:<{width}}  {counts[topic]}")
        return 0

    results = search(entries, args.query, topic=args.topic)
    if not results:
        print("crib: no matches", file=sys.stderr)
        return 1

    if args.command:
        best = results[0]
        if not best.commands:
            print(f"crib: '{best.title}' has no command", file=sys.stderr)
            return 1
        print("\n".join(best.commands))
        return 0

    shown = results if args.limit <= 0 else results[: args.limit]
    print("\n\n".join(format_entry(i, e) for i, e in enumerate(shown, start=1)))
    if len(shown) < len(results):
        print(f"\n... {len(results) - len(shown)} more, use -n 0 to see all")
    return 0


def add_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crib add",
        description="Append an entry to TOPIC.md in your notes folder.",
        epilog="Quote the command to keep its own quotes: "
               "crib add git 'Find removed line' 'git log -S \"name\" --oneline'",
    )
    parser.add_argument("topic", help="topic file to add to, without .md (created if missing)")
    parser.add_argument("title", help="the entry heading, what you'll search for later")
    parser.add_argument("command", nargs="+", help="the command; several words are joined with spaces")
    parser.add_argument("-m", "--note", help="a one-line note to keep with the command")
    parser.add_argument("--dir", type=Path, help="notes folder (default: $CRIB_DIR or ~/.config/crib/notes)")
    return parser


def run_add(argv: list[str]) -> int:
    args = add_parser().parse_args(argv)
    notes_dir = args.dir.expanduser() if args.dir else default_notes_dir()
    try:
        path, line = add_entry(notes_dir, args.topic, args.title, " ".join(args.command), args.note)
    except ValueError as exc:
        print(f"crib add: {exc}", file=sys.stderr)
        return 2
    print(f"added to {path}:{line}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "add":
        return run_add(argv[1:])
    return run_lookup(argv)


if __name__ == "__main__":
    sys.exit(main())
