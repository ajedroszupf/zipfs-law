"""Version specification.

Importing this module should set module-level variables `BASE_VERSION`,
`PACKAGE_VERSION` and `__version__`.

Note: This file is generated from the cookiecutter project template.
It is evaluated in `setup.py`.

Manual modification may break the package build process!
"""
from pathlib import Path
from shlex import shlex
from typing import Optional

VERSIONFILE_PATH = Path(__file__).parent.parent / 'Versionfile'
BASE_VERSION: Optional[str] = None
PACKAGE_VERSION: Optional[str] = None


def read_versionfile() -> None:
    """Read BASE_VERSION and PACKAGE_VERSION from Versionfile in the root project dir.

    Raises:
        FileNotFoundError: If `Versionfile` is not present in the root dir.
    """
    global BASE_VERSION, PACKAGE_VERSION

    with open(VERSIONFILE_PATH) as f:
        # Look for lines with `VAR=<<version>>`. Parse it according to
        # the shell syntax using `shlex`. Note that any references to shell
        # variables in <<version>> will not be interpreted, so for example for
        #
        # >> BASE_VERSION="${MAJOR}.${MINOR}.${PATH}"
        #
        # `base_version` will be set to the string `'${MAJOR}.${MINOR}.${PATH}'`.
        for line in f:
            tokens = list(shlex(line, posix=True))
            if len(tokens) > 2 and tokens[1] == '=':
                if tokens[0] == 'BASE_VERSION':
                    BASE_VERSION = ''.join(tokens[2:])
                elif tokens[0] == 'PACKAGE_VERSION':
                    PACKAGE_VERSION = ''.join(tokens[2:])
            if BASE_VERSION and PACKAGE_VERSION:
                break


__version__: str

try:
    # Versions from `Versionfile` take precedence.
    read_versionfile()
    if not BASE_VERSION:
        raise RuntimeError(f'BASE_VERSION not set in {VERSIONFILE_PATH}')
    __version__ = PACKAGE_VERSION or BASE_VERSION

except FileNotFoundError:
    # For an installed package there's no `Versionfile`.
    # In this case we can read the version from installed package metadata.
    from importlib.metadata import version

    PACKAGE_VERSION = version(__package__)
    __version__ = PACKAGE_VERSION
