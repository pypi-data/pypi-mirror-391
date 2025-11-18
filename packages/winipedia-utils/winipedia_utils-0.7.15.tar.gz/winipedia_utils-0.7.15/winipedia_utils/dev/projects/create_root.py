"""Utilities for working with Python projects."""

from winipedia_utils.dev.configs.base.base import ConfigFile
from winipedia_utils.dev.configs.pyproject import PyprojectConfigFile
from winipedia_utils.dev.testing.convention import TESTS_PACKAGE_NAME
from winipedia_utils.utils.modules.package import (
    make_init_modules_for_package,
)


def create_project_root() -> None:
    """Create the project root."""
    src_package_name = PyprojectConfigFile.get_package_name()
    ConfigFile.init_config_files()
    make_init_modules_for_package(src_package_name)
    make_init_modules_for_package(TESTS_PACKAGE_NAME)


if __name__ == "__main__":
    create_project_root()
