from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from cluster_setup.cli import process_options
from cluster_setup.main import run
from cluster_setup.options import _REPO_RE
from cluster_setup.options import _validate_ssh_key


@pytest.mark.usefixtures("write_config_file")
class TestProcessOptions:
    @staticmethod
    def test_should_parse_args_correctly(
        cli_command: list[str], cli_options: dict[str, Any]
    ) -> None:
        options = process_options(args=cli_command)
        args_parsed_correctly = []

        for key, value in cli_options.items():
            # List parameters are combined so only membership is tested
            if isinstance(value, list):
                args_parsed_correctly.append(
                    all(x in getattr(options, key) for x in value)
                )
            else:
                args_parsed_correctly.append(getattr(options, key) == value)

        assert all(args_parsed_correctly)


_repos = ["github.com:ugognw/mypy-upgrade.git"]


@pytest.mark.heavy
@pytest.mark.usefixtures("run_main")
@pytest.mark.parametrize(
    ("config_file_header", "python_venv_cli", "python_packages_cli"),
    [("tool.cluster-setup", "venv", ["mypy"])],
)
class TestMain:
    @staticmethod
    @pytest.fixture(name="run_main")
    def fixture_run_main(
        tmp_home: Path,
        cli_command: list[str],
        write_config_file: None,  # noqa: ARG004
        write_requirements_cli: None,  # noqa: ARG004
        write_installation_script: None,  # noqa: ARG004
    ) -> None:
        run(args=cli_command, home=tmp_home)

    @staticmethod
    @pytest.fixture(name="script")
    def fixture_script(installation_script: Path) -> str:
        return str(installation_script)

    @staticmethod
    @pytest.fixture(name="template")
    def fixture_template(tmp_path: Path) -> Generator[str, None, None]:
        template = Path(tmp_path, "template.j2")
        template.touch()
        yield str(template)
        template.unlink()

    @staticmethod
    @pytest.fixture(name="script_args")
    def fixture_script_args() -> list[str]:
        return ["{software_home}", "{support_file_home}"]

    @staticmethod
    @pytest.fixture(name="software_scripts_cli")
    def fixture_software_scripts_cli(software_script: str) -> list[str]:
        return [software_script]

    @staticmethod
    def test_should_create_directories(
        software_home_cli: str,
        support_file_home_cli: str,
        module_home_cli: str,
    ) -> None:
        assert Path(software_home_cli).exists()
        assert Path(support_file_home_cli).exists()
        assert Path(module_home_cli).exists()

    @staticmethod
    def test_should_create_python_venv(
        software_home_cli: str, python_venv_cli: str
    ) -> None:
        assert Path(software_home_cli, python_venv_cli).exists()

    @staticmethod
    @pytest.mark.skipif(
        False in _validate_ssh_key(_repos),
        reason="git clone requires valid ssh key",
    )
    @pytest.mark.parametrize("python_repos_cli", [_repos])
    def test_should_clone_git_repos(
        python_repos_cli: list[str], support_file_home_cli: str
    ) -> None:
        repos_cloned = []
        for repo in python_repos_cli:
            match = _REPO_RE.match(repo)
            assert match
            repo_root = match.group("root")
            repos_cloned.append(
                Path(support_file_home_cli, repo_root).exists()
            )
        assert all(repos_cloned)

    @staticmethod
    def test_should_write_bash_profile(tmp_home: Path) -> None:
        assert Path(tmp_home, ".bash_profile").exists()

    @staticmethod
    def test_should_write_bashrc(tmp_home: Path) -> None:
        assert Path(tmp_home, ".bashrc").exists()

    @staticmethod
    def test_should_install_software(
        software_home_cli: str,
        support_file_home_cli: str,
        software_name: str,
    ) -> None:
        assert Path(software_home_cli, software_name).exists()
        assert Path(support_file_home_cli, software_name).exists()

    @staticmethod
    def test_should_create_modulefile(
        module_home_cli: str,
        module: str,
    ) -> None:
        assert Path(module_home_cli, module).exists()

    @staticmethod
    @pytest.mark.recursive
    @pytest.mark.parametrize("verbosity_cli", [0])
    def test_should_run_tests_from_cli(
        tmp_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        args = ["--test", "-m", "not heavy"]
        with monkeypatch.context() as m:
            m.chdir(tmp_home)
            with pytest.raises(SystemExit, match="0"):
                run(args, home=tmp_home)
            assert next(tmp_home.glob("report_*.txt"))


@pytest.mark.heavy
@pytest.mark.parametrize(
    (
        "config_file_header",
        "python_venv_cli",
        "python_packages_cli",
        "verbosity_cli",
    ),
    [("tool.cluster-setup", "venv", ["mypy"], 0)],
)
class TestMainCleanUp:
    @staticmethod
    @pytest.mark.parametrize("git", ["/not/git"])
    def test_should_delete_all_directories_on_error(
        tmp_home: Path,
        cli_command: list[str],
        software_home_cli: str,
        support_file_home_cli: str,
        module_home_cli: str,
        write_config_file: None,  # noqa: ARG004
        write_requirements_cli: None,  # noqa: ARG004
    ) -> None:
        with pytest.raises(FileNotFoundError):
            run(args=cli_command, home=tmp_home)
        assert not Path(software_home_cli).exists()
        assert not Path(support_file_home_cli).exists()
        assert not Path(module_home_cli).exists()
