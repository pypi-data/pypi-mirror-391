"""This module defines the command-line interface."""

import argparse
from contextlib import redirect_stdout
import datetime
from io import StringIO
from pathlib import Path
import re
from typing import Any
from typing import TextIO

from cluster_setup.__about__ import __version__
from cluster_setup.config import create_config_file
from cluster_setup.config import expand_pattern
from cluster_setup.config import parse_config_file
from cluster_setup.config import resolve_path
from cluster_setup.config import tokenize_software_script
from cluster_setup.options import Options
from cluster_setup.options import validate_options
from cluster_setup.test import run_tests

_EPILOG_TEXT = """
\n
Specifying Software Scripts
---------------------------

Software scripts are specified as five-component, colon-separated strings
structured as

    SCRIPT[:[TEMPLATE]:[MODULE]:[VERSION]:[ARGS]]

SCRIPT must be a path to an executable script. TEMPLATE, MODULE,
VERSION, and ARGS are optional. TEMPLATE must point to a Jinja2 template file
for the modulefile; the template context will contain the software and support
file home directories as variables in addition to VERSION. If TEMPLATE is
omitted, then no modulefile will be created. MODULE should be the desired name
of the module. If omitted, then the stem of TEMPLATE will be used. VERSION
should be the version used for the module. If omitted, '0.0.1' is used. ARGS
should be the command line arguments to be passed to the script. The software
and support file home directories and Python environment directory can be
specified using Python template string syntax. For example,

cluster-setup --software-script install_vasp.sh:vasp.j2:vasp:6.3.2:{software_home} vasp.tar.gz

will run the 'install_vasp.sh' script (with the default software home, and
'vasp.tar.gz' as arguments) and create a modulefile (using the 'vasp.j2'
template) for 'vasp' version '6.3.2', and

cluster-setup --software-script install_vasp.sh:vasp.j2:::{python_venv} vasp.tar.gz

will run the install_vasp.sh script (with the Python environment directory and
'vasp.tar.gz' as arguments) and create a modulefile
(using the vasp.j2 template) for vasp version 0.0.1.
"""


class _ExpandPattern(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,  # noqa: ARG002
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,  # noqa: ARG002
    ) -> None:
        dest = getattr(namespace, self.dest)
        assert isinstance(dest, list)
        assert isinstance(values, str)
        dest.extend(expand_pattern(values))


class _GenerateConfig(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,  # noqa: ARG002
        values: Any,  # noqa: ARG002
        option_string: str | None = None,  # noqa: ARG002
    ) -> None:
        config = create_config_file()
        parser.exit(message=f"New configuration file written to: {config}")


class _RunTests(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,  # noqa: ARG002
        values: Any,
        option_string: str | None = None,  # noqa: ARG002
    ) -> None:
        print("Running tests...")
        try:
            with StringIO() as buffer, redirect_stdout(buffer):
                failed = run_tests(values)
                text = buffer.getvalue()
        except RuntimeError:
            parser.exit(
                status=1,
                message="Unable to run tests without pytest. Install the "
                "'test' extra (e.g., pip install .[test])",
            )

        if failed:
            message = "Success! All tests passed."
        else:
            message = "Failure! Some tests failed."

        print(message)
        tz = datetime.timezone.utc  # noqa: UP017 # no alias until Python <3.11
        time_stamp = re.sub(
            "[-:.+]",
            "_",
            datetime.datetime.now(tz).isoformat(sep="_"),
        )
        filename = f"report_{time_stamp}.txt"

        with Path(filename).open(mode="w", encoding="utf-8") as f:
            f.write(text)

        print(f"Report saved to: {filename}")

        parser.exit()


