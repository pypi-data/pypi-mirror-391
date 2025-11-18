"""Functions for installing software."""

from pathlib import Path
import subprocess
from typing import TextIO


def install_software(
    script: str | Path,
    software_home: str | Path,
    support_file_home: str | Path,
    python_venv: str | Path,
    *script_args: str,
    verbosity: int = 0,
    stderr: int | TextIO | None = None,
) -> None:
    """Install software via a script."""
    software_home = str(software_home)
    support_file_home = str(support_file_home)
    python_venv = str(python_venv)
    stderr = stderr or subprocess.STDOUT

    def _replace_args(args: tuple[str, ...]) -> list[str]:
        """Replace templated arguments."""
        new_args = []
        for arg in args:
            new_arg = arg.replace("{software_home}", software_home)
            new_arg = new_arg.replace("{support_file_home}", support_file_home)
            new_arg = new_arg.replace("{python_venv}", python_venv)
            new_args.append(new_arg)
        return new_args

    replaced_args = _replace_args(script_args)

    if verbosity > 0:
        msg = f"Running software installation script: {script} with args: {replaced_args}"
        print(msg)

    args = [
        str(script),
        *replaced_args,
    ]
    _ = subprocess.run(args, check=True, stderr=stderr)  # noqa: S603

    if verbosity > 0:
        msg = f"Successfully executed installation script: {script}"
        print(msg)
