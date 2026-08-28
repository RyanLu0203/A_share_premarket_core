# Python Runtime Compatibility

The project policy remains Python `>=3.9`. The clean GOAL-06B workflow retains
its Python 3.9 support claim, while the optional `httpx2` test compatibility
package is installed only on Python 3.10 or newer because its published package
metadata does not support Python 3.9.

The test extra resolves successfully under both policies:

```text
uv pip compile pyproject.toml --extra test --python-version 3.9
uv pip compile pyproject.toml --extra test --python-version 3.12
```

The Python 3.9 resolution contains `httpx` but excludes `httpx2`; the Python
3.12 resolution contains both. This is dependency-policy evidence only and
does not alter provider, research, recommendation, position, or execution
boundaries.
