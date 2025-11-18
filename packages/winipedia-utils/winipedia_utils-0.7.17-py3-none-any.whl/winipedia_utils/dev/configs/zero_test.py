"""Config utilities for test_zero.py."""

from winipedia_utils.dev.configs.base.base import PythonTestsConfigFile
from winipedia_utils.dev.projects.poetry.poetry import get_poetry_run_module_args
from winipedia_utils.dev.testing import create_tests
from winipedia_utils.utils.os.os import run_subprocess


class ZeroTestConfigFile(PythonTestsConfigFile):
    """Config file for test_zero.py."""

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        filename = super().get_filename()
        return "_".join(reversed(filename.split("_")))

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config."""
        return '''"""Contains an empty test."""


def test_zero() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
'''

    @classmethod
    def create_tests(cls) -> None:
        """Create the tests."""
        run_subprocess(get_poetry_run_module_args(create_tests))
