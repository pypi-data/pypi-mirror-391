"""For handling CLI options."""

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
import re
import shutil
import subprocess
from typing import TextIO

# SCRIPT:TEMPLATE:MODULE:VERSION:ARGS
SoftwareScript = tuple[str, str | None, str | None, str, list[str]]

_REPO_RE = re.compile(r"(?P<domain>.+):(?P<user>.+)/(?P<root>.+)\.git")


@dataclass
class Options:
    """Options collected from flags."""

    # These defaults MUST remain synchronized with those of the CLI args
    # defined in .main.process_options
    # Denote hidden options with leading underscores

    # General
    config_file: str | None = None
    verbosity: int = 0
    check: bool = True

    # Directories
    software_home: str = str(Path("~/software").expanduser())
    support_file_home: str = str(Path("~/support_files").expanduser())
    module_home: str = str(Path("~/modules").expanduser())

    # Python
    python_venv: str = "python_venv"
    python_packages: list[str] = field(default_factory=list)
    python_requirements: list[str] = field(default_factory=list)
    python_repos: list[str] = field(default_factory=list)

    # Git
    _git: str | None = field(default=shutil.which("git"))
    git_config_file: str = str(Path("~/.gitconfig").expanduser())
    git_user_name: str | None = None
    git_email: str | None = None
    git_editor: str | None = None
    git_rebase_on_pull: bool | None = None
    git_sign_with_ssh: bool = False
    ssh_key: str | None = None

    # Software
    bashrc: str | None = None
    software_scripts: list[SoftwareScript] = field(default_factory=list)


def _validate_git(options: Options, stderr: TextIO | None = None) -> None:
    if not options._git and any(
        [
            options.git_user_name,
            options.git_email,
            options.git_editor,
            options.git_rebase_on_pull,
            options.git_sign_with_ssh,
            options.ssh_key,
        ]
    ):
        msg = (
            "git executable not on PATH, but git config options are set. "
            "git configuration will be skipped..."
        )
        print(msg, file=stderr)

    if not options.git_email and options.git_sign_with_ssh:
        msg = "No git email provided. Signing with ssh will not be configured"
        print(msg, file=stderr)


def _validate_repository_uris(
    uris: list[str], stderr: TextIO | None = None
) -> bool:
    """Validate repository URIs.

    Valid URIs have the form:
        DOMAN:USER/REPO.git
    """
    for uri in uris:
        if _REPO_RE.match(uri) is None:
            msg = f"Invalid repository uri: {uri}"
            print(msg, file=stderr)
            return False
    return True


def _extract_endpoints(repos: list[str]) -> list[str]:
    return [x.split(":")[0] for x in repos]


def _validate_ssh_key(repos: list[str]) -> list[bool]:
    """Check that an ssh key has access to the given endpoints.

    Args:
        repos: A list of remote repositories.

    Returns:
        A list of booleans where the ith entry indicates whether or not the
        SSH key has access to the given endpoints.
    """
    results = []
    endpoints = _extract_endpoints(repos)
    for endpoint in endpoints:
        args = ["ssh", "-T", "git@" + endpoint]
        output = subprocess.run(  # noqa: S603
            args, check=False, capture_output=True, text=True
        )
        results.append(
            output.returncode == 0 or output.stderr.startswith("Hi")
        )
    return results


def validate_options(options: Options, stderr: TextIO | None = None) -> bool:
    """Validate CLI options."""
    _validate_git(options, stderr)
    uris_valid = _validate_repository_uris(options.python_repos, stderr)
    ssh_key_valid = False not in _validate_ssh_key(options.python_repos)
    return uris_valid and ssh_key_valid
