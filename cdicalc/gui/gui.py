#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

from functools import partial
from PyQt5.QtWidgets import QLineEdit, QMainWindow
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

        self.ui.crystal_size.textEdited.connect(
            partial(self.model.crystal_size_changed, self.ui)
        )
        self.ui.detector_distance.textEdited.connect(
            partial(self.model.detector_distance_changed, self.ui)
        )
        self.ui.detector_pixelsize.textEdited.connect(
            partial(self.model.detector_pixelsize_changed, self.ui)
        )
        self.ui.fringe_spacing.textEdited.connect(
            partial(self.model.fringe_spacing_changed, self.ui)
        )
        self.ui.sampling_ratio.textEdited.connect(
            partial(self.model.sampling_ratio_changed, self.ui)
        )
        self.ui.xray_energy.textEdited.connect(
            partial(
                self.model.field_changed,
                "xray_energy",
                ["xray_wavelength"],
                self.ui,
                [self.model.update_xrays],
            )
        )
        self.ui.xray_wavelength.textEdited.connect(
            partial(
                self.model.field_changed,
                "xray_wavelength",
                ["xray_energy"],
                self.ui,
                self.model.update_xrays,
            )
        )

        ui_attr = dir(self.ui)
        for idx, attr in enumerate(ui_attr):
            if isinstance(getattr(self.ui, attr), QLineEdit):
                field = getattr(self.ui, attr)
                field.editingFinished.connect(partial(self.model.format_field, field))
