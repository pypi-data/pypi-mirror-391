from io import StringIO
from typing import Any

import pytest

from cluster_setup.options import Options
from cluster_setup.options import _extract_endpoints
from cluster_setup.options import _validate_git
from cluster_setup.options import _validate_repository_uris
from cluster_setup.options import _validate_ssh_key

_repos = [
    "github.com:ugognw/mypy-upgrade.git",
    "gitlab.com:ugognw/python-comp-chem-utils.git",
]


class TestValidateGit:
    @staticmethod
    @pytest.mark.parametrize(
        ("git", "git_user_name_cli"), [(None, "test@tester.com")]
    )
    def test_should_print_warning_without_git_if_git_options_set(
        cli_options: dict[str, Any],
    ) -> None:
        msg = "git configuration will be skipped"
        file = StringIO()
        _validate_git(Options(**cli_options), stderr=file)
        file.seek(0)
        assert msg in file.read()

    @staticmethod
    @pytest.mark.parametrize(
        ("git_sign_with_ssh_cli", "git_user_name_cli"), [(True, None)]
    )
    def test_should_print_warning_if_sign_with_ssh_is_true_but_no_email_provided(
        cli_options: dict[str, Any],
    ) -> None:
        msg = "Signing with ssh will not be configured"
        file = StringIO()
        _validate_git(Options(**cli_options), stderr=file)
        file.seek(0)
        assert msg in file.read()


class TestValidateURIs:
    @staticmethod
    def test_should_return_true_for_valid_uri() -> None:
        uris = ["gitlab.com:ugognw/python-comp-chem-utils.git"]
        assert _validate_repository_uris(uris)

    @staticmethod
    def test_should_return_false_for_invalid_uri() -> None:
        uris = [""]
        assert not _validate_repository_uris(uris)


class TestExtractEndpoints:
    @staticmethod
    def test_should_extract_endpoints() -> None:
        repos = [
            "gitlab.com:ugognw/python-comp-chem-utils.git",
            "github.com:ugognw/mypy-upgrade.git",
        ]
        extracted_endpoints = _extract_endpoints(repos)
        assert "gitlab.com" in extracted_endpoints
        assert "github.com" in extracted_endpoints


@pytest.mark.heavy
class TestValidateSSHKey:
    @staticmethod
    @pytest.mark.skipif(
        False in _validate_ssh_key(_repos),
        reason=f"ssh key not valid for repos: {', '.join(_repos)}",
    )
    def test_should_return_true_with_valid_ssh_key() -> None:
        repos = [
            "gitlab.com:ugognw/python-comp-chem-utils.git",
            "github.com:ugognw/mypy-upgrade.git",
        ]
        ssh_key_valid = _validate_ssh_key(repos)
        assert all(ssh_key_valid)

    @staticmethod
    def test_should_return_false_with_invalid_ssh_key_for_endpoints() -> None:
        repos = ["notgithub.fake:ugognw/mypy-upgrade.git"]
        ssh_key_valid = _validate_ssh_key(repos)
        assert not any(ssh_key_valid)
