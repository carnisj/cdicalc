#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle the calculations."""

from math import pi, sin
from pint import Quantity, UnitRegistry
from pint.errors import DimensionalityError, UndefinedUnitError
from PyQt5.QtWidgets import QLineEdit
from typing import Callable, Dict, List, Optional, Union

from cdicalc.gui.mainWindow import Ui_MainWindow

default_units = {
    "crystal_size": ("nm", "~.0f", "250 nm"),
    "detector_distance": ("m", "~.2f", "1.5 m"),
    "detector_pixelsize": ("um", "~.0f", "55 um"),
    "fringe_spacing": ("", "~.1f", "5"),
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
    def format_field(field: QLineEdit) -> None:
        input_text = field.text()
        try:
            _quantity: Optional[Quantity] = units.Quantity(input_text)
            _quantity = convert_unit(
                quantity=_quantity,
                default_unit=default_units.get(field.objectName(), "unknown")[0],
            )
            if _quantity is not None:
                field.setText(
                    "{number:{precision}}".format(
                        number=_quantity,
                        precision=default_units.get(field.objectName(), "unknown")[1],
                    )
                )
        except (AttributeError, ValueError, UndefinedUnitError):
            field.setText(ERROR_MSG)

    def field_changed(
        self,
        field_name: str,
        ui: Ui_MainWindow,
        callbacks: Dict[Callable, Optional[Union[List[str], str]]],
    ) -> None:
        """Update the slots connected to the changed signal."""

        if not isinstance(callbacks, dict):
            raise TypeError(
                "callbacks should be a dict of `callback: target_fields`"
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
                self.send_error(callbacks=callbacks, ui=ui)
                ui.helptext.setText(
                    f"{field_name} should be in {default_units[field_name][0]}"
                )
            else:
                for _, callback in enumerate(callbacks):
                    callback(
                        field_name=field_name,
                        value=value,
                        target_fields=callbacks[callback],
                        ui=ui,
                    )
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            self.send_error(callbacks=callbacks, ui=ui)
            ui.helptext.setText(
                f"{field_name} should be a string: e.g. {default_units[field_name][2]}"
            )

    @staticmethod
    def send_error(
        callbacks: Dict[Callable, Optional[Union[List[str], str]]],
        ui: Ui_MainWindow,
    ) -> None:
        """
        Update all target widgets with the error message

        :param callbacks:
        :param ui:
        :return:
        """
        for _, (_, val) in enumerate(callbacks.items()):
            if val is not None:
                if isinstance(val, str):
                    val = [val]
                for _, target_field in enumerate(val):
                    target_widget = getattr(ui, target_field)
                    target_widget.setText(ERROR_MSG)

    def update_d2theta(self, ui: Ui_MainWindow, **kwargs) -> None:
        """
        Update the value of d2theta.

        d2theta is the angle in radian between two detector pixels, the origin of the
        reference frame being at the sample position.
        """
        fringe_spacing = to_quantity(
            ui.fringe_spacing.text(), field_name="fringe_spacing"
        )
        detector_pixelsize = to_quantity(
            ui.detector_pixelsize.text(), field_name="detector_pixelsize"
        )
        detector_distance = to_quantity(
            ui.detector_distance.text(), field_name="detector_distance"
        )
        print(fringe_spacing, detector_pixelsize, detector_distance)
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

    def update_crystal_size(self, ui: Ui_MainWindow) -> None:
        widget = ui.crystal_size
        if self._dq is not None:
            crystal_size = (2 * pi / self._dq).to("nm")
            self.update_text(
                widget=widget, field_name=widget.objectName(), value=crystal_size
            )
        else:
            ui.crystal_size.setText(EMPTY_MSG)

    def update_dq(self, ui: Ui_MainWindow) -> None:
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

    @staticmethod
    def update_text(
        widget: QLineEdit, field_name: str, value: Union[Quantity, str]
    ) -> None:

        if isinstance(value, units.Quantity):
            widget.setText(
                "{number:{precision}}".format(
                    number=value.to(default_units[field_name][0]),
                    precision=default_units[field_name][1],
                )
            )
        elif isinstance(value, str):
            widget.setText(value)
        else:
            raise TypeError(
                f"value should be a string or a Quantity, got {type(value)}"
            )

    def update_xrays(
        self,
        value: Quantity,
        target_fields: Optional[Union[List[str], str]],
        ui: Ui_MainWindow,
        **kwargs,
    ) -> None:
        """
        Update the X-ray parameters.

        The target field can be the X-ray energy or the X-ray wavelength.
        """
        if target_fields is None:
            raise ValueError("target_fields should be a string, got None")
        elif isinstance(target_fields, list):
            if len(target_fields) != 1:
                raise ValueError(
                    "target_fields should be either 'xray_energy' or 'xray_wavelength'"
                )
            else:
                target_field = target_fields[0]
        elif isinstance(target_fields, str):
            target_field = target_fields
        else:
            raise TypeError(f"Invalid type for target_fields: {type(target_fields)}")

        new_value = (planck_constant * speed_of_light / value).to_base_units()
        target_widget = getattr(ui, target_field)
        self.update_text(
            widget=target_widget, field_name=target_widget.objectName(), value=new_value
        )
