"""Build utilities for creating and managing project builds.

This module provides functions for building and managing project artifacts,
including creating build scripts, configuring build environments, and
handling build dependencies. These utilities help with the packaging and
distribution of project code.
"""

import os
import platform
import tempfile
from abc import abstractmethod
from importlib import import_module
from pathlib import Path

from PyInstaller.__main__ import run

import winipedia_utils
from winipedia_utils.dev import artifacts
from winipedia_utils.dev.configs.builder import BuilderConfigFile
from winipedia_utils.dev.configs.pyproject import PyprojectConfigFile
from winipedia_utils.utils.data.structures.text.string import make_name_from_obj
from winipedia_utils.utils.modules.class_ import (
    get_all_nonabstract_subclasses,
)
from winipedia_utils.utils.modules.module import (
    make_obj_importpath,
    to_module_name,
    to_path,
)
from winipedia_utils.utils.modules.package import get_src_package
from winipedia_utils.utils.oop.mixins.mixin import ABCLoggingMixin


class Builder(ABCLoggingMixin):
    """Base class for build scripts.

    Subclass this class and implement the get_artifacts method to create
    a build script for your project. The build method will be called
    automatically when the class is initialized. At the end of the file add
    if __name__ == "__main__":
        YourBuildClass()
    """

    ARTIFACTS_DIR_NAME = "artifacts"
    ARTIFACTS_PATH = Path(ARTIFACTS_DIR_NAME)

    @classmethod
    @abstractmethod
    def create_artifacts(cls) -> None:
        """Build the project.

        This method should create all artifacts in the ARTIFACTS_PATH folder.

        Returns:
            None
        """

    @classmethod
    def __init__(cls) -> None:
        """Initialize the build script."""
        cls.build()

    @classmethod
    def build(cls) -> None:
        """Build the project.

        This method is called by the __init__ method.
        It takes all the files and renames them with -platform.system()
        and puts them in the artifacts folder.
        """
        cls.ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
        cls.create_artifacts()
        artifacts = cls.get_artifacts()
        for artifact in artifacts:
            parent = artifact.parent
            if parent != cls.ARTIFACTS_PATH:
                msg = f"You must create {artifact} in {cls.ARTIFACTS_PATH}"
                raise FileNotFoundError(msg)

            # rename the files with -platform.system()
            new_name = f"{artifact.stem}-{platform.system()}{artifact.suffix}"
            new_path = cls.ARTIFACTS_PATH / new_name
            artifact.rename(new_path)

    @classmethod
    def get_artifacts(cls) -> list[Path]:
        """Get the built artifacts."""
        paths = list(cls.ARTIFACTS_PATH.glob("*"))
        if not paths:
            msg = f"Expected {cls.ARTIFACTS_PATH} to contain files"
            raise FileNotFoundError(msg)
        return paths

    @classmethod
    def get_non_abstract_subclasses(cls) -> set[type["Builder"]]:
        """Get all non-abstract subclasses of Builder."""
        path = BuilderConfigFile.get_parent_path()
        module_name = to_module_name(path)
        if not to_path(module_name, is_package=True).exists():
            return set()
        builds_pkg = import_module(module_name)
        return get_all_nonabstract_subclasses(cls, load_package_before=builds_pkg)

    @classmethod
    def init_all_non_abstract_subclasses(cls) -> None:
        """Build all artifacts."""
        for builder in cls.get_non_abstract_subclasses():
            builder()


class PyInstallerBuilder(Builder):
    """Build the project with pyinstaller.

    Expects main.py in the src package.
    """

    @classmethod
    @abstractmethod
    def get_add_datas(cls) -> list[tuple[Path, Path]]:
        """Get the add data paths.

        Returns:
            list[tuple[Path, Path]]: List of tuples with the source path
                and the destination path.
        """

    @classmethod
    def get_pyinstaller_options(cls, temp_dir: str) -> list[str]:
        """Get the pyinstaller options."""
        options = [
            str(cls.get_main_path()),
            "--name",
            cls.get_app_name(),
            "--clean",
            "--noconfirm",
            "--onefile",
            "--noconsole",
            "--workpath",
            temp_dir,
            "--specpath",
            temp_dir,
            "--distpath",
            str(cls.ARTIFACTS_PATH),
            "--icon",
            str(cls.get_app_icon_path()),
        ]
        for src, dest in cls.get_add_datas():
            options.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
        return options

    @classmethod
    def get_app_icon_path(cls) -> Path:
        """Get the app icon path.

        Default is under dev/artifacts folder as icon.ico.
        """
        artifacts_path = to_path(
            make_obj_importpath(artifacts).replace(
                winipedia_utils.__name__, get_src_package().__name__, 1
            ),
            is_package=True,
        )
        return artifacts_path / "icon.ico"

    @classmethod
    def get_app_name(cls) -> str:
        """Get the app name."""
        pkg_name = PyprojectConfigFile.get_package_name()
        return make_name_from_obj(pkg_name, split_on="_", join_on=" ")

    @classmethod
    def get_main_path_from_src_pkg(cls) -> Path:
        """Get the main path.

        The path to main from the src package.
        """
        return Path("main.py")

    @classmethod
    def get_root_path(cls) -> Path:
        """Get the root path."""
        src_pkg = get_src_package()
        return to_path(src_pkg, is_package=True).resolve().parent

    @classmethod
    def get_src_pkg_path(cls) -> Path:
        """Get the src package path."""
        src_pkg = get_src_package()
        return cls.get_root_path() / src_pkg.__name__

    @classmethod
    def get_main_path(cls) -> Path:
        """Get the main path."""
        return cls.get_src_pkg_path() / cls.get_main_path_from_src_pkg()

    @classmethod
    def create_artifacts(cls) -> None:
        """Build the project with pyinstaller."""
        with tempfile.TemporaryDirectory() as temp_build_dir:
            options = cls.get_pyinstaller_options(temp_build_dir)

            run(options)
