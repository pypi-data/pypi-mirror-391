from pathlib import Path

import pytest

from cluster_setup.install import install_software


@pytest.fixture(name="num_files_to_create")
def fixture_num_files_to_create() -> int:
    return 10


@pytest.fixture(name="script_args")
def fixture_script_args(num_files_to_create: int) -> list[str]:
    script_args = [
        "{software_home}",
        "{support_file_home}",
        *[str(i) for i in range(num_files_to_create)],
    ]
    return script_args


@pytest.fixture(name="install_software")
def fixture_install_software(
    software_home_cli: str,
    support_file_home_cli: str,
    python_venv_cli: str,
    installation_script: Path,
    script_args: list[str],
    create_directories: None,  # noqa: ARG001
    write_installation_script: None,  # noqa: ARG001
) -> None:
    install_software(
        installation_script,
        software_home_cli,
        support_file_home_cli,
        python_venv_cli,
        *script_args,
    )


@pytest.mark.heavy
@pytest.mark.usefixtures("install_software")
class TestInstallSoftware:
    @staticmethod
    def test_should_create_named_directory_in_software_home(
        software_home_cli: str, software_name: str
    ) -> None:
        assert Path(software_home_cli, software_name).exists()

    @staticmethod
    def test_should_create_named_directory_in_support_file_home(
        support_file_home_cli: str, software_name: str
    ) -> None:
        assert Path(support_file_home_cli, software_name).exists()

    @staticmethod
    def test_should_create_specified_number_of_files_in_software_subdirectory(
        software_home_cli: str, software_name: str, num_files_to_create: int
    ) -> None:
        files = [
            f
            for f in Path(software_home_cli, software_name).iterdir()
            if f.is_file()
        ]
        assert len(files) == num_files_to_create

    @staticmethod
    def test_should_create_support_file(
        support_file_home_cli: str, software_name: str, support_file_name: str
    ) -> None:
        assert Path(
            support_file_home_cli, software_name, support_file_name
        ).exists()
