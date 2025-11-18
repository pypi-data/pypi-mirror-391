"""Tools for unpacking software, support files, and scripts."""

from pathlib import Path
from typing import TextIO


def create_directories(
    *to_create: Path, verbosity: int = 0, stderr: TextIO | None = None
) -> None:
    """Create directories."""
    for d in to_create:
        d.mkdir(parents=True, exist_ok=False)
        if verbosity > 0:
            msg = f"Directory created at: {d}"
            print(msg, file=stderr)
