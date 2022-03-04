# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Create the GUI and connect signals to slots."""

from functools import partial

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit, QMainWindow

from cdicalc.resources.mainWindow import Ui_main_window
from cdicalc.utils.snippets_quantities import CallbackParams


class ApplicationWindow(QMainWindow):
    """Definition of the graphical user interface."""

    def __init__(self, model_bcdi):
        """View initializer."""
        super().__init__()
        self.model_bcdi = model_bcdi
        # Set some main window's properties
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(0)
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
        for _, attr in enumerate(ui_attr):
            if isinstance(getattr(self.ui, attr), QLineEdit):
                widget = getattr(self.ui, attr)
                widget.editingFinished.connect(
                    partial(self.model_bcdi.format_field, widget)
                )

    def _connect_tab_bcdi(self) -> None:
        """Connect signals to slots for the tab on BCDI calculations."""
        # slots for angular_sampling
        self.ui.angular_sampling.textEdited.connect(
            partial(
                self.model_bcdi.field_changed,
                self.ui.angular_sampling.objectName(),
                self.ui,
                {
                    self.model_bcdi.clear_widget: [self.ui.rocking_angle],
                    self.model_bcdi.update_max_rocking_angle: None,
                },
            )
        )

        # slots for crystal_size
        self.ui.crystal_size.textEdited.connect(
            partial(
                self.model_bcdi.field_changed,
                self.ui.crystal_size.objectName(),
                self.ui,
                {
                    self.model_bcdi.clear_widget: [self.ui.detector_distance],
                    self.model_bcdi.update_min_distance: None,
                    self.model_bcdi.update_angular_sampling: None,
                    self.model_bcdi.update_max_rocking_angle: None,
                },
            )
        )

        # slots for detector_distance
        self.ui.detector_distance.textEdited.connect(
            partial(
                self.model_bcdi.field_changed,
                self.ui.detector_distance.objectName(),
                self.ui,
                {
                    self.model_bcdi.update_d2theta: None,
                    self.model_bcdi.update_min_distance: None,
                },
            )
        )

        # slots for detector_pixelsize
        self.ui.detector_pixelsize.textEdited.connect(
            partial(
                self.model_bcdi.field_changed,
                self.ui.detector_pixelsize.objectName(),
                self.ui,
                {
                    self.model_bcdi.update_d2theta: None,
                    self.model_bcdi.update_min_distance: None,
                },
            )
        )

        # slots for fringe_spacing
        self.ui.fringe_spacing.textEdited.connect(
            partial(
                self.model_bcdi.field_changed,
                self.ui.fringe_spacing.objectName(),
                self.ui,
                {
                    self.model_bcdi.update_d2theta: None,
                    self.model_bcdi.update_min_distance: None,
                },
            )
        )

        # slots for rocking_angle
        self.ui.rocking_angle.textEdited.connect(
            partial(
                self.model_bcdi.field_changed,
                self.ui.rocking_angle.objectName(),
                self.ui,
                {
                    self.model_bcdi.update_angular_sampling: None,
                    self.model_bcdi.update_max_rocking_angle: None,
                },
            )
        )

        # slots for xray_energy
        self.ui.xray_energy.textEdited.connect(
            partial(
                self.model_bcdi.field_changed,
                self.ui.xray_energy.objectName(),
                self.ui,
                {
                    self.model_bcdi.update_xrays: [self.ui.xray_wavelength],
                },
            )
        )

        # slots for xray_wavelength
        self.ui.xray_wavelength.textEdited.connect(
            partial(
                self.model_bcdi.field_changed,
                self.ui.xray_wavelength.objectName(),
                self.ui,
                {
                    self.model_bcdi.update_xrays: [self.ui.xray_energy],
                },
            )
        )
        self.ui.xray_wavelength.textChanged.connect(
            partial(
                self.model_bcdi.update_d2theta,
                CallbackParams(self.ui),
            )
        )
        self.ui.xray_wavelength.textChanged.connect(
            partial(
                self.model_bcdi.update_min_distance,
                CallbackParams(self.ui),
            )
        )
        self.ui.xray_wavelength.textChanged.connect(
            partial(
                self.model_bcdi.update_angular_sampling,
                CallbackParams(self.ui),
            )
        )
        self.ui.xray_wavelength.textChanged.connect(
            partial(
                self.model_bcdi.update_max_rocking_angle,
                CallbackParams(self.ui),
            )
        )
