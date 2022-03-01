#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

from functools import partial
from PyQt5.QtWidgets import QMainWindow
from cdicalc.gui.mainWindow import Ui_MainWindow


class ApplicationWindow(QMainWindow):
    """Definition of the graphical user interface."""

    def __init__(self, model):
        """View initializer."""
        super().__init__()
        self.model = model
        # Set some main window's properties
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect signals and slots
        self._connectSignals()

    def _connectSignals(self):
        self.ui.energy.textEdited.connect(
            partial(self.model.energy_changed, self.ui)
        )
        self.ui.wavelength.textEdited.connect(
            partial(self.model.wavelength_changed, self.ui)
        )

        self.ui.energy.editingFinished.connect(
            partial(self.model.format_field, self.ui.energy)
        )
        self.ui.wavelength.editingFinished.connect(
            partial(self.model.format_field, self.ui.wavelength)
        )
