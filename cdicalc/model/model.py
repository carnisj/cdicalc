#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle the calculations."""

from math import pi, sin, asin
from pint import Quantity, UnitRegistry
from pint.errors import DimensionalityError, UndefinedUnitError
from PyQt5.QtWidgets import QLineEdit, QWidget
from typing import Callable, Dict, List, Optional, Union

from cdicalc.gui.mainWindow import Ui_main_window

default_units = {
    "angular_sampling": ("", "~.1f", "3"),
    "crystal_size": ("nm", "~.0f", "250 nm"),
    "detector_distance": ("m", "~.2f", "1.5 m"),
    "detector_pixelsize": ("um", "~.0f", "55 um"),
    "fringe_spacing": ("", "~.1f", "5"),
    "max_rocking_angle": ("deg", "~.4f", "0.01 deg"),
    "min_detector_distance": ("m", "~.2f", "1.5 m"),
    "rocking_angle": ("deg", "~.4f", "0.01 deg"),
    "sampling_ratio": ("", "~.1f", "3"),
    "unknown": ("", "~.2f", "unknown"),
    "xray_energy": ("keV", "~.2f", "10 keV"),
    "xray_wavelength": ("angstrom", "~.4f", "1.5 angstrom"),
}

EMPTY_MSG = ""
ERROR_MSG = "ERROR"

units = UnitRegistry(system="mks")
planck_constant = units.Quantity(1, units.h).to_base_units()
speed_of_light = units.Quantity(1, units.speed_of_light).to_base_units()


def convert_unit(quantity: Optional[Quantity], default_unit: str) -> Optional[Quantity]:
    """
    Convert the quantity to the desired unit.

    If the unit is not provided, it will assume that the quantity is expressed directly
    in the default unit.

    :param quantity: a valid Quantity
    :param default_unit: a valid unit
    :return: the quantity converted to the default unit
    """
    if not isinstance(quantity, units.Quantity):
        raise TypeError(f"quantity should be a Quantity, got {type(quantity)}")
    if not isinstance(default_unit, str):
        raise TypeError(f"default_unit should be a str, got {type(default_unit)}")
    if quantity.units == units.Unit("dimensionless"):
        return units.Quantity(quantity.m, default_unit)

    try:
        quantity = quantity.to(default_unit)
        return quantity
    except DimensionalityError:
        return None


def to_quantity(text: str, field_name: str = "unknown") -> Optional[Quantity]:
    """
    Try to convert the string to a Quantity using the field default parameters.

    :param text:
    :param field_name:
    :return:
    """
    try:
        value: Optional[Quantity] = units.Quantity(text)
        return convert_unit(quantity=value, default_unit=default_units[field_name][0])
    except (AttributeError, ValueError, UndefinedUnitError):
        return None


class Model:
    def __init__(
        self,
        config,
    ):
        self._config = config
        self._d2theta: Optional[Quantity] = None
        self._dq: Optional[Quantity] = None

    @staticmethod
    def clear_widget(
        target_widgets: Union[List[QLineEdit], QLineEdit], **kwargs
    ) -> None:

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

    def field_changed(
        self,
        field_name: str,
        ui: Ui_main_window,
        callbacks: Dict[Callable, Optional[Union[List[str], str]]],
    ) -> None:
        """Update the slots connected to the changed signal."""

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
    def send_error(
        callbacks: Dict[Callable, Optional[Union[List[str], str]]],
    ) -> None:
        """
        Update all target widgets with the error message

        :param callbacks:
        :return:
        """
        for _, (_, val) in enumerate(callbacks.items()):
            if val is not None:
                if isinstance(val, str):
                    val = [val]
                for _, target_widget in enumerate(val):
                    target_widget.setText(ERROR_MSG)

    def update_angular_sampling(self, ui: Ui_main_window, **kwargs) -> None:
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
            angular_sampling = asin(wavelength / (2 * crystal_size)) / rocking_angle.to(
                "radian"
            )
            self.update_text(widget=widget, ui=ui, value=angular_sampling)

    def update_d2theta(self, ui: Ui_main_window, **kwargs) -> None:
        """
        Update the value of d2theta.

        d2theta is the angle in radian between two detector pixels, the origin of the
        reference frame being at the sample position.
        """
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
        self.update_dq(ui=ui)

    def update_crystal_size(self, ui: Ui_main_window) -> None:
        widget = ui.crystal_size
        if self._dq is not None:
            crystal_size = (2 * pi / self._dq).to("nm")
            self.update_text(widget=widget, ui=ui, value=crystal_size)
        else:
            widget.setText(EMPTY_MSG)

    def update_dq(self, ui: Ui_main_window, **kwargs) -> None:
        """
        Update the value of dq.

        dq is the difference in diffusion vector between two detector pixels, the origin
        of the reference frame being at the sample position.

        :param ui:
        :return:
        """
        xray_wavelength = to_quantity(
            ui.xray_wavelength.text(), field_name="xray_wavelength"
        )
        if any(val is None for val in {xray_wavelength, self._d2theta}):
            self._dq = None
        else:
            self._dq = 4 * pi / xray_wavelength * sin(self._d2theta / 2)
        self.update_crystal_size(ui=ui)

    def update_max_rocking_angle(self, ui: Ui_main_window, **kwargs) -> None:
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
            max_rocking_angle = units.Quantity(
                asin(wavelength / (2 * crystal_size)) / angular_sampling, "radian"
            )
            self.update_text(widget=widget, ui=ui, value=max_rocking_angle)
            ui.rocking_angle.setText(EMPTY_MSG)

    def update_min_distance(self, ui: Ui_main_window, **kwargs) -> None:
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
            val is None for val in {
                fringe_spacing, detector_pixelsize, crystal_size, wavelength
            }
        ):
            widget.setText(EMPTY_MSG)
        else:
            min_detector_distance = (
                fringe_spacing
                * detector_pixelsize
                / (2 * asin(wavelength / (2 * crystal_size)))
            )
            self.update_text(widget=widget, ui=ui, value=min_detector_distance)
            ui.detector_distance.setText(EMPTY_MSG)

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
