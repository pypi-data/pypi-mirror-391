"""This module contains `run`, the main entry-point for running cluster-setup.

`run` can be used to invoke `cluster-setup` as if you would call cluster-setup
from the command line.
"""

import datetime
from pathlib import Path
import re
import shutil
import sys
from typing import TextIO

from cluster_setup.cli import process_options
from cluster_setup.config import textify_config_file
from cluster_setup.git import clone_repos
from cluster_setup.git import configure_git
from cluster_setup.install import install_software
from cluster_setup.options import Options
from cluster_setup.templating import template_file
from cluster_setup.templating import write_bash_profile
from cluster_setup.templating import write_bashrc
from cluster_setup.unpack import create_directories
from cluster_setup.venv import setup_venv

_JINJA_EXT_RE = re.compile(r".+(?P<ext>\.(?:j2|jinja2?))")


def _get_directories_to_create(options: Options) -> list[Path]:
    to_create = []
    if not Path(options.software_home).exists():
        to_create.append(Path(options.software_home))
    if not Path(options.support_file_home).exists():
        to_create.append(Path(options.support_file_home))
    if not Path(options.module_home).exists():
        to_create.append(Path(options.module_home))
    return to_create


def _print_options(options: Options, stderr: TextIO | None = None) -> None:
    text = "".join(textify_config_file(options))
    print(text + "\n", file=stderr)


def run(
    args: list[str] | None = None,
    *,
    stderr: TextIO | None = None,
    home: Path | None = None,
) -> None:
    """Run `cluster-setup`.

    Args:
        args: A list of command-line arguments to `cluster-setup`. Defaults to None.
        stderr: A text file opened for writing to which the standard error will
            be written. Defaults to the standard error.
        home: The home directory to use for the setup. Defaults to `Path.home()`.
    """
    start = datetime.datetime.now(tz=datetime.timezone.utc)  # noqa: UP017
    if args is None:
        args = sys.argv[1:]

    home = home or Path.home()
    options = process_options(args=args, stderr=stderr)
    print(" Running cluster-setup ".center(80, "-"))

    if options.verbosity > 0:
        _print_options(options, stderr=stderr)

    to_create = _get_directories_to_create(options)
    to_clean = [
        *to_create,
        *[d for home in to_create for d in home.parents if not d.exists()],
    ]

    try:
        create_directories(
            *to_create,
            verbosity=options.verbosity,
            stderr=stderr,
        )
        python_venv = Path(options.software_home, options.python_venv)
        setup_venv(
            python_venv=python_venv,
            packages=options.python_packages,
            requirements=options.python_requirements,
            verbosity=options.verbosity,
            stderr=stderr,
        )
        configure_git(
            git=options._git,
            home=home,
            git_config_file=options.git_config_file,
            user_name=options.git_user_name,
            email=options.git_email,
            editor=options.git_editor,
            rebase_on_pull=options.git_rebase_on_pull,
            sign_with_ssh=options.git_sign_with_ssh,
            ssh_key=options.ssh_key,
        )
        clone_repos(
            options._git,
            options.python_repos,
            options.support_file_home,
            stderr=stderr,
        )
        bash_profile = Path(home, ".bash_profile")
        bashrc = Path(home, ".bashrc")
        to_clean.append(bash_profile)
        write_bash_profile(bash_profile)
        to_clean.append(bashrc)
        write_bashrc(
            filename=bashrc,
            template_filename=options.bashrc,
            python_venv=python_venv,
            module_home=options.module_home,
            software_home=options.software_home,
            support_file_home=options.support_file_home,
            verbosity=options.verbosity,
            stderr=stderr,
        )

        for (
            script,
            template,
            module,
            version,
            script_args,
        ) in options.software_scripts:
            install_software(
                script,
                options.software_home,
                options.support_file_home,
                python_venv,
                *script_args,
                verbosity=options.verbosity,
                stderr=stderr,
            )
            if template:
                modulefile = Path(
                    options.module_home,
                    module or _JINJA_EXT_RE.sub("", Path(template).name),
                    f"{version or '0.0.1'}.lua",
                ).expanduser()
                template_vars = {
                    "software_home": options.software_home,
                    "support_file_home": options.support_file_home,
                    "module_home": options.module_home,
                    "version": version,
                }
                template_file(
                    filename=modulefile,
                    template_filename=template,
                    verbosity=options.verbosity,
                    stderr=stderr,
                    **template_vars,
                )
    except:
        msg = "An error occurred. Deleting all created files/directories..."
        print(msg, file=stderr)
        for f in to_clean:
            if f.is_dir():
                shutil.rmtree(f)
            else:
                f.unlink(missing_ok=True)
            if options.verbosity > 0:
                print(f"Successfully deleted: {f}", file=stderr)
        raise
    end = datetime.datetime.now(tz=datetime.timezone.utc)  # noqa: UP017
    duration = (end - start).total_seconds()
    print(f" cluster-setup complete in {duration}s ".center(80, "-"))
