"""Keyword search over parsed entries.

Every query word has to appear somewhere in the entry (title, topic, commands or
notes, case-insensitive). Where a word matches decides how high the entry ranks:
title beats topic, topic beats command, command beats notes.
"""

from __future__ import annotations

from .notes import Entry

TITLE, TOPIC, COMMAND, NOTES = 8, 4, 2, 1


def score(entry: Entry, words: list[str]) -> int:
    """Return the entry's score for ``words``, or 0 if any word is missing."""
    title = entry.title.lower()
    topic = entry.topic.lower()
    commands = "\n".join(entry.commands).lower()
    notes = entry.notes.lower()

    total = 0
    for word in words:
        if word in title:
            total += TITLE
        elif word in topic:
            total += TOPIC
        elif word in commands:
            total += COMMAND
        elif word in notes:
            total += NOTES
        else:
            return 0
    return total


def search(entries: list[Entry], query: list[str], topic: str | None = None,
           tag: str | None = None) -> list[Entry]:
    """Return matching entries, best first.

    ``topic`` and ``tag`` (both case-insensitive) narrow the entries searched.

    Ties keep the notes' own order (file name, then position in the file).
    With no query words, every entry matches, so ``crib -t git`` lists a topic.
    """
    words = [w.lower() for part in query for w in part.split()]
    if topic is not None:
        entries = [e for e in entries if e.topic.lower() == topic.lower()]
    if tag is not None:
        entries = [e for e in entries if tag.lower() in e.tags]
    if not words:
        return list(entries)

    scored = [(score(e, words), i, e) for i, e in enumerate(entries)]
    hits = [item for item in scored if item[0] > 0]
    hits.sort(key=lambda item: (-item[0], item[1]))
    return [e for _, _, e in hits]
