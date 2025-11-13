import os
import sys
from pathlib import Path
from subprocess import call
from tomllib import load


def find_settings(root=Path.cwd()) -> dict:
    def walk(path):
        for fn in path.iterdir():
            if fn.name.startswith("."):
                continue
            if fn.is_dir():
                yield from walk(fn)
            elif fn.name == "settings.py":
                yield fn

    for fn in walk(root):
        # Given a path, we want to convert it to a list, so that we
        # pop off an optional src/ directory and then convert to
        # python package dot notation
        settings = str(fn.with_suffix("").relative_to(root)).split("/")
        if settings[0] == "src":
            settings.pop(0)
        return {"settings": ".".join(settings)}
    return {}


def find_pyproject(path=Path.cwd() / "pyproject.toml") -> dict:
    if path.exists:
        with path.open("rb") as fp:
            data = load(fp)

    try:
        settings = data["tool"]["django"]
    except KeyError:
        return find_settings(root=path.parent)
    else:
        return settings


def main(argv=sys.argv) -> None:
    settings = find_pyproject()
    env = os.environ.copy()
    if "settings" in settings:
        env["DJANGO_SETTINGS_MODULE"] = settings["settings"]
        call(["uv", "run", "django-admin"] + argv[1:], env=env)
    else:
        from django.core.management import ManagementUtility

        utility = ManagementUtility(argv)
        utility.execute()
