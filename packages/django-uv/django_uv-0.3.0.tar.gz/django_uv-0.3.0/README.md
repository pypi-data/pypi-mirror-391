# django-uv helper

A helper for uv to allow calling django-admin for a regular project.

```bash
uvx django-uv
# Translates to running `uv run django-admin` in your project
```

You can configure the `DJANGO_SETTINGS_MODULE` in your `pyproject.toml`

```toml
[tool.django]
settings = 'path.to.our.settings'
```

Or let `django-uv` try to automatically detect it.
