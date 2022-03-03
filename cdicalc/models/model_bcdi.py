#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle the calculations."""

import numpy as np
from pint import Quantity
from pint.errors import UndefinedUnitError
from PyQt5.QtWidgets import QLineEdit, QWidget
from typing import Callable, Dict, List, Optional, Union

from cdicalc.gui.mainWindow import Ui_main_window
from cdicalc.models.snippets_quantities import (
    convert_unit,
    default_units,
    to_quantity,
    planck_constant,
    speed_of_light,
    units,
)

EMPTY_MSG = ""
ERROR_MSG = "ERROR"


class Model:
    def __init__(self, verbose=False):
        if not isinstance(verbose, bool):
            raise TypeError(f"verbose should be a boolean, got {type(verbose)}")
        self.verbose = verbose

    def clear_widget(
        self, target_widgets: Union[List[QLineEdit], QLineEdit], **kwargs
    ) -> None:
        if self.verbose:
            print("  -> clear_widget")
        if isinstance(target_widgets, QWidget):
            target_widgets = [target_widgets]

        if isinstance(target_widgets, list):
            for _, widget in enumerate(target_widgets):
                if isinstance(widget, QWidget) and hasattr(widget, "setText"):
                    widget.setText(EMPTY_MSG)
                else:
                    raise TypeError(f"Expecting a QLineEdit, got {type(widget)}")
        else:
            raise TypeError(
                f"Expecting a widget or a list of widgets, got {type(target_widgets)}"
            )

    def field_changed(
        self,
        field_name: str,
        ui: Ui_main_window,
        callbacks: Dict[Callable, Optional[Union[List[QLineEdit], QLineEdit]]],
    ) -> None:
        """Update the slots connected to the changed signal."""
        if self.verbose:
            print("\nfield changed:", field_name)
        if not isinstance(callbacks, dict):
            raise TypeError(
                "callbacks should be a dict of `callback: target_widgets`"
                f"key-value pairs, got {type(callbacks)}"
            )

        widget = getattr(ui, field_name)
        input_text = widget.text()
        try:
            value: Optional[Quantity] = units.Quantity(input_text)
            value = convert_unit(
                quantity=value, default_unit=default_units[field_name][0]
            )
            if value is None:
                self.send_error(callbacks=callbacks)
                ui.helptext.setText(
                    f" enter a valid {field_name}: "
                    f"e.g. {default_units[field_name][2]}"
                )
            else:
                for _, callback in enumerate(callbacks):
                    callback(
                        value=value,
                        target_widgets=callbacks[callback],
                        ui=ui,
                    )
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            self.send_error(callbacks=callbacks)
            ui.helptext.setText(
                f" enter a valid {field_name}: " f"e.g. {default_units[field_name][2]}"
            )

    @staticmethod
    def format_field(widget: QLineEdit) -> None:
        input_text = widget.text()
        try:
            _quantity: Optional[Quantity] = units.Quantity(input_text)
            _quantity = convert_unit(
                quantity=_quantity,
                default_unit=default_units.get(widget.objectName(), "unknown")[0],
            )
            if _quantity is not None:
                widget.setText(
                    "{number:{precision}}".format(
                        number=_quantity,
                        precision=default_units.get(widget.objectName(), "unknown")[1],
                    )
                )
        except (AttributeError, UndefinedUnitError):
            widget.setText(ERROR_MSG)
        except ValueError:  # the widget is empty
            widget.setText(EMPTY_MSG)

    @staticmethod
    def send_error(
        callbacks: Dict[Callable, Optional[Union[List[QLineEdit], QLineEdit]]],
    ) -> None:
        """
        Update all target widgets with the error message

        :param callbacks:
        :return:
        """
        for _, (_, val) in enumerate(callbacks.items()):
            if val is not None:
                if isinstance(val, QWidget):
                    val = [val]
                for _, target_widget in enumerate(val):
                    if isinstance(target_widget, QLineEdit):
                        target_widget.setText(ERROR_MSG)

    @staticmethod
    def update_text(
        widget: QLineEdit, ui: Ui_main_window, value: Union[Quantity, str]
    ) -> None:

        if isinstance(value, units.Quantity):
            try:
                widget.setText(
                    "{number:{precision}}".format(
                        number=value.to(default_units[widget.objectName()][0]),
                        precision=default_units[widget.objectName()][1],
                    )
                )
            except KeyError:
                ui.helptext.setText(
                    f" {widget.objectName()} not defined in default units"
                )
                widget.setText(str(value))
        elif isinstance(value, str):
            widget.setText(value)
        else:
            raise TypeError(
                f"value should be a string or a Quantity, got {type(value)}"
            )


