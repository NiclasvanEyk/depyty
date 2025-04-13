# Depyty

> /ˈdɛpaɪti/ as in the english word "deputy", but for Python *dep*endencies.

Enforce proper dependency declaration in shared Python environments.

## Usage

Install the package using

```shell
uv add --dev depyty
```

then run it via

```shell
uv run depyty "packages/*"
```

You can pass `glob.glob` strings that lead to all `pyproject.toml` files in your repository that you want to check.
Note the use of `"`s to prevent your shell from expanding the references.


## Example

Given the following `pyproject.toml` file

```toml
name = "my-awesome-api"
version = "1.2.3"
dependencies = ["fastapi"]
```

---

```python
from fastapi import FastAPI
```

✅ This is fine, we explicitly declared this module as a dependency

---

```python
import pandas as pd
```

❌ This will very likely fail at runtime.
We have not declared a dependency on `pandas` in our `pyproject.toml` file.

---

```python
from pydantic import BaseModel
```

⚠️ This is also not allowed, even though it will likely not crash at runtime.
Pydantic will be installed, as it is a dependency of `fastapi`.
However, since **you** imported it in your code, you'll likely also depend on Pydantics API.
If they decide to publish a breaking change, and FastAPI increments their minimum Pydantic version to the new one, your code can easily break.
By explicitly declaring a version and dependency upon `pydantic` in your `pyproject.toml`, you are in full control.

## Assumptions

- You develop a modern, `pyproject.toml`-based Python application/library/monorepo, and not a one-off script
- You install all third-party dependencies in a [virtual Python environment](https://virtualenv.pypa.io/en/latest/user_guide.html)

## Motivation

Tools like [`uv`](https://docs.astral.sh/uv) make it very convenient to create monorepos.

### Scenario

Imagine this hypothetical scenario, where our main application is a REST API, and we have a few lambdas that do auxiliary tasks.
All of them live in a shared monorepo:

```
depyty-demo-api
├── lambdas
│   ├── cleanup-old-db-entries-lambda
│   │   ├── main.py
│   │   └── pyproject.toml
│   └── data-warehouse-export-lambda
│       ├── main.py
│       └── pyproject.toml
├── packages
│   └── demo-database-models
│       ├── pyproject.toml
│       └── src
│           └── demo_database_models
│               ├── __init__.py
│               └── py.typed
├── pyproject.toml
└── src
    └── depyty_demo_api
        ├── __init__.py
        └── api.py
```

The lambdas may execute tasks like cleaning up database tables, or exporting them to S3.
They contain dependencies (e.g. `boto3` to interact with S3), that are not needed in your main application, so you declare them separately.
At the same time, they share code with your main application, e.g. the database models.

The `pyproject.toml` files would then look like this for the main application

```toml
# pyproject.toml
name = "depyty-demo-api"
dependencies = [
    "demo-database-models",
    "fastapi>=0.115.12",
]

[dependency-groups]
dev = ["pytest>=8.3.5"]

[tool.uv.workspace]
members = ["packages/*", "lambdas/*"]

[tool.uv.sources]
demo-database-models = { workspace = true }
```

and like this for a lambda

```toml
# lambdas/data-warehouse-export-lambda/pyproject.toml
[project]
name = "data-warehouse-export-lambda"
dependencies = [
    "boto3>=1.37.23",
    "demo-database-models",
]

[tool.uv.sources]
demo-database-models = { workspace = true }
```

Again, we don't want to inlcude `boto3` in our main application, so during deployment we run

```shell
uv sync
```

for our main application and

```shell
uv sync --package data-warehouse-export-lambda
```

for the exporter lambda.

### Problem

Imagine you add a new feature, which you decide to develop in a new library under `packages/my-new-utility-package`, since it contains very generic functionality.
Once its done, you run `uv add` at the project root and integrate it into the main application.

The next day, your intuition turns out to be right, and you need the functionality in one of the lambdas.
You immediately adjust the source code, your IDE happily autocompletes everything.
You also write unit tests, run `pytest`, and everything works like a charm.
Then you push everything, and everything fails ✨spectacularly✨.

Turns out you did not run `uv add my-new-utility-package` for your lambda, so it was never included as a dependency in its `pyproject.toml`.
Since you use `uv sync --all-packages` during local development, the dependencies of all packages are available locally.
But during deployment, you only install everything listed in each `pyproject.toml`.

### Solution

This is exactly what `depyty` solves.
It analyzes the packages available in the current environment, and checks the source files of each provided package, that it only `import`s modules that are also declared in its `pyproject.toml`.
To prevent an error like this, we'd just need to add

```shell
uv run depyty "lambdas/*" "."
```

to our CI and we should not get nasty surprises when deploying the next time.
At least not due to unspecified dependencies.

