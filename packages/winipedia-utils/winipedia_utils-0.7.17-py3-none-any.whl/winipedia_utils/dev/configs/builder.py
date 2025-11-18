"""Config File subclass that creates the builds dir and a build.py."""

from pathlib import Path

import winipedia_utils
from winipedia_utils.dev.configs.base.base import PythonConfigFile
from winipedia_utils.dev.configs.pyproject import PyprojectConfigFile
from winipedia_utils.utils.modules.module import to_path


class BuilderConfigFile(PythonConfigFile):
    """Config File subclass that creates the dirs folder."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        # avoids loading configs pkg when init_config_files is called
        # bc it leads to import error in sub pkg when adding new dev deps
        from winipedia_utils.dev.artifacts import builder  # noqa: PLC0415

        src_package = PyprojectConfigFile.get_package_name()
        builds_package = builder.__name__.replace(
            winipedia_utils.__name__, src_package, 1
        )
        return to_path(builds_package, is_package=True)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the content."""
        return '''"""Build script.

All subclasses of Builder in the builds package are automatically called.
"""'''
