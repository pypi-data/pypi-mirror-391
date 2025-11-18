from collections.abc import Generator
from collections.abc import Iterable
from io import StringIO
from pathlib import Path
import shlex
import shutil
import stat
from typing import Any
from typing import TextIO

import pytest

from cluster_setup.config import _map_types
from cluster_setup.git import _get_git_config
from cluster_setup.git import _reset_git_config
from cluster_setup.git import clone_repos
from cluster_setup.git import configure_git
from cluster_setup.unpack import create_directories


@pytest.fixture(name="tmp_home")
def fixture_tmp_home(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("home", numbered=True)


@pytest.fixture(name="git")
def fixture_git() -> str | None:
    return shutil.which("git")


# The suffixes "config" and "cli" denote option values set in the
# configuration file and command-line, respectively.


# Config Values


@pytest.fixture(name="check_config", params=[None])
def fixture_check_config(request: pytest.FixtureRequest) -> bool | None:
    param = request.param
    if param is None:
        return None
    return bool(request.param)


@pytest.fixture(name="software_home_config", params=[None])
def fixture_software_home_config(
    tmp_home: Path, request: pytest.FixtureRequest
) -> str | None:
    param = request.param
    if param is None:
        return None
    return str(Path(tmp_home, "software"))


@pytest.fixture(name="support_file_home_config", params=[None])
def fixture_support_file_home_config(
    tmp_home: Path, request: pytest.FixtureRequest
) -> str | None:
    param = request.param
    if param is None:
        return None
    return str(Path(tmp_home, "support_files"))


@pytest.fixture(name="module_home_config", params=[None])
def fixture_module_home_config(
    tmp_home: Path, request: pytest.FixtureRequest
) -> str | None:
    param = request.param
    if param is None:
        return None
    return str(Path(tmp_home, "modules"))


@pytest.fixture(name="python_venv_config", params=[None])
def fixture_python_venv_config(request: pytest.FixtureRequest) -> str | None:
    param = request.param
    if param is None:
        return None
    return str(request.param)


@pytest.fixture(name="python_packages_config", params=[None])
def fixture_python_packages_config(
    request: pytest.FixtureRequest, tmp_home: Path
) -> list[str]:
    param = request.param
    if not param or not isinstance(param, Iterable):
        return []
    return [str(Path(tmp_home, str(req))) for req in param]


@pytest.fixture(name="python_requirements_packages_config", params=[None])
def fixture_python_requirements_packages_config(
    request: pytest.FixtureRequest,
) -> list[list[str]]:
    param = request.param
    if not param or not isinstance(param, Iterable):
        return []
    return [[str(p) for p in req] for req in param]


@pytest.fixture(name="python_requirements_config", params=[None])
def fixture_python_requirements_config(
    request: pytest.FixtureRequest, tmp_home: Path
) -> list[str] | None:
    param = request.param
    if not param or not isinstance(param, Iterable):
        return []
    return [str(Path(tmp_home, str(req))) for req in param]


@pytest.fixture(name="write_requirements_config")
def fixture_write_requirements_config(
    python_requirements_config: list[str] | None,
    python_requirements_packages_config: list[list[str]] | None,
) -> None:
    if (
        fnames := python_requirements_config
    ) and python_requirements_packages_config:
        for i, fname in enumerate(fnames):
            with Path(fname).open(mode="w", encoding="utf-8") as file:
                file.writelines(
                    "\n".join(python_requirements_packages_config[i] or [])
                )


@pytest.fixture(name="python_repos_config", params=[None])
def fixture_python_repos_config(request: pytest.FixtureRequest) -> list[str]:
    param = request.param
    if not param or not isinstance(param, Iterable):
        return []
    return [str(p) for p in request.param]


@pytest.fixture(name="git_config_file_config", params=[".gitconfig"])
def fixture_git_config_file_config(
    request: pytest.FixtureRequest, tmp_home: Path
) -> Generator[str | None, None, None]:
    param = request.param
    if param is None:
        return None
    git_config_file = Path(tmp_home, ".gitconfig")
    git_config_file.touch()
    yield str(git_config_file)
    git_config_file.unlink(missing_ok=True)


@pytest.fixture(name="git_user_name_config", params=[None])
def fixture_git_user_name_config(request: pytest.FixtureRequest) -> str | None:
    return None if request.param is None else str(request.param)


@pytest.fixture(name="git_email_config", params=[None])
def fixture_git_email_config(request: pytest.FixtureRequest) -> str | None:
    return None if request.param is None else str(request.param)


@pytest.fixture(name="git_editor_config", params=[None])
def fixture_git_editor_config(request: pytest.FixtureRequest) -> str | None:
    return None if request.param is None else str(request.param)


@pytest.fixture(name="git_rebase_on_pull_config", params=[None])
def fixture_git_rebase_on_pull_config(
    request: pytest.FixtureRequest,
) -> bool | None:
    return None if request.param is None else bool(request.param)


@pytest.fixture(name="git_sign_with_ssh_config", params=[None])
def fixture_git_sign_with_ssh_config(
    request: pytest.FixtureRequest,
) -> bool | None:
    return None if request.param is None else bool(request.param)


@pytest.fixture(name="ssh_key_config", params=[None])
def fixture_ssh_key_config(
    request: pytest.FixtureRequest, tmp_path: Path
) -> str | None:
    param = request.param
    if param is None:
        return None
    return str(tmp_path.joinpath(param))


@pytest.fixture(name="bashrc_text_config")
def fixture_bashrc_text_config() -> str:
    return ""


@pytest.fixture(name="bashrc_config", params=[None])
def fixture_bashrc_config(
    request: pytest.FixtureRequest, tmp_path: Path, bashrc_text_config: str
) -> str | None:
    param = request.param
    if param is None:
        return None

    bashrc = Path(tmp_path, param)
    with bashrc.open(mode="w", encoding="utf-8") as file:
        file.write(bashrc_text_config)
    return str(bashrc)


@pytest.fixture(name="software_scripts_tuples_config", params=[None])
def fixture_software_scripts_tuples_config(
    request: pytest.FixtureRequest, datadir: Path
) -> list[tuple[str, str | None, str | None, str | None, str | None]] | None:
    software_scripts_tuples: list[
        tuple[str, str | None, str | None, str | None, str | None]
    ] = []
    param = request.param
    if param is None:
        return None
    assert isinstance(param, Iterable)
    for script, template, module, version, args in param:
        software_scripts_tuples.append(
            (
                str(Path(datadir, script)),
                str(template) if template else None,
                str(module) if module else None,
                str(version) if version else None,
                " ".join(args) if args else None,
            )
        )

    return software_scripts_tuples


@pytest.fixture(name="software_scripts_config")
def fixture_software_scripts_config(
    software_scripts_tuples_config: list[
        tuple[str, str | None, str | None, str | None, str | None]
    ]
    | None,
) -> list[str]:
    if not software_scripts_tuples_config:
        return []
    items: list[str] = []
    for item in software_scripts_tuples_config:
        items.append(":".join(x or "" for x in item))
    return items


@pytest.fixture(name="config_options")
def fixture_config_options(  # noqa: C901, PLR0912
    check_config: bool,
    software_home_config: str | None,
    support_file_home_config: str | None,
    module_home_config: str | None,
    python_venv_config: str | None,
    python_packages_config: list[str],
    python_requirements_config: list[str],
    python_repos_config: list[str],
    git_config_file_config: str | None,
    git_user_name_config: str | None,
    git_email_config: str | None,
    git_editor_config: str | None,
    git_rebase_on_pull_config: bool | None,
    git_sign_with_ssh_config: bool | None,
    ssh_key_config: str | None,
    bashrc_config: str | None,
    software_scripts_config: list[str],
) -> dict[str, Any]:
    config_options: dict[str, Any] = {}

    if check_config is not None:
        config_options["check"] = check_config
    if software_home_config is not None:
        config_options["software_home"] = software_home_config
    if support_file_home_config is not None:
        config_options["support_file_home"] = support_file_home_config
    if module_home_config is not None:
        config_options["module_home"] = module_home_config
    if python_venv_config is not None:
        config_options["python_venv"] = python_venv_config
    if python_packages_config:
        config_options["python_packages"] = python_packages_config
    if python_requirements_config:
        config_options["python_requirements"] = python_requirements_config
    if python_repos_config:
        config_options["python_repos"] = python_repos_config
    if git_config_file_config is not None:
        config_options["git_config_file"] = git_config_file_config
    if git_user_name_config is not None:
        config_options["git_user_name"] = git_user_name_config
    if git_email_config is not None:
        config_options["git_email"] = git_email_config
    if git_editor_config is not None:
        config_options["git_editor"] = git_editor_config
    if git_rebase_on_pull_config is not None:
        config_options["git_rebase_on_pull"] = git_rebase_on_pull_config
    if git_sign_with_ssh_config is not None:
        config_options["git_sign_with_ssh"] = git_sign_with_ssh_config
    if ssh_key_config is not None:
        config_options["ssh_key"] = ssh_key_config
    if bashrc_config is not None:
        config_options["bashrc"] = bashrc_config
    if software_scripts_config:
        config_options["software_scripts"] = software_scripts_config
    return config_options


# CLI Values


@pytest.fixture(name="check_cli", params=[None])
def fixture_check_cli(request: pytest.FixtureRequest) -> bool | None:
    param = request.param
    if param is None:
        return None
    return bool(request.param)


@pytest.fixture(
    name="config_file_header", params=["cluster-setup", "tool.cluster-setup"]
)
def fixture_config_file_header(request: pytest.FixtureRequest) -> str:
    return str(request.param)


@pytest.fixture(name="config_file_text")
def fixture_config_file_text(
    config_options: dict[str, Any], config_file_header: str
) -> str:
    text = [f"[{config_file_header}]"]
    for key, value in config_options.items():
        v = _map_types(value)
        text.append(f"{key} = {v}")

    return "\n".join(text)


@pytest.fixture(name="config_file_cli", params=["config.toml"])
def fixture_config_file_cli(
    tmp_path: Path, request: pytest.FixtureRequest
) -> str | None:
    param = request.param
    return None if param is None else str(Path(tmp_path, param))


@pytest.fixture(name="write_config_file")
def fixture_write_config_file(
    config_file_text: str, config_file_cli: str | None
) -> None:
    if fname := config_file_cli:
        with Path(fname).open(mode="w", encoding="utf-8") as file:
            file.write(config_file_text)


@pytest.fixture(name="verbosity_cli", params=[0, 1])
def fixture_verbosity_cli(request: pytest.FixtureRequest) -> int:
    return int(request.param)


@pytest.fixture(name="software_home_cli")
def fixture_software_home_cli(tmp_home: Path) -> str:
    return str(Path(tmp_home, "software"))


@pytest.fixture(name="support_file_home_cli")
def fixture_support_file_home_cli(tmp_home: Path) -> str:
    return str(Path(tmp_home, "support_files"))


@pytest.fixture(name="module_home_cli")
def fixture_module_home_cli(tmp_home: Path) -> str:
    return str(Path(tmp_home, "modules"))


@pytest.fixture(name="python_venv_cli", params=["python_venv", ".venv"])
def fixture_python_venv_cli(request: pytest.FixtureRequest) -> str:
    return str(request.param)


@pytest.fixture(
    name="python_packages_cli",
    params=[["pillow", "tomli==2.2.1"], ["mypy"]],
)
def fixture_python_packages_cli(
    request: pytest.FixtureRequest,
) -> list[str]:
    return [str(p) for p in request.param]


@pytest.fixture(
    name="python_requirements_packages_cli",
    params=[[["mypy-upgrade"], ["numpy"]]],
)
def fixture_python_requirements_packages_cli(
    request: pytest.FixtureRequest,
) -> list[list[str]]:
    param = request.param
    return [] if param is None else [[str(r) for r in reqs] for reqs in param]


@pytest.fixture(name="python_requirements_cli")
def fixture_python_requirements_cli(
    python_requirements_packages_cli: list[list[str]], tmp_home: Path
) -> list[str] | None:
    requirements = []
    for i, _ in enumerate(python_requirements_packages_cli):
        requirements.append(
            str(tmp_home.joinpath(f"requirements_cli_{i}.txt"))
        )
    return requirements


@pytest.fixture(name="write_requirements_cli")
def fixture_write_requirements_cli(
    python_requirements_cli: list[str] | None,
    python_requirements_packages_cli: list[list[str]] | None,
) -> None:
    if (
        fnames := python_requirements_cli
    ) and python_requirements_packages_cli:
        for i, fname in enumerate(fnames):
            with Path(fname).open(mode="w", encoding="utf-8") as file:
                file.writelines(
                    "\n".join(python_requirements_packages_cli[i] or [])
                )


@pytest.fixture(name="python_repos_cli", params=[None])
def fixture_python_repos_cli(request: pytest.FixtureRequest) -> list[str]:
    param = request.param
    if not param or not isinstance(param, Iterable):
        return []
    return [str(p) for p in request.param]


@pytest.fixture(name="git_config_file_cli", params=[".gitconfig"])
def fixture_git_config_file_cli(
    request: pytest.FixtureRequest, tmp_home: Path
) -> Generator[str | None, None, None]:
    param = request.param
    if param is None:
        return None
    git_config_file = Path(tmp_home, ".gitconfig")
    git_config_file.touch()
    yield str(git_config_file)
    git_config_file.unlink(missing_ok=True)


@pytest.fixture(name="git_user_name_cli", params=[None])
def fixture_git_user_name_cli(request: pytest.FixtureRequest) -> str | None:
    return None if request.param is None else str(request.param)


@pytest.fixture(name="git_email_cli", params=[None])
def fixture_git_email_cli(request: pytest.FixtureRequest) -> str | None:
    return None if request.param is None else str(request.param)


@pytest.fixture(name="git_editor_cli", params=[None])
def fixture_git_editor_cli(request: pytest.FixtureRequest) -> str | None:
    return None if request.param is None else str(request.param)


@pytest.fixture(name="git_rebase_on_pull_cli", params=[None])
def fixture_git_rebase_on_pull_cli(
    request: pytest.FixtureRequest,
) -> bool | None:
    return None if request.param is None else bool(request.param)


@pytest.fixture(name="git_sign_with_ssh_cli", params=[None])
def fixture_git_sign_with_ssh_cli(
    request: pytest.FixtureRequest,
) -> bool | None:
    return None if request.param is None else bool(request.param)


@pytest.fixture(name="ssh_key_cli", params=[None])
def fixture_ssh_key_cli(
    request: pytest.FixtureRequest, tmp_path: Path
) -> str | None:
    param = request.param
    if param is None:
        return None
    return str(tmp_path.joinpath(param))


@pytest.fixture(name="bashrc_text_cli")
def fixture_bashrc_text_cli() -> str:
    return ""


@pytest.fixture(name="bashrc_cli", params=[None])
def fixture_bashrc_cli(
    request: pytest.FixtureRequest, tmp_path: Path, bashrc_text_cli: str
) -> str | None:
    param = request.param
    if param is None:
        return None

    bashrc = Path(tmp_path, param)
    with bashrc.open(mode="w", encoding="utf-8") as file:
        file.write(bashrc_text_cli)
    return str(bashrc)


@pytest.fixture(name="software_scripts_tuples_cli", params=[None])
def fixture_software_scripts_tuples_cli(
    request: pytest.FixtureRequest, datadir: Path
) -> list[tuple[str, str | None, str | None, str | None, str | None]] | None:
    software_scripts_tuples: list[
        tuple[str, str | None, str | None, str | None, str | None]
    ] = []
    param = request.param
    if param is None:
        return None
    assert isinstance(param, Iterable)
    for script, template, module, version, args in param:
        combined_args = " ".join(args) if args else None
        software_scripts_tuples.append(
            (
                str(Path(datadir, script)),
                str(template) if template else None,
                str(module) if module else None,
                str(version) if version else None,
                f"'{combined_args}'" if combined_args else None,
            )
        )

    return software_scripts_tuples


@pytest.fixture(name="software_scripts_cli")
def fixture_software_scripts_cli(
    software_scripts_tuples_cli: list[
        tuple[str, str | None, str | None, str | None, str | None]
    ]
    | None,
) -> list[str]:
    if not software_scripts_tuples_cli:
        return []
    items: list[str] = []
    for item in software_scripts_tuples_cli:
        items.append(":".join(x or "" for x in item))
    return items


@pytest.fixture(name="allowed_signers")
def fixture_allowed_signers(tmp_home: Path) -> str:
    return str(Path(tmp_home, ".ssh/allowed_signers"))


@pytest.fixture(name="configure_git")
def fixture_configure_git(
    git: str | None,
    tmp_home: Path,
    git_config_file_cli: str,
    git_user_name_cli: str | None,
    git_email_cli: str | None,
    git_editor_cli: str | None,
    git_rebase_on_pull_cli: bool | None,
    git_sign_with_ssh_cli: bool,
    ssh_key_cli: str | None,
    allowed_signers: str,
) -> Generator[dict[str, Any], None, None]:
    old_config = _get_git_config(git, git_config_file_cli)
    new_config = {
        "user.name": git_user_name_cli,
        "user.email": git_email_cli,
        "core.editor": git_editor_cli,
        "pull.rebase": None
        if git_rebase_on_pull_cli is None
        else str(git_rebase_on_pull_cli).lower(),
    }
    if (
        git_email_cli
        and ssh_key_cli
        and git_sign_with_ssh_cli
        and allowed_signers
    ):
        new_config["gpg.format"] = "ssh"
        new_config["user.signingkey"] = ssh_key_cli
        new_config["commit.gpgsign"] = "true"
        new_config["gpg.ssh.allowedsignersfile"] = allowed_signers

    try:
        configure_git(
            git=git,
            home=tmp_home,
            git_config_file=git_config_file_cli,
            user_name=git_user_name_cli,
            email=git_email_cli,
            editor=git_editor_cli,
            rebase_on_pull=git_rebase_on_pull_cli,
            sign_with_ssh=git_sign_with_ssh_cli,
            ssh_key=ssh_key_cli,
            _allowed_signers=allowed_signers,
        )
        yield new_config
    finally:
        _reset_git_config(git, git_config_file_cli, old_config, **new_config)
        if git_email_cli and ssh_key_cli and allowed_signers:
            Path(allowed_signers).unlink()


# False booleans
@pytest.fixture(name="cli_options")
def fixture_cli_options(  # noqa: C901, PLR0912
    verbosity_cli: int | None,
    config_file_cli: str | None,
    check_cli: bool | None,
    software_home_cli: str | None,
    support_file_home_cli: str | None,
    module_home_cli: str | None,
    python_venv_cli: str | None,
    python_packages_cli: list[str],
    python_requirements_cli: list[str],
    python_repos_cli: list[str],
    git_config_file_cli: str | None,
    git_user_name_cli: str | None,
    git_email_cli: str | None,
    git_editor_cli: str | None,
    git_rebase_on_pull_cli: bool | None,
    git_sign_with_ssh_cli: bool | None,
    ssh_key_cli: str | None,
    bashrc_cli: str | None,
    software_scripts_cli: list[str],
    git: str | None,
) -> dict[str, Any]:
    cli_options: dict[str, Any] = {}

    # Only add value to dictionary if set
    if verbosity_cli is not None:
        cli_options["verbosity"] = verbosity_cli
    if config_file_cli is not None:
        cli_options["config_file"] = config_file_cli
    if check_cli is not None:
        cli_options["check"] = check_cli
    if software_home_cli is not None:
        cli_options["software_home"] = software_home_cli
    if support_file_home_cli is not None:
        cli_options["support_file_home"] = support_file_home_cli
    if module_home_cli is not None:
        cli_options["module_home"] = module_home_cli
    if python_venv_cli is not None:
        cli_options["python_venv"] = python_venv_cli
    if python_packages_cli:
        cli_options["python_packages"] = python_packages_cli
    if python_requirements_cli:
        cli_options["python_requirements"] = python_requirements_cli
    if python_repos_cli:
        cli_options["python_repos"] = python_repos_cli
    if git_config_file_cli is not None:
        cli_options["git_config_file"] = git_config_file_cli
    if git_user_name_cli is not None:
        cli_options["git_user_name"] = git_user_name_cli
    if git_email_cli is not None:
        cli_options["git_email"] = git_email_cli
    if git_editor_cli is not None:
        cli_options["git_editor"] = git_editor_cli
    if git_rebase_on_pull_cli is not None:
        cli_options["git_rebase_on_pull"] = git_rebase_on_pull_cli
    if git_sign_with_ssh_cli is not None:
        cli_options["git_sign_with_ssh"] = git_sign_with_ssh_cli
    if ssh_key_cli is not None:
        cli_options["ssh_key"] = ssh_key_cli
    if bashrc_cli is not None:
        cli_options["bashrc"] = bashrc_cli
    if software_scripts_cli:
        cli_options["software_scripts"] = software_scripts_cli

    # Always set these options when testing to prevent unexpected behaviour
    # due to default value
    cli_options["_git"] = git
    return cli_options


@pytest.fixture(name="cli_command")
def fixture_cli_command(cli_options: dict[str, Any]) -> list[str]:  # noqa: C901, PLR0912
    cli_command: list[str] = []

    for key, value in cli_options.items():
        k = key[1:] if key.startswith("_") else key
        option = f"--{k.replace('_', '-')}"

        if isinstance(value, bool):
            option = f"--no{option[1:]}" if not value else option
            cli_command.append(option)
        elif not value:
            continue
        elif key == "verbosity":
            cli_command.extend("-v" for _ in range(value))
        elif isinstance(value, str):
            cli_command.extend([option, value])
        elif isinstance(value, list):
            if key == "python_packages":
                option = "-p"
            elif key == "python_requirements":
                option = "-r"
            elif key == "software_scripts":
                option = "-s"
            elif key == "python_repos":
                option = "-c"
            else:
                raise RuntimeError
            for v in value:
                cli_command.extend([option, str(v)])
        else:
            raise RuntimeError

    return shlex.split(" ".join(cli_command))


@pytest.fixture(name="stdout")
def fixture_stdout() -> TextIO:
    return StringIO()


@pytest.fixture(name="stderr")
def fixture_stderr() -> TextIO:
    return StringIO()


# Unpack Fixtures
@pytest.fixture(name="create_directories")
def fixture_create_directories(
    capsys: pytest.CaptureFixture[str],
    software_home_cli: str,
    support_file_home_cli: str,
    module_home_cli: str,
    verbosity_cli: int,
    stderr: TextIO,
) -> Generator[None, None, None]:
    to_create = [
        Path(software_home_cli),
        Path(support_file_home_cli),
        Path(module_home_cli),
    ]
    create_directories(
        *to_create,
        verbosity=verbosity_cli,
    )
    stderr.write("\n".join(capsys.readouterr()))
    yield None
    for p in to_create:
        shutil.rmtree(p)


@pytest.fixture(name="clone_repos")
def fixture_clone_repos(
    python_repos_config: list[str],
    python_repos_cli: list[str],
    git: str | None,
    support_file_home_cli: str,
) -> Generator[None, None, None]:
    to_clone = (python_repos_config or []) + (python_repos_cli or [])
    dest = Path(support_file_home_cli)
    dest.mkdir(parents=False, exist_ok=True)
    clone_repos(git=git, to_clone=to_clone, dest=dest)
    yield None
    shutil.rmtree(dest)


@pytest.fixture(name="software_name")
def fixture_software_name() -> str:
    return "test_software"


@pytest.fixture(name="support_file_name")
def fixture_support_file_name() -> str:
    return "support_file.txt"


@pytest.fixture(name="script")
def fixture_script() -> str:
    return "script.sh"


@pytest.fixture(name="template")
def fixture_template() -> str:
    return "template.j2"


@pytest.fixture(name="module")
def fixture_module() -> str:
    return "module"


@pytest.fixture(name="version")
def fixture_version() -> str:
    return "0.0.1"


@pytest.fixture(name="script_args")
def fixture_script_args() -> list[str]:
    return ["arg"]


@pytest.fixture(name="software_script")
def fixture_software_script(
    script: str,
    template: str | None,
    module: str | None,
    version: str | None,
    script_args: list[str],
) -> str:
    args = " ".join(script_args)
    args = f"'{args}'"
    return f"{script}:{template or ''}:{module or ''}:{version or ''}:{args}"


@pytest.fixture(name="installation_script")
def fixture_installation_script(tmp_path: Path) -> Path:
    return Path(tmp_path, "installation_script.sh")


@pytest.fixture(name="write_installation_script")
def fixture_write_installation_script(
    software_name: str,
    support_file_name: str,
    installation_script: Path,
) -> Generator[None, None, None]:
    script_text = """#!/usr/bin/env bash
    software_name=XXX
    support_file_name=YYY
    software_home=$1
    support_file_home=$2
    shift 2

    mkdir -p "${software_home}/${software_name}"
    mkdir -p "${support_file_home}/${software_name}"

    for i in $@; do
    touch "${software_home}/${software_name}"/testfile_${i}.txt
    done

    i=0
    while true; do
    if [[ i -gt 10000 ]]; then break; fi
    echo "1" >> "${support_file_home}/${software_name}/${support_file_name}"
    ((i++))
    done\n
    """
    script_text = script_text.replace("XXX", software_name)
    script_text = script_text.replace("YYY", support_file_name)
    with installation_script.open(mode="w", encoding="utf-8") as file:
        file.write(script_text)
    installation_script.chmod(stat.S_IRWXU)
    yield None
    installation_script.unlink()
