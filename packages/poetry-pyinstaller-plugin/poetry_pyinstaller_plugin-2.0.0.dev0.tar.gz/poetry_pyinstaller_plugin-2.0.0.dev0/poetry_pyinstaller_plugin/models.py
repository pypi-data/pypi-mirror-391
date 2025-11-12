# MIT License
#
# Copyright (c) 2025 Thomas Mahé <oss@tmahe.fr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import dataclasses
import logging
import os
import textwrap
import zipfile
from errno import EEXIST, EINVAL, ENOTDIR
from importlib.machinery import SourceFileLoader
from pathlib import Path
from shutil import copy, copytree, rmtree
from typing import Any, Dict, List, Optional, Union

import tomlkit
from cleo.io.io import IO
from poetry.core.masonry.builders.wheel import WheelBuilder
from poetry.core.version.pep440 import PEP440Version
from poetry.poetry import Poetry
from poetry.utils.env import Env, EnvManager
from tomlkit import TOMLDocument


class LoggingMixin:
    _io: IO

    def __init__(self, io: IO, **kwargs):
        self._io = io

    def attach_io(self, io: IO):
        self._io = io

    def is_debug(self) -> bool:
        return self._io.is_debug()

    def log(self, msg: str) -> None:
        if self.is_debug():
            msg = f"<fg=yellow;options=bold>[poetry-pyinstaller-plugin]</> {msg}"
        self._io.write_line(msg)

    def warning(self, msg: str) -> None:
        self.log(f"<fg=yellow;options=bold>{msg}</>")

    def error(self, msg: str) -> None:
        self.log(f"<error>{msg}</error>")

    def debug(self, msg: str) -> None:
        if self.is_debug():
            self.log(f"<debug>{msg}</debug>")

    def debug_command(self, output: str):
        for line in output.splitlines():
            self.debug(f" + {line}")


class PyProjectConfig:
    def __init__(self, data: TOMLDocument):
        self.data = data

    def lookup(self, field: str, default: Any = None) -> Any:
        if self.data:
            items = field.split('.')
            data = self.data

            if len(items) == 1:
                return data.get(field, default)

            for item in items[:-1]:
                data = data.get(item, {})
            return data.get(items[-1], default)

        raise RuntimeError("Error while retrieving pyproject.toml data.")

    def get_section(self, section: str) -> PyProjectConfig:
        return PyProjectConfig(self.lookup(section, {}))


@dataclasses.dataclass(init=False)
class PyInstallerPluginHook(LoggingMixin):
    """
    Generic interface for interacting with Poetry in hooks
    """
    module_name: str
    callable: str
    source_path: Path
    poetry: Poetry
    platform: str
    _venv: Env

    def __init__(self, io: IO, poetry: Poetry, platform: str, spec: str):
        super().__init__(io)
        self.poetry = poetry
        self.platform = platform
        self.module_name, self.callable = spec.split(":")

        parts = self.module_name.split(".")
        self.source_path = (poetry.pyproject.path.parent / Path(*parts[:-1]) / f"{parts[-1]}.py")

    def exec(self, venv: Env) -> None:
        """
        Run command in virtual environment
        """
        self._venv = venv
        module = SourceFileLoader(self.module_name.split('.')[-1], str(self.source_path)).load_module()
        if hasattr(module, self.callable):
            self.log(f"<b><info>Running<b><info> pre-build hook <debug>{module.__name__}:{self.callable}()</debug>")
            getattr(module, self.callable)(
                self
            )
        else:
            self.warning(f"Skipping pre-build hook, method '{self.callable}' not found in {module.__name__}.")

    @property
    def pyproject_data(self) -> TOMLDocument:
        """
        Get pyproject data
        :return: Configuration file dictionary
        """
        return self.poetry.pyproject.data

    def run(self, command: str, *args: str) -> None:
        """
        Run command in virtual environment
        """
        self.debug(f"Running '{' '.join(args)}'")
        output = self._venv.run(command, *args)
        for line in output.split('\n'):
            self.debug("++ " + line)

    def run_pip(self, *args: str) -> None:
        """
        Install requirements in virtual environment
        """
        self.debug(f"Running 'pip {' '.join(args)}'")
        output = self._venv.run_pip(*args)
        for line in output.split('\n'):
            self.debug("++ " + line)


