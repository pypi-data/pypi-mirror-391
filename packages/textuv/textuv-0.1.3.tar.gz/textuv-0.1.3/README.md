# textuv

Scaffold a Textual + uv application.

- GitHub: https://github.com/totsuxyz/textuv

## Install & Run

- Zero-install (recommended):

```bash
uvx textuv --help
# 0.1.2+ also supports subcommand:
# uvx textuv new my-textual-app
uvx textuv my-textual-app
```

- Or install the CLI locally:

```bash
uv tool install .
textuv --help
# both forms work:
textuv my-textual-app
textuv new my-textual-app
```

## Generated project

The scaffold includes:
- `src/<package>/app.py` — minimal Textual App
- `pyproject.toml` — with `textual` and dev extras
- `Makefile`, `.gitignore`, `tests/__init__.py`

Next steps after generation:

```bash

cd my-textual-app
uv venv
uv pip install -e .
uv pip install -e ".[dev]"
uv run textual run --dev src/<package>/app.py
```

## License

MIT


