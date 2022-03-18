# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Utility functions and classes for the serialization of the config."""

import os
import pathlib
from typing import Any, Optional
import yaml


class ConfigFile:
    """
    Class gathering methods related to loading/dumping a configuration file.

    :param path: full path the config file.
    """
    def __init__(self, path: Optional[str]) -> None:
        self.config: Any = None
        self.path = path
        self.load()

    @property
    def path(self):
        """Path of the directory for saving the config file."""
        return self._path

    @path.setter
    def path(self, value: Optional[str]) -> None:
        if value is None or value == "":
            self._path = None
            return

        if not isinstance(value, str):
            raise TypeError(f"'path' should be a string, got {type(value)}")
        elif not value.endswith(".yml"):
            value += ".yml"
        self._path = value
        pathlib.Path(value).parent.mkdir(parents=True, exist_ok=True)

    def dump(self) -> None:
        """Dump the config to the config file."""
        if self.path is None:
            return
        with open(self.path, mode="w", encoding="utf-8") as file:
            print(f"dumping config to {self.path}")
            yaml.dump(self.config, stream=file, Dumper=yaml.Dumper)

    def load(self) -> None:
        """Load the config from the config file."""
        if self.path is None or not os.path.isfile(self.path):
            self.config = {}
        else:
            with open(self.path, mode="r", encoding="utf-8") as file:
                print(f"loading config from {self.path}")
                self.config = yaml.safe_load(stream=file)
