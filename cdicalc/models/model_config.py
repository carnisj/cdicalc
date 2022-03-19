# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle loading/dumping of the config."""

import logging
from PyQt5.QtWidgets import QLineEdit
from typing import Any

from cdicalc.models.model import Model
from cdicalc.resources.mainWindow import Ui_main_window
from cdicalc.utils.serialization import ConfigFile

logger = logging.getLogger(__name__)


class ModelConfig(Model):
    """
    Specific class gathering the methods for updating the config.

    :param config_file: an instance of ConfigFile
    """

    def __init__(self, config_file: ConfigFile):
        super().__init__()
        if not isinstance(config_file, ConfigFile):
            logger.error(
                "'config_file' should be an instance of ConfigFile, got "
                f"{type(config_file)}"
            )
            config_file = ConfigFile(path=None)
        self.config_file = config_file

    @staticmethod
    def _generate_config(ui: Ui_main_window) -> Any:
        """Generate the config dictionary."""
        config = {}
        ui_attr = dir(ui)
        for _, attr in enumerate(ui_attr):
            if isinstance(getattr(ui, attr), QLineEdit):
                widget = getattr(ui, attr)
                if not widget.isReadOnly():
                    config[attr] = widget.text()
        return config

    def load_config(self, path, ui: Ui_main_window) -> None:
        """Load a config file and update the GUI."""
        # update the path
        self.config_file.path = path
        # load the config
        self.config_file.load()
        # update the GUI with the new config
        self.update_gui(ui=ui)

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

    def update_gui(self, ui: Ui_main_window):
        """Update the GUI widgets with the config values."""
        if not isinstance(self.config_file.config, dict):
            return
        for widget, value in self.config_file.config.items():
            getattr(ui, widget).setText(value)
