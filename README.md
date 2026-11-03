# cmd-crib

`crib` looks up commands from your own cheatsheet notes, kept as plain Markdown
files. Type a few words, get back the command you wrote down last time.

Work in progress: see [ROADMAP.md](ROADMAP.md).

## Install

Needs Python 3.11 or newer. No runtime dependencies.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
```

## Test

```bash
pytest
```

## License

MIT, see [LICENSE](LICENSE).
