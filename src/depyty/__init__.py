"""
Enforces all imports in you monorepo to be declared as dependencies.

## Example

Given the following `pyproject.toml` file

```toml
name = "my-awesome-api"
version = "1.2.3"
dependencies = ["fastapi"]
```

we'd get the following feedback

```python
# ✅ This is fine, we explicitly declared this module as a dependency
from fastapi import FastAPI

# ❌ This will very likely fail at runtime. We have not declared a dependency on
# `pandas` in our `pyproject.toml` file.
import pandas as pd

# ⚠️ This is also not allowed, even though, it will likely not crash at runtime.
# Pydantic will be installed, as it is a dependency of `fastapi`. However,
# since **you** import it here, you likely rely on its behavior in your code.
# If **you** do not also declare which version
from pydantic import BaseModel
```
"""