class Model_BCDI(Model):
    def __init__(self, config, verbose=False):
        super().__init__(verbose=verbose)
        self._config = config
        self._d2theta: Optional[Quantity] = None
        self._dq: Optional[Quantity] = None

    def update_angular_sampling(self, ui: Ui_main_window, **kwargs) -> None:
        if self.verbose:
            print("  -> update_angular_sampling")
        if ui.rocking_angle.text() == "":
            return
        widget = ui.angular_sampling
        crystal_size = to_quantity(
            ui.crystal_size.text(), field_name=ui.crystal_size.objectName()
        )
        rocking_angle = to_quantity(
            ui.rocking_angle.text(), field_name=ui.rocking_angle.objectName()
        )
        wavelength = to_quantity(
            ui.xray_wavelength.text(), field_name=ui.xray_wavelength.objectName()
        )
        if any(val is None for val in {crystal_size, rocking_angle, wavelength}) or (
            rocking_angle == 0
        ):
            widget.setText(EMPTY_MSG)
        else:
            angular_sampling = np.arcsin(
                wavelength / (2 * crystal_size)
            ) / rocking_angle.to("radian")
            self.update_text(widget=widget, ui=ui, value=angular_sampling)

    def _update_crystal_size(self, ui: Ui_main_window) -> None:
        if self.verbose:
            print("  -> _update_crystal_size")
        widget = ui.crystal_size
        if self._dq is not None:
            crystal_size = (2 * np.pi / self._dq).to("nm")
            self.update_text(widget=widget, ui=ui, value=crystal_size)
        else:
            widget.setText(EMPTY_MSG)
        self.update_angular_sampling(ui=ui)

    def update_d2theta(self, ui: Ui_main_window, **kwargs) -> None:
        """
        Update the value of d2theta.

        d2theta is the angle in radian between two detector pixels, the origin of the
        reference frame being at the sample position.
        """
        if self.verbose:
            print("  -> update_d2theta")
        if ui.detector_distance.text() == "":
            return
        fringe_spacing = to_quantity(
            ui.fringe_spacing.text(), field_name=ui.fringe_spacing.objectName()
        )
        detector_pixelsize = to_quantity(
            ui.detector_pixelsize.text(), field_name=ui.detector_pixelsize.objectName()
        )
        # use the detector distance if defined, or try with the minimum detector
        # distance in the contrary
        detector_distance = to_quantity(
            ui.detector_distance.text(), field_name=ui.detector_distance.objectName()
        ) or to_quantity(
            ui.min_detector_distance.text(),
            field_name=ui.min_detector_distance.objectName(),
        )

        if any(
            val is None
            for val in {fringe_spacing, detector_pixelsize, detector_distance}
        ):
            self._d2theta = None
        else:
            self._d2theta = units.Quantity(
                fringe_spacing * detector_pixelsize / detector_distance, "radian"
            )
        self._update_dq(ui=ui)

    def _update_dq(self, ui: Ui_main_window, **kwargs) -> None:
        """
        Update the value of dq.

        dq is the difference in diffusion vector between two detector pixels, the origin
        of the reference frame being at the sample position.

        :param ui:
        :return:
        """
        if self.verbose:
            print("  -> _update_dq")
        xray_wavelength = to_quantity(
            ui.xray_wavelength.text(), field_name="xray_wavelength"
        )
        if any(val is None for val in {xray_wavelength, self._d2theta}):
            self._dq = None
        else:
            self._dq = 4 * np.pi / xray_wavelength * np.sin(self._d2theta / 2)
        self._update_crystal_size(ui=ui)

    def update_max_rocking_angle(self, ui: Ui_main_window, **kwargs) -> None:
        if self.verbose:
            print("  -> update_max_rocking_angle")
        if ui.rocking_angle.text() != "":
            return
        widget = ui.max_rocking_angle
        crystal_size = to_quantity(
            ui.crystal_size.text(), field_name=ui.crystal_size.objectName()
        )
        angular_sampling = to_quantity(
            ui.angular_sampling.text(), field_name=ui.angular_sampling.objectName()
        )
        wavelength = to_quantity(
            ui.xray_wavelength.text(), field_name=ui.xray_wavelength.objectName()
        )
        if any(val is None for val in {crystal_size, angular_sampling, wavelength}) or (
            angular_sampling == 0
        ):
            widget.setText(EMPTY_MSG)
        else:
            max_rocking_angle: Quantity = units.Quantity(
                np.arcsin(wavelength / (2 * crystal_size)) / angular_sampling, "radian"
            )
            self.update_text(widget=widget, ui=ui, value=max_rocking_angle)
            ui.rocking_angle.setText(EMPTY_MSG)

    def update_min_distance(self, ui: Ui_main_window, **kwargs) -> None:
        if self.verbose:
            print("  -> update_min_distance")
        if ui.detector_distance.text() != "":
            return
        widget = ui.min_detector_distance
        fringe_spacing = to_quantity(
            ui.fringe_spacing.text(), field_name=ui.fringe_spacing.objectName()
        )
        detector_pixelsize = to_quantity(
            ui.detector_pixelsize.text(), field_name=ui.detector_pixelsize.objectName()
        )
        crystal_size = to_quantity(
            ui.crystal_size.text(), field_name=ui.crystal_size.objectName()
        )
        wavelength = to_quantity(
            ui.xray_wavelength.text(), field_name=ui.xray_wavelength.objectName()
        )
        if any(
            val is None
            for val in {fringe_spacing, detector_pixelsize, crystal_size, wavelength}
        ):
            widget.setText(EMPTY_MSG)
        else:
            min_detector_distance = (
                fringe_spacing
                * detector_pixelsize
                / (2 * np.arcsin(wavelength / (2 * crystal_size)))
            )
            self.update_text(widget=widget, ui=ui, value=min_detector_distance)
            ui.detector_distance.setText(EMPTY_MSG)

    def update_xrays(
        self,
        value: Quantity,
        target_widgets: Optional[Union[List[QLineEdit], QLineEdit]],
        ui: Ui_main_window,
        **kwargs,
    ) -> None:
        """
        Update the X-ray parameters.

        The target field can be the X-ray energy or the X-ray wavelength.
        """
        if self.verbose:
            print("  -> update_xrays")
        if target_widgets is None:
            raise ValueError(
                "target_widgets should be a widget or a list of widgets, not None"
            )
        elif isinstance(target_widgets, list):
            if len(target_widgets) != 1:
                raise ValueError("target_widgets should be a single widget")
            else:
                target_widget = target_widgets[0]
        elif isinstance(target_widgets, QLineEdit):
            target_widget = target_widgets
        else:
            raise TypeError(f"Invalid type for target_widgets: {type(target_widgets)}")

        if value == 0:
            target_widget.setText(EMPTY_MSG)
        else:
            new_value = (planck_constant * speed_of_light / value).to_base_units()
            self.update_text(widget=target_widget, ui=ui, value=new_value)
