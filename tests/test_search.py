from pathlib import Path

from cmd_crib.notes import Entry
from cmd_crib.search import score, search


def entry(topic, title, commands=(), notes=""):
    return Entry(topic=topic, title=title, path=Path(f"{topic}.md"), line=1,
                 commands=list(commands), notes=notes)


ENTRIES = [
    entry("tar", "Extract an archive", ["tar xf archive.tar"]),
    entry("tar", "Create a gzip archive", ["tar czf out.tgz dir/"]),
    entry("git", "Undo last commit", ["git reset --soft HEAD~1"], "keeps changes staged"),
    entry("git", "List files in a commit", ["git show --name-only REV"]),
    entry("ffmpeg", "Cut a clip", ["ffmpeg -ss 10 -i in.mp4 -t 5 out.mp4"]),
]


def titles(results):
    return [e.title for e in results]


def test_all_words_must_match():
    assert titles(search(ENTRIES, ["tar", "extract"])) == ["Extract an archive"]
    assert search(ENTRIES, ["tar", "nothing-like-this"]) == []


def test_case_insensitive():
    assert titles(search(ENTRIES, ["UNDO"])) == ["Undo last commit"]


def test_title_hit_ranks_above_command_hit():
    results = search(ENTRIES, ["commit"])
    assert titles(results) == ["Undo last commit", "List files in a commit"]
    a = entry("x", "files", ["ls"])
    b = entry("x", "listing", ["ls files"])
    assert titles(search([b, a], ["files"])) == ["files", "listing"]


def test_notes_and_topic_are_searched():
    assert titles(search(ENTRIES, ["staged"])) == ["Undo last commit"]
    assert titles(search(ENTRIES, ["ffmpeg"])) == ["Cut a clip"]


def test_score_weights():
    e = entry("git", "Undo", ["git reset"], "staged")
    assert score(e, ["undo"]) == 8
    assert score(e, ["git"]) == 4
    assert score(e, ["reset"]) == 2
    assert score(e, ["staged"]) == 1
    assert score(e, ["undo", "missing"]) == 0


def test_ties_keep_original_order():
    assert titles(search(ENTRIES, ["archive"])) == ["Extract an archive", "Create a gzip archive"]


def test_topic_filter_and_empty_query():
    assert titles(search(ENTRIES, [], topic="git")) == ["Undo last commit", "List files in a commit"]
    assert titles(search(ENTRIES, ["archive"], topic="GIT")) == []
    assert len(search(ENTRIES, [])) == len(ENTRIES)


def test_quoted_query_is_split_into_words():
    assert titles(search(ENTRIES, ["cut clip"])) == ["Cut a clip"]


def test_tag_filter():
    a = entry("sh", "Open ports", ["ss -tlnp"])
    a.tags = ["net", "debug"]
    b = entry("sh", "Disk usage", ["du -sh"])
    b.tags = ["disk"]
    assert titles(search([a, b], [], tag="NET")) == ["Open ports"]
    assert titles(search([a, b], ["disk"], tag="net")) == []
    assert titles(search([a, b], ["usage"], tag="disk")) == ["Disk usage"]
