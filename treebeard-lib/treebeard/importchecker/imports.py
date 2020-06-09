import glob
import re
import sys
from pydoc import ModuleScanner
from typing import Any, Optional, Set

import click
from nbconvert import ScriptExporter  # type: ignore
from sentry_sdk import capture_exception  # type: ignore

from_regexp = re.compile(r"^from (\w+)")
import_regexp = re.compile(r"^import (\w+)")


def get_imported_modules(glob_path: str) -> Set[str]:
    nb_paths = glob.glob(glob_path, recursive=True)
    if len(nb_paths) == 0:
        raise Exception(f"No notebooks found with glob {glob_path}")

    se: Any = ScriptExporter()

    all_imported_modules = set()
    for path in nb_paths:
        try:
            click.echo(f"Import check inspecting {path}")
            [script, _] = se.from_filename(path)
        except Exception as ex:
            capture_exception(ex)
            click.echo(f"Import checker cannot read {path}")
            continue
        lines = script.split("\n")

        for line in lines:
            from_match = from_regexp.match(line)
            if from_match:
                all_imported_modules.add(from_match.group(1))
                continue

            import_match = import_regexp.match(line)
            if import_match:
                all_imported_modules.add(import_match.group(1))
                continue

    return all_imported_modules


def get_installed_modules() -> Set[str]:
    modules = set()

    def callback(path: Optional[str], modname: str, desc: str):
        if modname and modname.endswith(".__init__"):
            modname = modname.replace(".__init__", " (package)")

        if modname.find(".") == -1:
            modules.add(modname)

    def onerror(modname: str):
        pass

    ModuleScanner().run(callback, onerror=onerror)
    return modules


def is_local_module(module_name: str):
    # is there a <name>.py or <name> directory
    dirs = glob.glob(f"**/{module_name}", recursive=True)
    scripts = glob.glob(f"**/{module_name}.py", recursive=True)

    return dirs or scripts


def check_imports(glob_path: str = "**/*ipynb"):
    click.echo(f"🌲 Checking for potentially missing imports...\n")
    imported_modules = get_imported_modules(glob_path)
    installed_modules = get_installed_modules()

    missing_modules = list(
        filter(
            lambda m: not is_local_module(m),
            imported_modules.difference(installed_modules),
        )
    )

    if len(missing_modules) > 0:
        click.echo(
            f"\n❗📦 You *may* be missing project requirements, the following modules are imported from your notebooks but can't be imported from your project root directory\n"
        )
        for module in sorted(missing_modules):
            click.echo(f"  - {module}")
        return False
    else:
        click.echo(
            "\n✨ All notebook imports appear to be backed by a reproducible dependency file!"
        )
        return True


if __name__ == "__main__":
    glob_path = sys.argv[1] if len(sys.argv) > 1 else "**/*ipynb"
    check_imports(glob_path)
