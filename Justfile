default: lint tests docs

# Live-reloading documentation
docs:
    uv run pdoc depyty

# Runs all tests
tests:
    uv run pytest

# Formats all Python files
format:
    uv run ruff format

# Validates the types
types:
    uv run mypy src

# Validate formatting, types, and common errors
lint:
    uv run ruff check --fix

# Runs linting and type checking
validate: lint types
