#!/usr/bin/env python3
# pylint: disable=redefined-outer-name
#
import os
import shutil
import subprocess
import tempfile
import typing as t

from setuptools import setup

try:
    import tomlib
except ModuleNotFoundError:
    try:
        import tomllib as tomlib
    except ModuleNotFoundError:
        import tomli as tomlib


class AutoRestoreFile:
    def __init__(self, src: str, dst: str):
        self.src = src
        self.dst = dst

    def __enter__(self) -> None:
        shutil.copyfile(self.src, self.dst)

    def __exit__(self, _exc_type: t.Any, _exc_value: t.Any, _exc_traceback: t.Any) -> None:
        shutil.copyfile(self.dst, self.src)


def load_requirements() -> list[str]:
    with open("requirements.txt", encoding="UTF-8") as fd:
        requirements = fd.read().splitlines()
        requirements = [x for x in requirements if x and not x.startswith("--")]
    return requirements


def save_requirements(requirements: list[str]) -> None:
    with open("requirements.txt", mode="w", encoding="UTF-8") as fd:
        fd.writelines([f"{x}\n" for x in requirements])


def push_requirements() -> None:
    # requirements.txt support flags such as "--index", remove
    # them before we continue
    requirements = load_requirements()
    save_requirements(requirements)


def freeze_requirements() -> None:
    # If pyproject specifies creating script files, then
    # compile a static version of the dependencies.

    # Does the pyproject.toml have a "project.scripts"?
    config = os.path.dirname(__file__) + "/pyproject.toml"
    with open(config, mode="rb") as fd:
        pyproject = tomlib.load(fd)

    if not pyproject["project"].get("scripts"):
        return

    cmdline = "uv pip compile requirements.txt --format requirements.txt -o requirements.txt"
    retval = subprocess.run(cmdline, shell=True, check=True, capture_output=True)
    retval.check_returncode()

    # Make a copy as a `constraints.txt` file so it can be used optionally for dev
    shutil.copyfile("requirements.txt", "constraints.txt")


with tempfile.NamedTemporaryFile() as tmpfile:
    with AutoRestoreFile("requirements.txt", tmpfile.name):
        push_requirements()
        freeze_requirements()
        setup()
