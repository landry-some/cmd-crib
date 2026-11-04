# cmd-crib

`crib` looks up commands from your own cheatsheet notes, kept as plain Markdown
files. Type a few words, get back the command you wrote down last time.

It is for people who already keep notes on commands they run only now and then
(tar flags, ffmpeg options, git recovery tricks) and are tired of grepping those
notes and reading around the match.

Built with Python 3.11+ and the standard library only. Tests use pytest.

## Install

```bash
git clone https://github.com/landry-some/cmd-crib.git
cd cmd-crib
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
```

This puts a `crib` command in the virtual environment.

## Try it on the sample notes

```bash
crib --dir examples/notes tar extract
crib --dir examples/notes -c cut clip
crib --dir examples/notes --topics
```

## Notes format

A notes folder holds one `.md` file per topic. The file name is the topic:
`git.md` is topic `git`. Files in subfolders are not read.

Inside a file, every `## heading` starts an entry. Under it:

- a line that is only inline code, like `` `tar tf backup.tgz` ``, is a command;
- a fenced code block is one command (it can span several lines);
- any other text is a note, searched and shown as `# ...` under the command.

Text before the first `##` heading (a `# title`, an intro) is ignored. Files are
read as UTF-8; CRLF line endings and a byte order mark are fine, and `crib add`
keeps a file's CRLF endings.

````markdown
# git

## Undo last commit, keep changes
`git reset --soft HEAD~1`

## Show a file as it was at an old commit
Use the short hash from git log.
```bash
git show abc1234:src/main.py
```
````

## Where notes are read from

1. `--dir PATH`, if given
2. `$CRIB_DIR`, if set
3. `$XDG_CONFIG_HOME/crib/notes`, else `~/.config/crib/notes`

## Usage

```text
crib WORDS...            show entries matching all the words, best first
crib -c WORDS...         print only the command(s) of the best match
crib -t TOPIC [WORDS]    search one topic; with no words, list the whole topic
crib -n N WORDS...       show at most N results (default 10, 0 for all)
crib --topics            list topics and how many entries each has
crib add TOPIC TITLE COMMAND... [-m NOTE]
                         append an entry to TOPIC.md (created if missing)
```

Matching is case-insensitive substring matching. Every word has to appear in the
entry's title, topic, commands or notes. A word found in the title counts more than
one found in the topic, which counts more than the command, then the notes. Equal
scores keep the order of the files.

`crib` exits with 0 when something matched, 1 when nothing did, and 2 on bad input.

`-c` is meant for pasting or piping, for example `crib -c cut clip | wl-copy`.

### Adding entries

```bash
crib add docker "Remove stopped containers" docker container prune
crib add git "Find which commit removed a line" 'git log -S "name" --oneline' -m "searches every diff"
```

Several command words are joined with spaces. If unquoted command words start
with `-`, put `--` before the command (`crib add sh "Long listing" -- ls -la`).
Quote the whole command when it contains its own quotes, or the shell will strip them. Commands with backticks are
written as a fenced block so they read back unchanged.

## Test

```bash
pytest
```

## Plans

See [ROADMAP.md](ROADMAP.md).

## License

MIT, see [LICENSE](LICENSE).
