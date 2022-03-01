#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle the calculations."""

from pint import Quantity, UnitRegistry
from pint.errors import DimensionalityError, UndefinedUnitError
from PyQt5.QtWidgets import QLineEdit
from typing import Callable, List, Optional, Union

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


class Model:
    def __init__(
        self,
        config,
    ):
        self._config = config
        self._delta_twotheta: Optional[Quantity] = None
        self._delta_q: Optional[Quantity] = None

    @staticmethod
    def crystal_size_changed(ui: Ui_MainWindow):
        input_text = ui.detector_distance.text()
        try:
            _crystal_size: Optional[Quantity] = units.Quantity(input_text)
            _crystal_size = convert_unit(
                quantity=_crystal_size, default_unit=default_units["crystal_size"][0]
            )
            if _crystal_size is None:
                ui.helptext.setText("The crystal size should be in nm")
            else:
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText("The crystal size should be a string: e.g. '250 nm'")

    @staticmethod
    def detector_distance_changed(ui: Ui_MainWindow):
        input_text = ui.detector_distance.text()
        try:
            _distance: Optional[Quantity] = units.Quantity(input_text)
            _distance = convert_unit(
                quantity=_distance, default_unit=default_units["detector_distance"][0]
            )
            if _distance is None:
                ui.helptext.setText("The detector distance should be in m")
            else:
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText("The detector distance should be a string: e.g. '1 m'")

    @staticmethod
    def detector_pixelsize_changed(ui: Ui_MainWindow):
        # FIXME: this is a placeholder
        input_text = ui.detector_pixelsize.text()
        try:
            _pixelsize: Optional[Quantity] = units.Quantity(input_text)
            _pixelsize = convert_unit(
                quantity=_pixelsize, default_unit=default_units["detector_pixelsize"][0]
            )
            if _pixelsize is None:
                ui.helptext.setText("The detector pixel size should be in um")
            else:
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText(
                "The detector pixel size should be a string: e.g. '55 um'"
            )

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

    def fringe_spacing_changed(self, ui: Ui_MainWindow):
        # FIXME: this is a placeholder
        input_text = ui.fringe_spacing.text()
        try:
            _fringe_spacing: Optional[Quantity] = units.Quantity(input_text)
            _fringe_spacing = convert_unit(
                quantity=_fringe_spacing,
                default_unit=default_units["fringe_spacing"][0],
            )
            if _fringe_spacing is None:
                ui.helptext.setText("The fringe spacing should be a number")
            else:
                self.update_form(ui=ui)
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText(
                "The fringe spacing should be a unit-less string: e.g. '3'"
            )

    @staticmethod
    def sampling_ratio_changed(ui: Ui_MainWindow):
        # FIXME: this is a placeholder
        input_text = ui.sampling_ratio.text()
        try:
            _sampling_ratio: Optional[Quantity] = units.Quantity(input_text)
            _sampling_ratio = convert_unit(
                quantity=_sampling_ratio,
                default_unit=default_units["sampling_ratio"][0],
            )
            if _sampling_ratio is None:
                ui.helptext.setText("The sampling ratio should be a number")
            else:
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText(
                "The sampling ratio should be a unit-less string: e.g. '3'"
            )

    def update_form(self, ui: Ui_MainWindow):
        fringe_spacing = ui.fringe_spacing.text()
        # self._delta_twotheta =

    @staticmethod
    def field_changed(
        field_name: str,
        target_fields: Union[List[str], str],
        ui: Ui_MainWindow,
        callbacks: List[Callable],
    ) -> None:
        """Update the slots connected to the changed signal."""
        if isinstance(target_fields, str):
            target_fields = [target_fields]
        if isinstance(callbacks, Callable):
            callbacks = [callbacks]
        if len(callbacks) != len(target_fields):
            raise ValueError(
                "The number of callbacks and target fields should be identical."
            )

        widget = getattr(ui, field_name)
        input_text = widget.text()
        try:
            value: Optional[Quantity] = units.Quantity(input_text)
            value = convert_unit(
                quantity=value, default_unit=default_units[field_name][0]
            )
            if value is None:
                for _, target_field in enumerate(target_fields):
                    target_widget = getattr(ui, target_field)
                    target_widget.setText(ERROR_MSG)
                ui.helptext.setText(
                    f"{field_name} should be in {default_units[field_name][0]}"
                )
            else:
                for idx, callback in enumerate(callbacks):
                    callback(
                        field_name=field_name,
                        value=value,
                        target_field=target_fields[idx],
                        ui=ui,
                    )
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            for _, target_field in enumerate(target_fields):
                target_widget = getattr(ui, target_field)
                target_widget.setText(ERROR_MSG)
            ui.helptext.setText(
                f"{field_name} should be a string: e.g. {default_units[field_name][2]}"
            )

    @staticmethod
    def update_xrays(
        field_name: str, value: Quantity, target_field: str, ui: Ui_MainWindow
    ):
        """
        Update the X-ray parameters.

        The target field can be the X-ray energy or the X-ray wavelength.
        """
        print("In update_xrays")
        new_value = (planck_constant * speed_of_light / value).to_base_units()
        target_widget = getattr(ui, target_field)
        target_widget.setText(
            "{number:{precision}}".format(
                number=new_value.to(default_units[target_field][0]),
                precision=default_units[target_field][1],
            )
        )
