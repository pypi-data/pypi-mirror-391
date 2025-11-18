
# Cluster Setup :tornado:

[![codecov](https://codecov.io/gh/ugognw/cluster-setup/graph/badge.svg?token=8YAQGB9YFP)](https://codecov.io/gh/ugognw/cluster-setup)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Static Badge](https://img.shields.io/badge/type%20checked-mypy-039dfc)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![image](https://img.shields.io/pypi/v/cluster-setup.svg)](https://pypi.python.org/pypi/cluster-setup)
[![image](https://img.shields.io/pypi/l/cluster-setup.svg)](https://github.com/ugognw/cluster-setup/blob/main/LICENSE)
[![image](https://img.shields.io/pypi/pyversions/cluster-setup.svg)](https://pypi.python.org/pypi/cluster-setup)
[![Actions status](https://github.com/ugognw/cluster-setup/actions/workflows/CI.yaml/badge.svg)](https://github.com/ugognw/cluster-setup/actions)

- [Cluster Setup :tornado:](#cluster-setup-tornado)
  - [Description](#description)
  - [Quickstart](#quickstart)
    - [Requirements](#requirements)
    - [Installation](#installation)
    - [Basic Usage](#basic-usage)
    - [Command-Line Flags](#command-line-flags)
  - [How-Tos](#how-tos)
    - [Write a Software Script](#write-a-software-script)
    - [Write a Configuration File](#write-a-configuration-file)
  - [Tips](#tips)
    - [Before you call `cluster-setup`](#before-you-call-cluster-setup)
    - [`--clone-repo`](#--clone-repo)
    - [`--software-script`](#--software-script)

This package sets up a remote cluster for computational chemistry workflows.
For a more detailed explanation, see [below](#description).

## Description

In setting up the cluster, this code performs the following steps in order:

1. Create directories for software, support files, and modules in
   folders specified by the corresponding CLI options

2. Create a Python virtual environment with specified packages

3. Optionally, configure `git` (e.g., sign commits with your `ssh` key)

4. Optionally, clone `git` repositories for development.

5. Write Bash startup files (`.bash_profile` and `.bashrc`).
   By default, a minimal `.bash_profile` file is written that simply checks if
   `~/.bashrc` exists and then sources it if it does. The default `.bashrc`
   file defines an alias, `activate_env`, for activating the Python virtual
   environment, and adds the module home directory to the Lmod module path.

6. Install specified software via "software scripts". See
   [How to Write a Software Script](#write-a-software-script) for more details.

7. Creates modulefiles for installed software, virtual environment activation,
   and scripts passed via the `--module-scripts` option.

If `cluster-setup` fails for any reason during execution, all files and folders
created by `cluster-setup` are removed. (This does not include files and
folders that are created by custom software scripts that reside outside of the
software, support file, and module home directories.) **This means that if
any of the software, support file, or module home directories existed and
contained files prior to calling `cluster-setup`, then these files may be
unintentially deleted.** For this reason, **it is not recommended to use
existing directories for any of the aforementioned directories.**

## Quickstart

### Requirements

This package requires:

- [`python`](https://www.python.org) (3.10 or higher with
  `pip` installed) and
- [`git`](https://git-scm.com) (if cloning repositories is
  desired).

All other requirements are installed by `pip`. For more details,
see the `dependencies` and `optional-dependencies` keys in `pyproject.toml`.

### Installation

`cluster-setup` can be installed via `pip`. It is recommended to install
`cluster-setup` in a fresh Python virtual environment,

```bash
python -m venv .venv && source .venv/bin/activate
pip install cluster-setup
```

It is also recommended to run the tests prior to running the CLI. However, to
do so, you must first install the `test` extra:

```bash
pip install .[test]
```

### Basic Usage

`cluster-setup` can be called from the command-line via the `cluster-setup`
command.

```bash
cluster-setup <options>
```

or from within Python code via the function, `cluster_setup.main.run`.

```python
from cluster_setup.main import run
args = [...]
run(args)
```

To run the tests prior to running the CLI, use the `--test` option:

```bash
cluster-setup --test
```

A test report will be written to a text file after the tests run. If any tests
fail, please [file an issue][file-issue] and attach the report.

> [!NOTE]
> This may take up to a minute.

Options can be supplied to the program either via command-line options
or in a configuration file using the `--config-file` CLI option. Configuration
files must be in the [toml format][toml]. A basic configuration
file can be generated with the `--config-gen` option. Details on writing a
configuration file can be found [below](#write-a-configuration-file).

> [!NOTE]
> Options supplied via the command-line options override those specified via
> the configuration file (except in the case of `--python-packages` and
> `--requirements` where option values are combined).

### Command-Line Flags

All the command-line flags can be obtained by running `cluster-setup --help`:

```bash
usage: cluster-setup [-h|-v|-V|-g|-t] [more options; see below]

Set up a Digital Research Alliance of Canada cluster account.

General options:
  -h, --help            Show this help message and exit.
  -v, --verbose         More verbose messages.
  -V, --version         Show the program version number and exit.
  --dry-run             Perform the setup steps for the installation but don't
                        actually install anything. (Not yet supported)
  --check               Perform pre-installation checks. This is the default.
                        Forego checks with '--no-check'.
  -t [PYTEST_ARGS ...], --test [PYTEST_ARGS ...]
                        Run the test suite and exit. Option arguments are forwarded to pytest.

Config file:
  Use a config file instead of command line arguments.
  This is useful if you are using many flags or want to
  transfer a configuration from one cluster to another.

  --config-file CONFIG_FILE
                        Specify a configuration TOML file, must have a [cluster-setup]
                        or [tool.cluster-setup] section.
  -g, --config-gen      Generate a configuration file with default values and exit.

Installation directories:
  Specify installation directories

  --software-home SOFTWARE_HOME
                        The location in which to install software.
                        Defaults to ~/software.
  --support-file-home SUPPORT_FILE_HOME
                        The location in which to install support files.
                        Defaults to ~/support_files.
  --module-home MODULE_HOME
                        The location in which to install modules.
                        Defaults to ~/modules.

Python virtual environment:
  Configure the Python virtual environment

  --venv VENV, --python-venv VENV
                        The name of the Python virtual environment to create.
                        The environment will be created in a subdirectory relative
                        to the software home. Defaults to python_venv.
  -p PACKAGE, --package PACKAGE
                        The name of a Python package to install into the virtual
                        environment. This option may be repeated.
  -r PATTERN, --requirements PATTERN
                        The path to a requirements.txt file specifying Python packages
                        to install. Relative glob patterns are supported. This option
                        may be repeated.
  -c REPO, --clone-repo REPO
                        A repository to clone. For example: DOMAIN:USER/REPO.git
                        This option may be repeated.

Git configuration:
  Configure git version control

  --git-config-file GIT_CONFIG_FILE
                        The file to be used to configure git. Defaults to the global
                        config file.
  --git-user-name GIT_USER_NAME
                        Set your git user name.
  --git-email GIT_EMAIL
                        Set your git user email.
  --git-editor GIT_EDITOR
                        Set your git editor.
  --git-rebase-on-pull  Rebase git branches when pulling from upstream branch.
                        Defaults to False.
  --sign-with-ssh, --git-sign-with-ssh
                        Sign git commits with ssh. You must specify a file containing
                        an ssh public key with the --ssh-key option.
                        Do not sign commits with ssh with the '--no-sign-with-ssh',
                        which is the default.
  --ssh-key SSH_KEY     The file containing your ssh public key. Make sure you have
                        created an ssh key with 'ssh-keygen' first.

Software:
  Configure software installation

  --bashrc BASHRC       A Jinja2 template file to be used to write the .bashrc file. A
                        minimal .bashrc file will be written if omitted.
  -s SOFTWARE_SCRIPTS, --software-script SOFTWARE_SCRIPTS
                        Specify software to be installed via scripts and optionally
                        create modulefiles from templates. See 'Specifying Software Scripts'
                        below for a detailed description of formatting.

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
```

## How-Tos

### Write a Software Script

This guide will describe how to write a software script for use with the
`--software-script` option. In particular, our script will copy files from
a directory, `sources/custom_commands/`, to a subdirectory of the software
home directory. We will also specify a generic template that will be used to
write a modulefile for the software.

The `--software-script` option can be used to install arbitrary software
during the cluster setup process and create a corresponding module. Software
scripts are specified in the format `SCRIPT[:[TEMPLATE]:[MODULE]:[VERSION]:[ARGS]]`.
`SCRIPT` must point to an executable script.

Software scripts should be written with the understanding that they will be
executed in the same directory from which `cluster-setup` is called. As an
example, check out the contents of `install_custom_scripts.sh` below:

```bash
#!/usr/bin/bash

software_home=$1

if [[ $software_home = "" ]]; then
echo "Error: No software home directory specified"
exit
fi

if ! test -e "$software_home"; then
echo "Error: Software home directory $software_home does not exist"
exit
fi

# Create software subdirectory
dest=${software_home}/custom_scripts
mkdir "$dest"

# Copy sources into new directory
cp -v sources/custom_scripts/* "$dest"
chmod +x "$dest"/*
```

This software script will copy several scripts into a subdirectory of the software
home directory.

If specified, `TEMPLATE` must point to a [Jinja2][jinja2] template for the
modulefile. An example of a suitable template (`custom_scripts.j2`) for the
modulefile corresponding to the software installed by `install_custom_scripts.sh`
is shown below:

```lua
help([[
Custom commands that can be executed from the command-line

]])

whatis("Version: {{ version }}")

prepend_path(PATH, "{{ software_home }}/custom_commands")
```

Note that `{{ version }}` and `{{ software_home }}` will be replaced by the
module version (0.0.1 if not specified) and the software home directory,
respectively.

We have thus defined all necessary components in order for `cluster-setup` to
install our software correctly. When we eventually call `cluster-setup`, we
should either specify the following option:

```shell
--software-script="install_custom_scripts.sh:custom_scripts.j2:custom_scripts:0.0.1:{software_home}"
```

or place the following in the configuration file:

```toml
...
software_scripts = [
  "install_custom_scripts.sh:custom_scripts.j2:custom_scripts:0.0.1:{software_home}",
]
...
```

Equivalently, we could allow `cluster-setup` to infer the module name and set
the default version like so from the command-line:

```shell
--software-script="install_custom_scripts.sh:custom_scripts.j2:::{software_home}"
```

or in the configuration file:

```toml
...
software_scripts = [
  "install_custom_scripts.sh:custom_scripts.j2:::{software_home}",
]
...
```

Note that arguments must be quoted in order to specify arguments with spaces. For
example, one might pass both the software and support file homes to the
`--software-script` option like so:

```shell
--software-script="install_custom_scripts.sh:custom_scripts.j2:::'{software_home} {support_file_home}'"
```

or in the configuration file:

```toml
...
software_scripts = [
  "install_custom_scripts.sh:custom_scripts.j2:::'{software_home} {support_file_home}'",
]
...
```

### Write a Configuration File

`cluster-setup` configuration files must be written in the [TOML][toml] format.
Configuration settings can be placed under the `cluster-setup` table or the
`tool.cluster-setup` table. The latter choice enables users to include a
configuration from `cluster-setup` in the `pyproject.toml` file.

An example configuration file is shown below. Note that the names of the Python
options differ from the CLI options in that they include the prefix
(e.g,. `python_requirements`).

```toml
# config.toml

[cluster-setup]
verbosity = 0

# General Setup
software_home = "/Users/USER/software"
support_file_home = "/Users/USER/support_files"
module_home = "/Users/USER/modules"

# Python
python_venv = "python_venv"
python_packages = [
    "pymatgen",
    "numpy",
    "scipy",
    "maggma",
    "fireworks",
    "matplotlib",
]
python_requirements = "/Users/USER/requirements.txt"
python_repos = [
  "github.com:zadorlab/sella.git",
  "github.com:cclib/cclib.git",
  "gitlab.com:ase/ase.git",
]

# Git
git_user_name = "John Doe"
git_email = "john.doe@example.com"
git_editor = "vi"
git_rebase_on_pull = false
git_sign_with_ssh = true
ssh_key = "/Users/USER/.ssh/id_edcsa.pub"
```

## Tips

### Before you call `cluster-setup`

Prior to execution, ensure that any required modules are loaded. For example,
if you would like to use Python 3.12 for virtual environment creation, ensure
that the appropriate module is loaded. Or if the installation of Python packages
specified with the `--packages` or `--requirements` options requires specific
software to be available, ensure that these will be accessible when `pip` is
called during installation.

### `--clone-repo`

- Setup **will fail** unless you have read access to the repository
- epositories will be cloned using SSH
- Because repositories will be cloned using SSH, make sure to add
  your SSH key to the ssh-agent **prior** to executing `cluster-setup`

### `--software-script`

- If your script requires additional dependencies, ensure that these
  are available prior to running `cluster-setup` or load them within
  your script
- Note that software scripts **must** be executable and that the **first**
  line of the file **must** be a shebang.

[jinja2]: https://jinja.palletsprojects.com/en/stable/
[file-issue]: https://github.com/ugognw/cluster-setup/issues
[toml]: (https://toml.io/)
