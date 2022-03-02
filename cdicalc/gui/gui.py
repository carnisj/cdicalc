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

        # self.ui.crystal_size.textEdited.connect(
        #     partial(
        #         self.model.field_changed,
        #         "crystal_size",
        #         self.ui,
        #         {self.model.update_d2theta: None},
        #     )
        # )
        self.ui.detector_distance.textEdited.connect(
            partial(
                self.model.field_changed,
                "detector_distance",
                self.ui,
                {self.model.update_d2theta: None},
            )
        )
        self.ui.detector_pixelsize.textEdited.connect(
            partial(
                self.model.field_changed,
                "detector_pixelsize",
                self.ui,
                {self.model.update_d2theta: None},
            )
        )
        self.ui.fringe_spacing.textEdited.connect(
            partial(
                self.model.field_changed,
                "fringe_spacing",
                self.ui,
                {self.model.update_d2theta: None},
            )
        )
        self.ui.sampling_ratio.textEdited.connect(
            partial(
                self.model.field_changed,
                "sampling_ratio",
                self.ui,
                {self.model.update_d2theta: None},
            )
        )
        self.ui.xray_energy.textEdited.connect(
            partial(
                self.model.field_changed,
                "xray_energy",
                self.ui,
                {
                    self.model.update_xrays: ["xray_wavelength"],
                    self.model.update_d2theta: None,
                },
            )
        )
        self.ui.xray_wavelength.textEdited.connect(
            partial(
                self.model.field_changed,
                "xray_wavelength",
                self.ui,
                {
                    self.model.update_xrays: ["xray_energy"],
                    self.model.update_d2theta: None,
                },
            )
        )

        ui_attr = dir(self.ui)
        for idx, attr in enumerate(ui_attr):
            if isinstance(getattr(self.ui, attr), QLineEdit):
                field = getattr(self.ui, attr)
                field.editingFinished.connect(partial(self.model.format_field, field))
