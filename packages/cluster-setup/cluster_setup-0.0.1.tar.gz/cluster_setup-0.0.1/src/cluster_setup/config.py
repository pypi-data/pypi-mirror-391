"""Installation configuration module."""

import dataclasses
from pathlib import Path
import shlex
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from typing import Any
from typing import TextIO

from cluster_setup.options import Options
from cluster_setup.options import SoftwareScript

_PATH_OPTIONS = [
    "config_file",
    "software_home",
    "support_file_home",
    "module_home",
    "git_config_file",
    "ssh_key",
    "bashrc",
]


def resolve_path(v: str) -> str:
    """Resolve a path and expand user (~ and ~user) constructs."""
    return str(Path(v).expanduser().resolve())


def expand_pattern(v: str) -> list[str]:
    """Return a list of  files matching a pattern.

    Note:
        If `v` is an absolute path, then the returned list contains `v` only.
    """
    if Path(v).is_absolute():
        files = [v]
    else:
        files = [str(p.expanduser().resolve()) for p in Path().glob(v)]
    return files


def tokenize_software_script(v: str) -> SoftwareScript:
    """Tokenize a software script spec into a tuple.

    A software script spec has the format:

        SCRIPT[:[TEMPLATE]:[MODULE]:[VERSION]:[ARGS]]

    Examples:
        >>> _parse_software_script("install_bash.sh")
        ('install_bash.sh', None, None, '0.0.1', [])
        >>> _parse_software_script("install_bash.sh:bash.j2:bash:0.0.1:~/software_sources")
        ('install_bash.sh', 'bash.j2', 'bash', '0.0.1', ['~/software_sources'])
        >>> _parse_software_script("install_bash.sh:::v1:")
        ('install_bash.sh', None, None, 'v1', [])
        >>> _parse_software_script("install_bash.sh::bash::")
        ('install_bash.sh', None, 'bash', '0.0.1', [])
        >>> _parse_software_script("install_bash.sh:bash.j2:::")
        ('install_bash.sh', 'bash.j2', 'bash', '0.0.1', [])
    """
    template = module = version = None

    if ":" in v:
        script, template, module, version, args = v.split(":")
    else:
        script = v
        args = ""

    template = template or None
    module = module or (Path(template).stem if template else None)
    version = version or "0.0.1"

    return (
        script,
        template,
        module,
        version,
        shlex.split(args) if args else [],
    )


def parse_config_file(
    options: Options,
    filename: str,
    stderr: TextIO | None = None,
) -> None:
    """Parse option values from a configuration file."""
    # Parse top-level of config
    with Path(filename).open("rb") as f:
        toml_data = tomllib.load(f)

    cluster_setup_data: dict[str, Any] = toml_data.get("tool", toml_data)
    section = cluster_setup_data.get("cluster-setup")

    if section is None:
        msg = f"No cluster-setup configuration found in {filename}"
        print(msg, file=stderr)
    else:
        for k, v in section.items():
            if k in _PATH_OPTIONS:
                value: Any = resolve_path(v)
            elif k == "python_requirements":
                value = [f for p in v for f in expand_pattern(p)]
            elif k == "software_scripts":
                value = [tokenize_software_script(s) for s in v]
            else:
                value = v
            setattr(options, k, value)


def _stringify_software_scripts(script: SoftwareScript) -> str:
    combined_args = " ".join(script[-1])
    midsection = ":".join(x or "" for x in script[1:-1])
    return f"{script[0]}:{midsection}:" + combined_args


def _map_types(v: Any) -> str:
    """Convert a value to its configuration file string representation.

    Raises:
        ValueError: The type of `v` is not recognized.
    """
    if isinstance(v, str):
        value = repr(str(v))
    elif isinstance(v, bool):
        value = str(v).lower()
    elif isinstance(v, int | float):
        value = str(v)
    elif isinstance(v, list):
        values = [f"  {_map_types(el)}," for el in v]
        value = "[\n" + "\n".join(values) + "\n]"
    elif isinstance(v, tuple):
        # concatenate software scripts
        value = _stringify_software_scripts(v)
    else:
        msg = f"Unknown type for value: {v} ({type(v)})"
        raise ValueError(msg)

    return value


def textify_config_file(options: Options) -> list[str]:
    """Print an Options object into a list of text."""
    lines: list[str] = []

    for key, value in dataclasses.asdict(options).items():
        if value is not None and not key.startswith("_"):
            v = _map_types(value)
            lines.append(f"{key} = {v}\n")

    return lines


def create_config_file(dest: Path | None = None) -> Path:
    """Create a simple configuration file."""
    dest = dest or Path().cwd()
    lines = ["[tool.cluster-setup]\n", *textify_config_file(Options())]

    config = Path(dest, "config.toml").absolute()
    with config.open(mode="w", encoding="utf-8") as file:
        file.writelines(lines)
    return config
