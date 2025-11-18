from collections.abc import Generator
from pathlib import Path
from typing import Any
from typing import TextIO

import pytest

from cluster_setup.config import _PATH_OPTIONS
from cluster_setup.config import create_config_file
from cluster_setup.config import parse_config_file
from cluster_setup.config import tokenize_software_script
from cluster_setup.options import Options
from cluster_setup.options import SoftwareScript


@pytest.mark.usefixtures("write_requirements_config", "write_config_file")
@pytest.mark.parametrize(
    (
        "check_config",
        "software_home_config",
        "support_file_home_config",
        "module_home_config",
        "python_venv_config",
        "python_packages_config",
        "python_requirements_packages_config",
        "python_requirements_config",
        "python_repos_config",
        "git_config_file_config",
        "git_user_name_config",
        "git_email_config",
        "git_editor_config",
        "git_rebase_on_pull_config",
        "git_sign_with_ssh_config",
        "ssh_key_config",
        "bashrc_config",
        "software_scripts_tuples_config",
    ),
    [
        (
            True,
            "software",
            "support_files",
            "modules",
            "venv",
            ["mypy-upgrade"],
            ["python-comp-chem-utils"],
            ["requirements.txt"],
            ["gitlab.com:ugognw/python-comp-chem-utils.git"],
            ".gitconfig",
            "John Doe",
            "john_doe@example.com",
            "nano",
            True,
            True,
            ".ssh/id_rsa.pub",
            ".bashrc",
            [("script.sh", "template.j2", "module", "v1", "")],
        )
    ],
    indirect=True,
)
class TestParseConfigFile:
    @staticmethod
    def test_should_read_values_from_config_file(
        config_options: dict[str, Any],
        config_file_cli: str,
    ) -> None:
        options = Options()
        parse_config_file(options=options, filename=config_file_cli)
        values_read_correctly = []

        for key, value in config_options.items():
            if (
                value is not None
                and key not in _PATH_OPTIONS
                and key != "software_scripts"
            ):
                values_read_correctly.append(getattr(options, key) == value)

        assert all(values_read_correctly)

    @staticmethod
    @pytest.mark.parametrize("config_file_text", [""])
    def test_should_print_error_for_invalid_config_file(
        capsys: pytest.CaptureFixture[str],
        config_options: dict[str, Any],  # noqa: ARG004
        config_file_cli: str,
    ) -> None:
        error_msg = (
            f"No cluster-setup configuration found in {config_file_cli}"
        )
        options = Options()
        parse_config_file(options=options, filename=config_file_cli)
        output = capsys.readouterr().out
        assert error_msg in output


@pytest.mark.usefixtures("write_config_file")
class TestParseConfigFileConversion:
    @staticmethod
    @pytest.mark.parametrize(
        (
            "software_home_config",
            "support_file_home_config",
            "module_home_config",
            "git_config_file_config",
            "ssh_key_config",
            "bashrc_config",
        ),
        [
            (
                "~/software",
                "~/support_files",
                "~/modules",
                "~/.gitconfig",
                "~/.ssh/id_ed25519.pub",
                "~/.bashrc",
            )
        ],
    )
    def test_should_convert_paths_to_absolute_paths(
        write_requirements_config: None,  # noqa: ARG004
        config_options: dict[str, Any],
        config_file_cli: str,
    ) -> None:
        options = Options()
        parse_config_file(options=options, filename=config_file_cli)
        paths_absolute = []

        for key, _ in config_options.items():
            if key in _PATH_OPTIONS:
                paths_absolute.append(
                    Path(getattr(options, key)).is_absolute()
                )

        assert all(paths_absolute)

    @staticmethod
    @pytest.mark.parametrize(
        ("python_requirements_config", "num_requirements_files"),
        [(["requirements*.txt"], 4)],
    )
    def test_should_expand_patterns_from_globs(
        monkeypatch: pytest.MonkeyPatch,
        write_config_file: None,  # noqa: ARG004
        config_file_cli: str,
        tmp_home: Path,
        num_requirements_files: int,
        python_requirements_config: list[str],
    ) -> None:
        # Create multiple requirements files matching a glob pattern
        pattern = python_requirements_config[0]
        for i in range(num_requirements_files):
            Path(tmp_home, pattern.replace("*", f"_{i}")).touch()

        # Parse the config file
        with monkeypatch.context() as m:
            m.chdir(tmp_home)
            options = Options()
            parse_config_file(options=options, filename=config_file_cli)

        # Check that all three paths appear in the options object
        assert len(options.python_requirements) == num_requirements_files


@pytest.mark.usefixtures("write_config_file")
class TestParseConfigSoftwareScripts:
    @staticmethod
    @pytest.fixture(name="software_scripts_config")
    def fixture_software_scripts_config(software_script: str) -> list[str]:
        return [software_script]

    @staticmethod
    def test_should_tokenize_software_script_spec_correctly(
        config_file_cli: str,
        script: str,
        template: str | None,
        module: str | None,
        version: str | None,
        script_args: list[str],
    ) -> None:
        options = Options()
        parse_config_file(options=options, filename=config_file_cli)
        assert options.software_scripts[0] == (
            script,
            template,
            module,
            version,
            script_args,
        )


class TestCreateConfigFile:
    @staticmethod
    @pytest.fixture(name="created_config_file")
    def fixture_created_config_file(
        tmp_path: Path,
    ) -> Generator[Path, None, None]:
        created_config_file = create_config_file(tmp_path)
        yield created_config_file
        created_config_file.unlink()

    @staticmethod
    def test_should_create_file(created_config_file: Path) -> None:
        assert created_config_file.exists()

    @staticmethod
    def test_should_create_valid_toml_file(
        created_config_file: Path, stderr: TextIO
    ) -> None:
        options = Options()
        parse_config_file(options, str(created_config_file), stderr=stderr)
        stderr.seek(0)
        assert stderr.read() == ""


class TestTokenizeSoftwareScript:
    @staticmethod
    @pytest.fixture(name="parsed_software_script")
    def fixture_parsed_software_script(software_script: str) -> SoftwareScript:
        parsed_software_script = tokenize_software_script(software_script)
        return parsed_software_script

    @staticmethod
    def test_should_parse_all_sections_correctly(
        parsed_software_script: SoftwareScript,
        script: str,
        template: str | None,
        module: str | None,
        version: str | None,
        script_args: list[str],
    ) -> None:
        assert parsed_software_script == (
            script,
            template,
            module,
            version,
            script_args,
        )

    @staticmethod
    @pytest.mark.parametrize("version", [None])
    def test_should_parse_default_version_when_version_not_set(
        parsed_software_script: SoftwareScript,
    ) -> None:
        assert parsed_software_script[3] == "0.0.1"

    @staticmethod
    @pytest.mark.parametrize("module", [None])
    def test_should_determine_module_name_from_template_if_provided(
        parsed_software_script: SoftwareScript, template: str
    ) -> None:
        assert parsed_software_script[2] == template.removesuffix(".j2")

    @staticmethod
    @pytest.mark.parametrize("software_script", ["script.sh"])
    def test_should_parse_script_and_args_if_only_script_provided(
        parsed_software_script: SoftwareScript,
    ) -> None:
        assert parsed_software_script[0] == "script.sh"
        assert parsed_software_script[-1] == []
