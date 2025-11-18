from collections.abc import Generator
from pathlib import Path

import pytest

from cluster_setup.templating import template_file
from cluster_setup.templating import write_bash_profile
from cluster_setup.templating import write_bashrc

_bashrc_text = """
software_home={{ software_home }}
module_home={{ module_home }}
support_file_home={{ support_file_home }}
python_venv={{ python_venv }}
"""


@pytest.fixture(name="bashrc_text_cli")
def fixture_bashrc_text_cli() -> str:
    return _bashrc_text


@pytest.mark.usefixtures("write_bash_profile", "write_bashrc")
class TestWriteBashFiles:
    @staticmethod
    @pytest.fixture(name="write_bash_profile")
    def fixture_write_bash_profile(
        tmp_home: Path,
    ) -> Generator[None, None, None]:
        dest = Path(tmp_home, ".bash_profile")
        write_bash_profile(dest)
        yield None
        dest.unlink()

    @staticmethod
    @pytest.fixture(name="write_bashrc")
    def fixture_write_bashrc(
        tmp_home: Path,
        bashrc_cli: str | None,
        python_venv_cli: str,
        module_home_cli: str,
        software_home_cli: str,
        support_file_home_cli: str,
    ) -> Generator[Path, None, None]:
        filename = Path(tmp_home, ".bashrc")
        write_bashrc(
            filename=filename,
            template_filename=bashrc_cli,
            python_venv=Path(software_home_cli, python_venv_cli),
            module_home=module_home_cli,
            software_home=software_home_cli,
            support_file_home=support_file_home_cli,
        )
        yield filename
        filename.unlink()

    @staticmethod
    def test_should_write_bash_profile(tmp_home: Path) -> None:
        assert Path(tmp_home, ".bash_profile").exists()

    @staticmethod
    def test_should_write_bashrc(tmp_home: Path) -> None:
        assert Path(tmp_home, ".bashrc").exists()

    @staticmethod
    @pytest.mark.parametrize("bashrc_cli", [None])
    def test_should_write_default_bashrc_if_no_template_provided(
        write_bashrc: Path, software_home_cli: str
    ) -> None:
        with write_bashrc.open(mode="r", encoding="utf-8") as file:
            text = file.read()

        assert "activate_env" in text
        assert software_home_cli in text

    @staticmethod
    @pytest.mark.parametrize("bashrc_cli", ["bashrc.j2"], indirect=True)
    def test_should_use_bashrc_template_if_provided(
        write_bashrc: Path,
        software_home_cli: str,
        support_file_home_cli: str,
        module_home_cli: str,
        python_venv_cli: str,
    ) -> None:
        with write_bashrc.open(mode="r", encoding="utf-8") as file:
            text = file.read()

        python_venv = str(Path(software_home_cli, python_venv_cli))

        assert software_home_cli in text
        assert support_file_home_cli in text
        assert module_home_cli in text
        assert python_venv in text


_template_text = """
TEST_VAR={{ sample_text }}\n
"""


@pytest.fixture(name="template_filename")
def fixture_template_filename(tmp_home: Path) -> Path:
    template_filename = Path(tmp_home, "testfile")

    with template_filename.open(mode="w", encoding="utf-8") as f:
        f.write(_template_text)

    return template_filename


@pytest.fixture(name="sample_text")
def fixture_sample_text() -> str:
    return "this should be in the templated result"


@pytest.fixture(name="template_file")
def fixture_template_file(
    template_filename: Path, sample_text: str
) -> Generator[Path, None, None]:
    template_file(
        filename=template_filename,
        template_filename=template_filename,
        verbosity=0,
        sample_text=sample_text,
    )
    yield template_filename
    template_filename.unlink()


class TestShouldTemplateFile:
    @staticmethod
    def test_should_create_templated_file_with_correct_text(
        template_file: Path, sample_text: str
    ) -> None:
        with template_file.open(mode="r", encoding="utf-8") as file:
            file_text = file.read()

        assert sample_text in file_text
