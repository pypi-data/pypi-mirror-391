from collections.abc import Generator
from collections.abc import Iterable
from pathlib import Path
import shutil
from typing import Any

import pytest

from cluster_setup.git import _construct_git_signer_text
from cluster_setup.git import _get_git_config
from cluster_setup.options import _REPO_RE
from cluster_setup.options import _validate_ssh_key

_repos = [
    "github.com:ugognw/mypy-upgrade.git",
    "gitlab.com:ugognw/python-comp-chem-utils.git",
]


@pytest.fixture(name="python_repos_config", params=[[_repos[0]]])
def fixture_python_repos_config(request: pytest.FixtureRequest) -> list[str]:
    param = request.param
    if not param or not isinstance(param, Iterable):
        return []
    return [str(p) for p in request.param]


@pytest.fixture(name="python_repos_cli", params=[[_repos[1]]])
def fixture_python_repos_cli(request: pytest.FixtureRequest) -> list[str]:
    param = request.param
    if not param or not isinstance(param, Iterable):
        return []
    return [str(p) for p in request.param]


@pytest.mark.skipif(shutil.which("git") is None, reason="git not found")
@pytest.mark.usefixtures("configure_git")
class TestConfigureGit:
    @staticmethod
    def test_should_set_all_values_correctly(
        configure_git: dict[str, Any],
        git_config_file_cli: str,
        git: str | None,
    ) -> None:
        current_config = _get_git_config(git, git_config_file_cli)
        values_set_correctly = []
        for key, value in configure_git.items():
            values_set_correctly.append(
                # This first condition is effective so long as the default
                # values for all config options are falsey
                not value or value == current_config[key]
            )

        assert all(values_set_correctly)


@pytest.mark.heavy
@pytest.mark.skipif(shutil.which("git") is None, reason="git not found")
class TestConfigureGitWithSSH(TestConfigureGit):
    @staticmethod
    @pytest.fixture(name="git_sign_with_ssh_cli")
    def fixture_git_sign_with_ssh_cli() -> bool:
        return True

    @staticmethod
    @pytest.fixture(name="ssh_key_cli")
    def fixture_ssh_key_cli(
        tmp_home: Path, git_email_cli: str
    ) -> Generator[str, None, None]:
        ssh_key = tmp_home.joinpath(".ssh/id_ed25519.pub")
        try:
            ssh_key.parent.mkdir(parents=True, exist_ok=True)
            with ssh_key.open(mode="w", encoding="utf-8") as file:
                file.write(f"ssh-ed25519 {'X' * 68} {git_email_cli}")
            yield str(ssh_key)
        finally:
            shutil.rmtree(ssh_key.parent)

    @staticmethod
    @pytest.fixture(name="git_email_cli")
    def fixture_git_email_cli() -> str:
        return "john_doe@example.com"

    @staticmethod
    def test_should_add_ssh_key_to_allowed_signers_file(
        ssh_key_cli: str, git_email_cli: str, allowed_signers: str
    ) -> None:
        with Path(allowed_signers).open(mode="r", encoding="utf-8") as file:
            contents = file.read()
        signer_text = _construct_git_signer_text(ssh_key_cli, git_email_cli)
        assert contents.endswith(signer_text)


@pytest.mark.heavy
@pytest.mark.skipif(shutil.which("git") is None, reason="git not found")
@pytest.mark.skipif(
    False in _validate_ssh_key(_repos),
    reason=f"ssh key not valid for repos: {', '.join(_repos)}",
)
@pytest.mark.usefixtures("clone_repos", "write_config_file")
class TestCloneRepo:
    @staticmethod
    @pytest.mark.parametrize("python_repos_cli", [None])
    def test_should_clone_repos_in_config_file(
        python_repos_config: list[str],
        support_file_home_cli: str,
    ) -> None:
        repos_cloned = []
        for repo in python_repos_config:
            match = _REPO_RE.match(repo)
            assert match is not None
            root = match.group("root")
            repos_cloned.append(Path(support_file_home_cli, root).exists())
        assert all(repos_cloned)

    @staticmethod
    @pytest.mark.parametrize("python_repos_config", [None])
    def test_should_clone_repos_from_command_line(
        python_repos_cli: list[str],
        support_file_home_cli: str,
    ) -> None:
        repos_cloned = []
        for repo in python_repos_cli:
            match = _REPO_RE.match(repo)
            assert match is not None
            root = match.group("root")
            repos_cloned.append(Path(support_file_home_cli, root).exists())
        assert all(repos_cloned)