@dataclasses.dataclass(init=False)
class Target(LoggingMixin):
    pyinstaller_version: str
    package_version: PEP440Version
    dist_path: Path
    work_path: Path
    platform: str
    prog: str
    source: Path
    type: str
    bundle: bool
    strip: bool
    noupx: bool
    console: bool
    windowed: bool
    icon: Optional[str]
    uac_admin: bool
    uac_uiaccess: bool
    argv_emulation: bool
    arch: Optional[str]
    hiddenimport: Union[str, List[str]]
    when: Optional[str]
    add_version: bool
    certificates: List[str]
    collect_config: Dict[str, List[str]]
    exclude_poetry_include: bool
    include_config: Dict[str, List[str]]
    runtime_hooks: List[str]
    copy_metadata_config: List[str]
    recursive_copy_metadata_config: List[str]
    package_config: Dict[str, str]

    def __init__(self, prog: str, poetry: Poetry, io: IO, **kwargs):
        super().__init__(io, **kwargs)
        self.prog = prog
        self.platform = WheelBuilder(poetry)._get_sys_tags()[0].split("-")[-1]  # noqa
        self._global_config = PyProjectConfig(poetry.pyproject.data)
        self._plugin_config = self._global_config.get_section(f"tool.poetry-pyinstaller-plugin")
        self._target_config = self._global_config.get_section(f"tool.poetry-pyinstaller-plugin.scripts.{prog}")
        # When target specified by '<target> = "script.py"'
        if not isinstance(self._target_config.data, dict):
            self._target_config.data = TOMLDocument().add("source", self._target_config.data)

        self.package_version = self._get_package_version(poetry)
        self.dist_path = Path(self.lookup('dist-path', Path("dist", "pyinstaller", self.platform))).resolve()
        self.work_path = Path(self.lookup("work-path", Path('build', self.platform))).resolve()

        _ = self.lookup

        fields = {
            "pyinstaller_version": None,
            "type": "onedir",
            "bundle": False,
            "strip": False,
            "noupx": False,
            "console": False,
            "windowed": False,
            "icon": None,
            "uac_admin": False,
            "uac_uiaccess": False,
            "argv_emulation": False,
            "arch": None,
            "hiddenimport": None,
            "runtime_hooks": None,
            "when": None,
            "add_version": False
        }
        for field, default in fields.items():
            self.__setattr__(field, self.lookup(field, default))

        self.source = Path(self.lookup("source", None)).resolve()
        self.certificates = self.lookup("certifi.append", list())
        self.collect_config = self.lookup("collect", dict())
        self.exclude_poetry_include = self.lookup("exclude-include", False)
        self.include_config = self.lookup("include", dict())
        self.runtime_hooks = self.lookup("runtime_hooks", list())
        self.copy_metadata_config = self.lookup("copy-metadata", list())
        self.recursive_copy_metadata_config = self.lookup("recursive-copy-metadata", list())
        self.package_config = self.lookup("package", dict())

        if self.add_version:
            self.prog = f"{self.prog}-{self.package_version.to_string()}"

        self.validate()

    @property
    def pyinstaller_command(self) -> List[str]:
        args = [
            "pyinstaller",
            self.source,
            f"--{self.type}",
            f"--name", self.prog,
            "--noconfirm",
            "--clean",
            "--workpath", self.work_path,
            "--distpath", self.dist_path,
            "--specpath", (self.dist_path / ".specs"),
            "--contents-directory", f"_{self.prog}_internal",
            "--strip" if self.strip else ...,
            "--noupx" if self.noupx else ...,
            "--console" if self.console else "--noconsole",
            "--windowed" if self.windowed else "--nowindowed",
            "--uac-admin" if self.uac_admin else ...,
            "--uac-uiaccess" if self.uac_uiaccess else ...,
            "--argv-emulation" if self.argv_emulation else ...,
        ]

        if self.icon:
            args.extend(("--icon", self.icon))

        if self.arch:
            args.extend(("--target-arch", self.arch))

        for hook in self.runtime_hooks:
            args.extend(("--runtime-hook", hook))

        for package in self.copy_metadata_config:
            args.extend(("--copy-metadata", package))

        for package in self.recursive_copy_metadata_config:
            args.extend(("--recursive-copy-metadata", package))

        self._add_collect_args(args)
        self._add_include_args(args)
        self._add_hidden_imports_args(args)
        self._add_logging_args(args)

        args = list(filter(lambda i: i is not Ellipsis, args))
        return list(map(str, args))

    def _add_collect_args(self, args: List[Any]) -> None:
        for collect_type, modules in self.collect_config.items():
            if collect_type in ["submodules", "data", "datas", "binaries", "all"]:
                for module in modules:
                    args.extend((f"--collect-{collect_type}", module))

    def _add_include_args(self, args: List[Any]) -> None:
        sep = ";" if "win" in self.platform else ":"

        # Includes from poetry
        if not self.exclude_poetry_include:
            for item in self._global_config.lookup("tool.poetry.include", list()):
                if path := item if isinstance(item, str) else item.get("path", None):
                    args.extend(("--add-data", f"{Path(path).resolve()}{sep}."))

        # Includes from plugin
        for source, target in self.include_config.items():
            if source and target:
                args.extend(("--add-data", f"{Path(source).resolve()}{sep}{target}"))

    def _add_hidden_imports_args(self, args: List[Any]) -> None:
        if self.hiddenimport:
            if isinstance(self.hiddenimport, str):
                self.hiddenimport = list(self.hiddenimport)
            for item in self.hiddenimport:
                args.extend(("--hidden-import", item))

    def _add_logging_args(self, args: List[Any]) -> None:
        if logging.root.level == logging.WARNING:
            args.append(f"--log-level=WARN")
        if logging.root.level == logging.INFO:
            args.append(f"--log-level=INFO")
        if logging.root.level == logging.DEBUG:
            args.extend(("--debug=all", "--log-level=DEBUG"))

    def _get_package_version(self, poetry: Poetry):
        # version from 'project.version'
        version = self._global_config.lookup("project.version", None)

        # version from 'tool.poetry.version'
        version = self._global_config.lookup("tool.poetry.version", version)

        # version from 'poetry-dynamic-versioning'
        if self._global_config.lookup("tool.poetry-dynamic-versioning.enable", False):
            from poetry_dynamic_versioning import _get_config, _get_version
            pyproject = tomlkit.parse(poetry.pyproject_path.read_bytes().decode("utf-8"))
            version, _ = _get_version(_get_config(pyproject))

        return PEP440Version.parse(version)

    def validate(self):
        if self.type not in ["onefile", "onedir"]:
            raise ValueError(
                f"ValueError: Unsupported distribution type for target '{self.prog}', "
                f"'{self.type}' not in ['onefile', 'onedir']."
            )

        if self.when not in [None, "release", "prerelease"]:
            raise ValueError(
                f"ValueError: Unsupported value for field 'when' for target '{self.prog}', "
                f"'{self.when}' not in ['release', 'prerelease']."
            )

    def lookup(self, field: str, default: Any) -> Any:
        return self._target_config.lookup(field, self._plugin_config.lookup(field, default))

    @property
    def skip(self):
        if self.when == "release":
            return not self.package_version.is_prerelease()
        if self.when == "prerelease":
            return self.package_version.is_prerelease()
        return False

    def build(self, poetry: Poetry):
        env_manager = EnvManager(poetry, io=self._io)
        venv = env_manager.create_venv()
        platform = WheelBuilder(poetry)._get_sys_tags()[0].split("-")[-1]  # noqa

        if self.skip:
            self.warning(f" <info>-</info> Skipping {self.prog} (on {self.when} only)")
            return

        self.log(f" - Building <c1>{self.prog}</c1>")

        # Install dependencies
        self._install_dependencies(venv)

        # Deploy certificates to venv
        self._deploy_certificates(poetry, venv)

        # Run pyinstaller
        self._run_pyinstaller(venv)

    def _install_dependencies(self, venv: Env):
        args = ("poetry", "install", "--all-extras", "--all-groups", "--compile")
        self.debug(f"run '{' '.join(args)}'")
        self.debug_command(venv.run(*args))

    def _deploy_certificates(self, poetry: Poetry, venv: Env):
        for crt in self.certificates:
            crt_path = (poetry.pyproject_path.parent / crt).relative_to(poetry.pyproject_path.parent)
            self.log(f"  - Adding <c1>{crt_path}</c1> to certifi")
            venv.run_python_script(textwrap.dedent(f"""
            import certifi
            print(certifi.where())
            with open(r"{crt_path}", "r") as include:
                with open(certifi.where(), 'a') as cert:
                    cert.write(include.read())
            """))

    def _run_pyinstaller(self, venv: Env):
        args = self.pyinstaller_command
        self.debug(f"run '{' '.join(args)}'")
        self.debug_command(venv.run(*args))

    def _run_package(self):
        if self.type == "onefile":
            package_path = Path("dist", "pyinstaller", self.platform, self.prog)
        else:
            package_path = Path("dist", "pyinstaller", self.platform)

        for source, target in self.package_config.items():
            destination = Path(package_path / (target if target != "." else source))
            try:
                if destination.exists() and destination.is_dir():
                    rmtree(destination)
                copytree(source, destination)
            except OSError as exc:  # python >2.5 or, is file and/or file exists
                if exc.errno in (ENOTDIR, EINVAL, EEXIST):
                    copy(source, destination)
                else:
                    raise

    def bundle_to_wheel(self, wheel: str):
        target_path = Path("dist", "pyinstaller", self.platform, self.prog)
        wheel_path = Path("dist", wheel)

        self.log(f"  - Adding <c1>{self.prog}</c1> to data scripts <debug>{wheel}</debug>")
        with zipfile.ZipFile(wheel_path, "a", zipfile.ZIP_DEFLATED) as wheel_f:
            for file in wheel_f.filelist:
                if "dist-info/WHEEL" in file.filename:
                    wheel_scripts_path = Path(file.filename.replace("dist-info/WHEEL", "data/scripts/"))

            if os.path.isfile(target_path):
                wheel_f.write(target_path, arcname=wheel_scripts_path / target_path.name)
                return

            for root, dirs, files in os.walk(target_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    wheel_f.write(file_path, arcname=wheel_scripts_path / os.path.relpath(file_path, target_path))
