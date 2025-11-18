"""Tools for setting up git."""

from pathlib import Path
import subprocess
from typing import Any
from typing import TextIO

_ALLOWED_SIGNERS = str(Path("~/.ssh/allowed_signers").expanduser())


def clone_repos(
    git: str | None = None,
    to_clone: list[str] | None = None,
    dest: str | Path | None = None,
    stderr: TextIO | None = None,
) -> None:
    """Clone remote repositories.

    Args:
        git: The path to the git executable.
        to_clone: A list of strings indicating the repositories to clone. Repos
            must be in the form DOMAN:USER/REPO.git. For example,
            github.com:ugognw/cluster-setup.git. Defaults to an empty list.
        dest: The directory into which to clone the repos. Defaults to the
            current directory.
        stderr: A text file opened for writing. Defaults to the standard output.
    """
    assert git is not None
    to_clone = to_clone or []
    dest = dest or Path.cwd()

    for repo in to_clone:
        args = [git, "clone", f"git@{repo}"]
        subprocess.run(args, check=True, cwd=dest, stderr=stderr)  # noqa: S603


def _construct_git_signer_text(ssh_key: str, email: str) -> str:
    with Path(ssh_key).open(mode="r", encoding="utf-8") as file:
        key_data = file.read()
    to_append = f'{email} namespaces="git" {key_data}'
    return to_append


def _get_git_config(git: str | None, git_config_file: str) -> dict[str, str]:
    assert git is not None
    args = [git, "config", "-f", git_config_file, "-l"]
    output = subprocess.check_output(  # noqa: S603
        args, text=True
    )
    config: dict[str, Any] = {}

    for line in output.splitlines():
        key, value = line.split("=", maxsplit=1)
        config[key] = value
    return config


def _reset_git_config(
    git: str | None,
    git_config_file: str | None,
    old_config: dict[str, str],
    **new_config: Any,
) -> None:
    assert git is not None
    cmd_prefix = [git, "config"]

    if git_config_file:
        cmd_prefix.extend(["-f", git_config_file])
    else:
        cmd_prefix.append("--global")

    for key, value in new_config.items():
        if old_config.get(key) == value:
            continue
        if key in old_config:
            args = [key, old_config[key]]
        else:
            args = ["--unset", key]
        _ = subprocess.run(  # noqa: S603
            [*cmd_prefix, *args],
            check=True,
        )


def configure_git(
    *,
    git: str | None = None,
    home: Path | None = None,
    git_config_file: str | None = None,
    user_name: str | None = None,
    email: str | None = None,
    editor: str | None = None,
    rebase_on_pull: bool | None = None,
    sign_with_ssh: bool = False,
    ssh_key: str | None = None,
    _allowed_signers: str = _ALLOWED_SIGNERS,
) -> None:
    """Configure git."""
    assert git is not None
    home = home or Path.home()

    if not git_config_file or not Path(git_config_file).exists():
        git_config_file = str(Path(home, ".gitconfig").expanduser())
        Path(git_config_file).touch()

    old_config = _get_git_config(git, git_config_file)
    cmd_prefix = [git, "config", "-f", git_config_file]
    cmds = []

    if rebase_on_pull is not None:
        cmds.append(["pull.rebase", str(rebase_on_pull).lower()])
    if user_name:
        cmds.append(["user.name", user_name])
    if email:
        cmds.append(["user.email", email])
    if editor:
        cmds.append(["core.editor", editor])
    if sign_with_ssh and ssh_key and email:
        # Append ssh public key to ~/.ssh/allowed_signers
        to_append = _construct_git_signer_text(ssh_key, email)
        if _allowed_signers:
            signers_file = Path(_allowed_signers)
        else:
            signers_file = Path.home().joinpath(".ssh/allowed_signers")
        with signers_file.open(mode="a", encoding="utf-8") as file:
            file.write(to_append)

        cmds.extend(
            [
                ["gpg.format", "ssh"],
                ["user.signingkey", ssh_key],
                ["commit.gpgsign", "true"],
                ["gpg.ssh.allowedsignersfile", str(_allowed_signers)],
            ]
        )
    try:
        for cmd in cmds:
            _ = subprocess.run(  # noqa: S603
                [*cmd_prefix, *cmd], check=False, text=True
            )
    except:
        new_config = _get_git_config(git, git_config_file)
        _reset_git_config(git, git_config_file, old_config, **new_config)
        raise
