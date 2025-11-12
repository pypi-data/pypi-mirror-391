# MiraBest Identifier

## Documentation quickstart

```bash
# Install runtime dependencies
uv sync --all-groups

# Generate static docs into the docs/ folder
uv run --group dev pdoc src/mirabest_identifier -o docs

# Open the result in your browser
python -m webbrowser docs/index.html
```

You can also preview the docs locally without writing files:

```bash
uv run --group dev pdoc src/mirabest_identifier
```

This project ships with docstrings in Google style, so pdoc renders the module and API documentation automatically.
