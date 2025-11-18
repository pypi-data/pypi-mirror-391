"""A script that can be called after you installed the package.

This script calls create tests, creates the pre-commit config, and
creates the pyproject.toml file and some other things to set up a project.
This package assumes you are using poetry and pre-commit.
This script is intended to be called once at the beginning of a project.
"""

from collections.abc import Callable
from typing import Any

from winipedia_utils.dev.configs.conftest import ConftestConfigFile
from winipedia_utils.dev.configs.gitignore import GitIgnoreConfigFile
from winipedia_utils.dev.configs.py_typed import PyTypedConfigFile
from winipedia_utils.dev.configs.pyproject import PyprojectConfigFile
from winipedia_utils.dev.configs.zero_test import ZeroTestConfigFile
from winipedia_utils.dev.git.pre_commit.run_hooks import run_hooks
from winipedia_utils.utils.logging.logger import get_logger

logger = get_logger(__name__)


SETUP_STEPS: list[Callable[..., Any]] = [
    GitIgnoreConfigFile,  # must be there at the beginning to have gitignore
    PyprojectConfigFile,  # must be there at the beginning to make dev group
    PyTypedConfigFile,  # must be there at the beginning to have src pkg
    run_hooks,
    ZeroTestConfigFile.create_tests,
    ConftestConfigFile.run_tests,
]


def get_setup_steps() -> list[Callable[..., Any]]:
    """Get the setup steps."""
    return SETUP_STEPS


def setup() -> None:
    """Set up the project."""
    for step in get_setup_steps():
        logger.info("Running setup step: %s", step.__name__)
        step()
    logger.info("Setup complete!")


if __name__ == "__main__":
    setup()
