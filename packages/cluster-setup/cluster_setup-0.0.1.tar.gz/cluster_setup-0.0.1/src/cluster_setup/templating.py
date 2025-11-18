"""Functions for templating files."""

from pathlib import Path
from typing import Any
from typing import TextIO

import jinja2
from jinja2 import Environment


def write_bash_profile(dest: Path) -> None:
    """Write the .bash_profile file."""
    with dest.open(mode="w", encoding="utf-8") as file:
        file.write(
            "# Ensure that .bashrc is sourced for all login shells\n"
            "if [ -f ~/.bashrc ]; then . ~/.bashrc; fi\n"
        )


def template_file(
    filename: Path,
    template_filename: str | Path,
    verbosity: int,
    stderr: TextIO | None = None,
    **template_vars: Any,
) -> None:
    """Create a file from a Jinja2 template.

    Args:
        filename: The path in which to save the templated file.
        template_filename: The path to the template.
        verbosity: The level of verbosity.
        stderr: A file to which the standard error will be written.
            Defaults to None.
        template_vars: Additional variables that will be passed to the template
            context.
    """
    env = Environment(
        loader=jinja2.FileSystemLoader(
            searchpath=Path(template_filename).parent
        ),
        autoescape=True,
        trim_blocks=True,
    )
    template = env.get_template(Path(template_filename).name)
    filename.parent.mkdir(exist_ok=True)

    with filename.open(mode="w", encoding="utf-8") as file:
        file.write(template.render(**template_vars))

    if verbosity > 0:
        msg = f"Successfully templated {filename.parent.name} file: {filename}"
        print(msg, file=stderr)


def _write_default_bashrc(
    dest: Path, python_venv: str, module_home: str
) -> None:
    """Write the default .bashrc file."""
    with dest.open(mode="w", encoding="utf-8") as file:
        file.write(
            f"alias activate_env='source {python_venv}/bin/activate'\n\n"
            "# Configure/setup Lmod\n"
            "module purge\n"
            f'module use "{module_home}\n"'
        )


def write_bashrc(
    filename: Path,
    template_filename: str | None,
    python_venv: str | Path,
    module_home: str,
    software_home: str,
    support_file_home: str,
    verbosity: int = 0,
    stderr: TextIO | None = None,
) -> None:
    """Write the .bashrc file."""
    if template_filename:
        template_vars = {
            "python_venv": python_venv,
            "module_home": module_home,
            "software_home": software_home,
            "support_file_home": support_file_home,
        }
        template_file(
            filename=filename,
            template_filename=template_filename,
            verbosity=verbosity,
            stderr=stderr,
            **template_vars,
        )
    else:
        _write_default_bashrc(filename, str(python_venv), str(module_home))
