#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

from functools import partial
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QMainWindow
from cdicalc.gui.mainWindow import Ui_main_window
from cdicalc.resources import resources_cdicalc


class ApplicationWindow(QMainWindow):
    """Definition of the graphical user interface."""

    def __init__(self, model):
        """View initializer."""
        super().__init__()
        self.model = model
        # Set some main window's properties
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/diffract.png"))
        # Connect signals and slots
        self._connect_tab_bcdi()
        self._connect_QLineEdits()

    def _connect_QLineEdits(self) -> None:
        """
        Connect signals from QLineEdit widgets to the formatting callback.

        The callback rewrites widget values with the configured unit, using
        str(Quantity).
        """

        ui_attr = dir(self.ui)
        for idx, attr in enumerate(ui_attr):
            if isinstance(getattr(self.ui, attr), QLineEdit):
                widget = getattr(self.ui, attr)
                widget.editingFinished.connect(partial(self.model.format_field, widget))

    def _connect_tab_bcdi(self) -> None:
        """Connect signals to slots for the tab on BCDI calculations."""
        # slots for angular_sampling
        self.ui.angular_sampling.textEdited.connect(
            partial(
                self.model.update_max_rocking_angle,
                self.ui,
            )
        )

        # slots for crystal_size
        self.ui.crystal_size.textEdited.connect(
            partial(
                self.model.update_min_distance,
                self.ui,
            )
        )

        # slots for detector_distance
        self.ui.detector_distance.textEdited.connect(
            partial(
                self.model.field_changed,
                self.ui.detector_distance.objectName(),
                self.ui,
                {
                    self.model.update_d2theta: None,
                    self.model.clear_widget: [self.ui.min_detector_distance],
                },
            )
        )

        # slots for detector_pixelsize
        self.ui.detector_pixelsize.textEdited.connect(
            partial(
                self.model.field_changed,
                self.ui.detector_distance.objectName(),
                self.ui,
                {self.model.update_d2theta: None},
            )
        )
        self.ui.detector_pixelsize.textEdited.connect(
            partial(
                self.model.update_min_distance,
                self.ui,
            )
        )

        # slots for fringe_spacing
        self.ui.fringe_spacing.textEdited.connect(
            partial(
                self.model.field_changed,
                self.ui.fringe_spacing.objectName(),
                self.ui,
                {self.model.update_d2theta: None},
            )
        )
        self.ui.detector_pixelsize.textEdited.connect(
            partial(
                self.model.update_min_distance,
                self.ui,
            )
        )

        # slots for rocking_angle
        self.ui.rocking_angle.textEdited.connect(
            partial(
                self.model.field_changed,
                self.ui.rocking_angle.objectName(),
                self.ui,
                {
                    self.model.update_angular_sampling: None,
                    self.model.clear_widget: [self.ui.max_rocking_angle],
                },
            )
        )

        # slots for xray_energy
        self.ui.xray_energy.textEdited.connect(
            partial(
                self.model.field_changed,
                self.ui.xray_energy.objectName(),
                self.ui,
                {
                    self.model.update_xrays: [self.ui.xray_wavelength],
                    self.model.update_d2theta: None,
                },
            )
        )

        # slots for xray_wavelength
        self.ui.xray_wavelength.textEdited.connect(
            partial(
                self.model.field_changed,
                self.ui.xray_wavelength.objectName(),
                self.ui,
                {
                    self.model.update_xrays: [self.ui.xray_energy],
                    self.model.update_d2theta: None,
                },
            )
        )
        self.ui.xray_wavelength.textChanged.connect(
            partial(
                self.model.update_min_distance,
                self.ui,
            )
        )
