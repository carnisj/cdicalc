# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle loading/dumping of the config."""

from typing import Any, Dict

from cdicalc.models.model import Model
from cdicalc.resources.mainWindow import Ui_main_window
from cdicalc.utils.serialization import ConfigFile


class ModelConfig(Model):
    """
    Specific class gathering the methods for updating the config.

    :param config_file: an instance of ConfigFile
    :param verbose: True to have more logging output.
    """

    def __init__(self, config_file: ConfigFile, verbose=False):
        super().__init__(verbose=verbose)
        self.config_file = config_file

    @staticmethod
    def _generate_config(ui: Ui_main_window) -> Any:
        """Generate the config dictionary."""
        config = None
        return config

    def load_config(self, path) -> None:
        """Load a config file and update the GUI."""
        # update the path
        self.config_file.path = path
        # load the config
        self.config_file.load()
        # update the GUI with the new config
        self._update_gui()

    def save_config(self, path: str, ui: Ui_main_window) -> None:
        """
        Override the config file with the current GUI values.
        """
        # get the config
        self.config_file.config = self._generate_config(ui=ui)
        # update the path
        self.config_file.path = path
        # dump the config to the file
        self.config_file.dump()

    def _update_gui(self):
        """Update the GUI widgets with the config values."""
        config = self.config_file.config
