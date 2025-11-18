"""This module can be used to run the test suite."""

from collections.abc import Iterable

try:
    import pytest
except ImportError:
    pytest = None  # type: ignore[assignment]


def run_tests(args: Iterable[str]) -> bool:
    """Run the test suite.

    Args:
        args: An iterable of command-line arguments to pass to
            `pytest`.

    Returns:
        Whether or not all tests pass.

    Raises:
        RuntimeError: pytest is not installed.
    """
    if pytest is None:
        msg = "pytest is not installed"
        raise RuntimeError(msg)

    package = __name__.removeprefix("src.").split(".")[0]
    args = [
        "--import-mode",
        "importlib",
        "-r",
        "A",
        "--tb",
        "short",
        "-n",
        "auto",
        "-m",
        "not recursive",
        "-W",
        "ignore::_pytest.warning_types.PytestUnknownMarkWarning",
        *args,
        "--pyargs",
        package,
    ]
    return pytest.main(args) == 0
