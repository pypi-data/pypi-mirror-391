from collections.abc import Generator
from pathlib import Path
import shutil
import subprocess

import pytest

from cluster_setup.venv import setup_venv


@pytest.mark.heavy
@pytest.mark.usefixtures("setup_venv")
class TestSetupVenv:
    @staticmethod
    @pytest.fixture(name="setup_venv")
    def fixture_setup_venv(
        software_home_cli: str,
        python_venv_cli: str,
        python_packages_cli: list[str] | None,
        python_requirements_cli: list[str] | None,
        write_requirements_cli: None,  # noqa: ARG004
    ) -> Generator[None, None, None]:
        python_venv = Path(software_home_cli, python_venv_cli)
        setup_venv(
            python_venv=python_venv,
            packages=python_packages_cli,
            requirements=python_requirements_cli,
        )
        yield None
        shutil.rmtree(python_venv)

    @staticmethod
    @pytest.fixture(name="verbosity_cli")
    def fixture_verbosity_cli() -> int:
        return 0

    @staticmethod
    @pytest.fixture(name="python_venv_cli")
    def fixture_python_venv_config() -> str:
        return ".venv"

    @staticmethod
    @pytest.fixture(name="installed_packages")
    def fixture_installed_packages(
        software_home_cli: str,
        python_venv_cli: str,
    ) -> list[str]:
        executable = Path(software_home_cli, python_venv_cli, "bin", "python")
        args: list[str | Path] = [executable, "-m", "pip", "freeze"]
        installed_packages = subprocess.check_output(  # noqa: S603
            args, stderr=subprocess.PIPE, encoding="utf-8"
        ).splitlines()
        return installed_packages

    @staticmethod
    @pytest.mark.parametrize("python_requirements_cli", [None])
    def test_should_install_packages_from_packages(
        python_packages_cli: list[str],
        installed_packages: list[str],
    ) -> None:
        packages_are_installed = []
        for p in python_packages_cli:
            packages_are_installed.append(
                any(p in line for line in installed_packages)
            )
        assert all(packages_are_installed)

    @staticmethod
    @pytest.mark.parametrize("python_packages_cli", [None])
    def test_should_install_packages_from_requirements(
        python_requirements_packages_cli: list[str],
        installed_packages: list[str],
    ) -> None:
        packages_are_installed = []
        to_be_installed = [
            p
            for packages in python_requirements_packages_cli
            for p in packages
        ]
        for p in to_be_installed:
            packages_are_installed.append(
                any(p in line for line in installed_packages)
            )
        assert all(packages_are_installed)
