"""Parse Markdown cheatsheet files into entries.

A notes folder holds one ``*.md`` file per topic (``git.md`` is topic ``git``).
Inside a file, every ``## heading`` starts an entry. An entry's commands are its
fenced code blocks and any line made only of inline code (`` `like this` ``).
Everything else under the heading is kept as free-text notes.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HEADING = re.compile(r"^##\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*```")
INLINE_ONLY = re.compile(r"^\s*`([^`]+)`\s*$")


@dataclass
class Entry:
    topic: str
    title: str
    path: Path
    line: int
    commands: list[str] = field(default_factory=list)
    notes: str = ""


def warn(message: str) -> None:
    print(f"crib: warning: {message}", file=sys.stderr)


def parse_text(text: str, topic: str, path: Path) -> list[Entry]:
    """Split one Markdown file's text into entries.

    CRLF line endings and a leading UTF-8 byte order mark are accepted.
    """
    text = text.removeprefix("\ufeff")
    entries: list[Entry] = []
    current: Entry | None = None
    note_lines: list[str] = []
    block: list[str] | None = None

    def finish() -> None:
        if current is not None:
            current.notes = "\n".join(note_lines).strip()
            entries.append(current)

    for number, line in enumerate(text.splitlines(), start=1):
        if block is not None:
            if FENCE.match(line):
                if current is not None and block:
                    current.commands.append("\n".join(block))
                block = None
            else:
                block.append(line)
            continue

        if FENCE.match(line):
            block = []
            continue

        heading = HEADING.match(line)
        if heading:
            finish()
            current = Entry(topic=topic, title=heading.group(1), path=path, line=number)
            note_lines = []
            continue

        if current is None:
            continue

        inline = INLINE_ONLY.match(line)
        if inline:
            current.commands.append(inline.group(1).strip())
        else:
            note_lines.append(line)

    if block and current is not None:
        current.commands.append("\n".join(block))
    finish()
    return entries


def load_dir(notes_dir: Path) -> list[Entry]:
    """Parse every ``*.md`` file directly inside ``notes_dir``, sorted by name.

    A file that is not valid UTF-8 is skipped with a warning on stderr.
    """
    entries: list[Entry] = []
    for path in sorted(notes_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            warn(f"skipping {path}: not valid UTF-8")
            continue
        entries.extend(parse_text(text, path.stem, path))
    return entries