def process_options(
    args: list[str] | None = None,
    stderr: TextIO | None = None,
) -> Options:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(
        "cluster-setup",
        description="Set up a Digital Research Alliance of Canada cluster "
        "account.",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
        usage="%(prog)s [-h|-v|-V|-g|-t] [more options; see below]",
        epilog=_EPILOG_TEXT,
    )
    general_group = parser.add_argument_group("General options")
    general_group.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit."
    )
    general_group.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=1,
        dest="verbosity",
        help="More verbose messages.",
    )
    general_group.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the program version number and exit.",
    )
    general_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform the setup steps for the installation but do not\n"
        "actually install anything. (Not yet supported)",
    )
    general_group.add_argument(
        "--check",
        action="store_true",
        default=True,
        help="Perform pre-installation checks. This is the default.\n"
        "Forego checks with '--no-check'.",
    )
    general_group.add_argument(
        "--no-check",
        action="store_false",
        dest="check",
        help=argparse.SUPPRESS,
    )
    general_group.add_argument(
        "-t",
        "--test",
        action=_RunTests,
        metavar="PYTEST_ARGS",
        nargs="*",
        help="Run the test suite and exit. Option arguments are forwarded to "
        "pytest.",
    )

    config_group = parser.add_argument_group(
        title="Config file",
        description=(
            "Use a config file instead of command line arguments.\n"
            "This is useful if you are using many flags or want to\n"
            "transfer a configuration from one cluster to another."
        ),
    )
    config_group.add_argument(
        "--config-file",
        help="Specify a configuration TOML file, must have a [cluster-setup]\n"
        "or [tool.cluster-setup] section.",
        type=resolve_path,
    )
    config_group.add_argument(
        "-g",
        "--config-gen",
        action=_GenerateConfig,
        nargs=0,
        help="Generate a configuration file with default values and exit.",
    )

    directories_group = parser.add_argument_group(
        title="Installation directories",
        description="Specify installation directories",
    )
    directories_group.add_argument(
        "--software-home",
        help=(
            "The location in which to install software.\n"
            "Defaults to ~/software."
        ),
        default=str(Path(Path.home(), "software").expanduser()),
        type=resolve_path,
    )
    directories_group.add_argument(
        "--support-file-home",
        help=(
            "The location in which to install support files.\n"
            "Defaults to ~/support_files."
        ),
        default=str(Path(Path.home(), "support_files").expanduser()),
        type=resolve_path,
    )
    directories_group.add_argument(
        "--module-home",
        help=(
            "The location in which to install modules.\nDefaults to ~/modules."
        ),
        default=str(Path(Path.home(), "modules").expanduser()),
        type=resolve_path,
    )

    python_group = parser.add_argument_group(
        title="Python virtual environment",
        description="Configure the Python virtual environment",
    )
    python_group.add_argument(
        "--venv",
        "--python-venv",
        help=(
            "The name of the Python virtual environment to create.\n"
            "The environment will be created in a subdirectory relative\n"
            "to the software home. Defaults to python_venv."
        ),
        default="python_venv",
        dest="python_venv",
        metavar="VENV",
    )
    python_group.add_argument(
        "-p",
        "--package",
        action="append",
        help=(
            "The name of a Python package to install into the virtual\n"
            "environment. This option may be repeated."
        ),
        dest="python_packages",
        metavar="PACKAGE",
    )
    python_group.add_argument(
        "-r",
        "--requirements",
        action=_ExpandPattern,
        help=(
            "The path to a requirements.txt file specifying Python packages\n"
            "to install. Relative glob patterns are supported. This option\n"
            "may be repeated."
        ),
        default=[],
        dest="python_requirements",
        metavar="PATTERN",
    )
    python_group.add_argument(
        "-c",
        "--clone-repo",
        action="append",
        dest="python_repos",
        default=[],
        help="A repository to clone. For example: DOMAIN:USER/REPO.git\n"
        "This option may be repeated.",
        metavar="REPO",
    )

    git_group = parser.add_argument_group(
        title="Git configuration",
        description="Configure git version control",
    )
    git_group.add_argument("--git", dest="_git", help=argparse.SUPPRESS)
    git_group.add_argument(
        "--git-config-file",
        help=(
            "The file to be used to configure git. Defaults to the global\n"
            "config file."
        ),
        type=resolve_path,
    )
    git_group.add_argument("--git-user-name", help="Set your git user name.")
    git_group.add_argument("--git-email", help="Set your git user email.")
    git_group.add_argument("--git-editor", help="Set your git editor.")
    git_group.add_argument(
        "--git-rebase-on-pull",
        action="store_true",
        help=(
            "Rebase git branches when pulling from upstream branch.\n"
            "Defaults to False."
        ),
        default=str(Path("~/.gitconfig").expanduser()),
    )
    git_group.add_argument(
        "--sign-with-ssh",
        "--git-sign-with-ssh",
        help=(
            "Sign git commits with ssh. You must specify a file containing\n"
            "an ssh public key with the --ssh-key option.\n"
            "Do not sign commits with ssh with the '--no-sign-with-ssh',\n"
            "which is the default."
        ),
        action="store_true",
        default=False,
    )
    git_group.add_argument(
        "--no-sign-with-ssh",
        action="store_false",
        dest="sign_with_ssh",
        help=argparse.SUPPRESS,
    )
    git_group.add_argument(
        "--ssh-key",
        help=(
            "The file containing your ssh public key. Make sure you have\n"
            "created an ssh key with 'ssh-keygen' first."
        ),
        type=resolve_path,
    )

    software_group = parser.add_argument_group(
        title="Software",
        description="Configure software installation",
    )
    software_group.add_argument(
        "--bashrc",
        help=(
            "A Jinja2 template file to be used to write the .bashrc file. A\n"
            "minimal .bashrc file will be written if omitted."
        ),
        type=resolve_path,
    )
    # ! NEVER SUPPORT GLOB PATTERNS HERE. IT IS A SIGNIFICANT SECURITY RISK
    # ! SINCE THESE FILES ARE RUN WITH BASH
    software_group.add_argument(
        "-s",
        "--software-script",
        action="append",
        dest="software_scripts",
        default=[],
        help="Specify software to be installed via scripts and optionally\n"
        "create modulefiles from templates. See 'Specifying Software Scripts'\n"
        "below for a detailed description of formatting.",
        type=tokenize_software_script,
    )

    dummy = argparse.Namespace()
    parser.parse_args(args, dummy)
    config_file = dummy.config_file
    # taken from mypy.main.process_options
    if config_file is not None and not Path(config_file).exists():
        parser.error(f"Cannot find config file '{config_file}'")

    options = Options()
    # Parse config file first, so command line can override.
    if config_file:
        parse_config_file(options, config_file, stderr)

    parser.parse_args(args, options)

    if options.check:
        validate_options(options)

    return options
