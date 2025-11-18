"""Tools for setting up Python virtual environments."""

from pathlib import Path
import subprocess
from typing import TextIO
import venv


def setup_venv(
    python_venv: Path,
    packages: list[str] | None,
    requirements: list[str] | None,
    verbosity: int = 0,
    stderr: int | TextIO | None = None,
) -> None:
    """Set up a Python virtual environment and install packages."""
    venv.create(python_venv, clear=True, with_pip=True)
    executable = Path(python_venv, "bin", "python")
    args: list[str | Path] = [executable, "-m", "pip", "install"]

    if verbosity > 0:
        args.append("-v")
    if packages:
        args.extend(packages)
    if requirements:
        for req in requirements:
            args.extend(["-r", req])

    if packages or requirements:
        _ = subprocess.run(  # noqa: S603
            args,
            check=True,
            stderr=stderr,
            text=True,
        )
