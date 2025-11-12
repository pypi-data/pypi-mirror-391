# MIT License
#
# Copyright (c) 2024-2025 Thomas Mahé <oss@tmahe.fr>
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

__author__ = "Thomas Mahé <oss@tmahe.fr>"

import fnmatch
import logging
import os
import importlib
from pathlib import Path
from typing import Optional, List, Union

import poetry.console
from cleo.commands.command import Command
from cleo.events.console_terminate_event import ConsoleTerminateEvent
from cleo.events.event import Event

# Reload logging after PyInstaller import (conflicts with poetry logging)
importlib.reload(logging)

from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND, TERMINATE
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.core.masonry.builders.wheel import WheelBuilder
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.utils.env import EnvManager
from poetry_pyinstaller_plugin import __version__
from poetry_pyinstaller_plugin.models import (LoggingMixin,
                                              PyInstallerPluginHook,
                                              PyProjectConfig, Target)

class PyInstallerShowCommand(Command, LoggingMixin):
    name = "pyinstaller show"
    description = "Print plugin version."

    def handle(self) -> int:
        self.log(f"poetry-pyinstaller-plugin {__version__}")
        return 0

class PyInstallerBuildCommand(Command, LoggingMixin):
    name = "pyinstaller build"
    description = "Build PyInstaller targets (Excluding targets with bundle feature enabled)."
    targets: List[Target]

    def __init__(self, application: Application):
        super().__init__()
        self._app = application
        self._pyproject = PyProjectConfig(self._app.poetry.pyproject.data)
        self.attach_io(application._io)  # noqa

        targets = self._pyproject.lookup("tool.poetry-pyinstaller-plugin.scripts", dict())
        self.targets = [Target(name, self._app.poetry, io=self._io) for name in targets.keys()]

        self.platform = WheelBuilder(self._app.poetry)._get_sys_tags()[0].split("-")[-1]  # noqa
        self.pre_build_hook = None
        self.post_build_hook = None

        if pre_build := self._pyproject.lookup('tool.poetry-pyinstaller-plugin.pre-build', None):
            self.pre_build_hook = PyInstallerPluginHook(self._io, self._app.poetry, self.platform, pre_build)

        if post_build := self._pyproject.lookup('tool.poetry-pyinstaller-plugin.post-build', None):
            self.post_build_hook = PyInstallerPluginHook(self._io, self._app.poetry, self.platform, post_build)

    @property
    def use_bundle(self) -> bool:
        return True in [t.bundle for t in self.targets]

    def handle(self) -> int:
        env_manager = EnvManager(self._app.poetry, io=self._io)

        venv = env_manager.create_venv()
        venv_version = f"python{venv.version_info[0]}.{venv.version_info[1]}"
        pyinstaller_version = venv.run("pyinstaller", "--version").strip()

        if self.pre_build_hook:
            self.pre_build_hook.attach_io(self._io)
            self.pre_build_hook.exec(venv)

        self.log(f"Building <info>pyinstaller</info> <debug>[{venv_version} {self.platform}]</debug>")
        self.debug(f"PyInstaller version = {pyinstaller_version}")

        for target in self.targets:
            target.build(self._app.poetry)

        if self.post_build_hook:
            self.post_build_hook.attach_io(self._io)
            self.post_build_hook.exec(venv)

        return 0

    def bundle_wheels(self):
        wheels = []
        for file in os.listdir('dist'):
            if fnmatch.fnmatch(file, '*-py3-none-any.whl'):
                wheels.append(file)

        targets = list(filter(lambda t: t.bundle and not t.skip, self.targets))

        if len(targets) == 0:
            return

        self.log(f"Bundling PyInstaller targets to wheel(s)")
        for wheel in wheels:
            for target in targets:
                target.bundle_to_wheel(wheel)

        if len(wheels) > 0:
            self.log(f"Replacing <info>platform</info> in wheels <b>({self.platform})</b>")
            for wheel in wheels:
                new = wheel.replace("-any.whl", f"-{self.platform}.whl")
                os.replace(Path("dist", wheel), Path("dist", new))
                self.log(f"  - {new}")


class PyInstallerPlugin(ApplicationPlugin):
    _app: Application = None
    _pyproject: Optional[PyProjectConfig] = None
    build_command: Optional[PyInstallerBuildCommand] = None

    def activate(self, application: poetry.console.application.Application) -> None:
        """
        Activation method for ApplicationPlugin
        """
        self._app = application

        def build_command_factory():
            return PyInstallerBuildCommand(self._app)

        def show_command_factory():
            return PyInstallerShowCommand()

        application.command_loader.register_factory("pyinstaller build", build_command_factory)
        application.command_loader.register_factory("pyinstaller show", show_command_factory)

        application.event_dispatcher.add_listener(COMMAND, self.on_build_command)
        application.event_dispatcher.add_listener(TERMINATE, self.on_terminate)

    def on_terminate(self, event: Event, event_name: str, dispatcher: EventDispatcher) -> None:
        if isinstance(event, ConsoleTerminateEvent) and event.command.name == "build":

            # Skip build if format specified in build command
            if event.io.input.option("format"):
                return

            if self.build_command.use_bundle:
                self.build_command.bundle_wheels()

    def on_build_command(self, event: Event, event_name: str, dispatcher: EventDispatcher) -> None:
        """
        Main event
        """
        if isinstance(event, ConsoleCommandEvent) and event.command.name == "build":
            self.build_command = PyInstallerBuildCommand(self._app)

            # Skip build if format specified in build command
            if event.io.input.option("format"):
                return

            self.build_command.handle()
