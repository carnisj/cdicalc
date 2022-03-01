#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle the calculations."""

from pint import Quantity, UnitRegistry
from pint.errors import DimensionalityError, UndefinedUnitError
from PyQt5.QtWidgets import QLineEdit
from typing import Optional

from cdicalc.gui.mainWindow import Ui_MainWindow

default_units = {
    "distance": ("m", "~.2f"),
    "energy": ("keV", "~.2f"),
    "pixelsize": ("um", "~.0f"),
    "wavelength": ("angstrom", "~.4f"),
    "unknown": ("", "~.2f"),
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

    @staticmethod
    def energy_changed(ui: Ui_MainWindow):
        input_text = ui.energy.text()
        try:
            _energy: Optional[Quantity] = units.Quantity(input_text)
            _energy = convert_unit(
                quantity=_energy, default_unit=default_units["energy"][0]
            )
            if _energy is None:
                ui.wavelength.setText(ERROR_MSG)
                ui.helptext.setText("The X-ray energy should be in keV")
            else:
                new_wavelength = (
                        planck_constant * speed_of_light / _energy
                ).to_base_units()
                ui.wavelength.setText(
                    "{number:{precision}}".format(
                        number=new_wavelength.to(default_units["wavelength"][0]
                                                 ),
                        precision=default_units["wavelength"][1],
                    )
                )
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText("The X-ray energy should be a string: e.g. '10 keV'")
            ui.wavelength.setText(ERROR_MSG)

    @staticmethod
    def wavelength_changed(ui: Ui_MainWindow):
        input_text = ui.wavelength.text()
        try:
            _wavelength: Optional[Quantity] = units.Quantity(input_text)
            _wavelength = convert_unit(
                quantity=_wavelength, default_unit=default_units["wavelength"][0]
            )
            if _wavelength is None:
                ui.energy.setText(ERROR_MSG)
                ui.helptext.setText("The X-ray wavelength should be in angstrom")
            else:
                new_energy = (
                            planck_constant * speed_of_light / _wavelength
                ).to_base_units()
                ui.energy.setText(
                    "{number:{precision}}".format(
                        number=new_energy.to(default_units["energy"][0]
                                             ),
                        precision=default_units["energy"][1],
                    )
                )
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText(
                "The X-ray wavelength should be a string: e.g. '1.5 angstrom'"
            )
            ui.energy.setText(ERROR_MSG)

    @staticmethod
    def distance_changed(ui: Ui_MainWindow):
        input_text = ui.distance.text()
        try:
            _distance: Optional[Quantity] = units.Quantity(input_text)
            _distance = convert_unit(
                quantity=_distance, default_unit=default_units["distance"][0]
            )
            if _distance is None:
                ui.helptext.setText("The detector distance should be in m")
            else:
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText("The detector distance should be a string: e.g. '1 m'")

    @staticmethod
    def pixelsize_changed(ui: Ui_MainWindow):
        input_text = ui.pixelsize.text()
        try:
            _pixelsize: Optional[Quantity] = units.Quantity(input_text)
            _pixelsize = convert_unit(
                quantity=_pixelsize, default_unit=default_units["pixelsize"][0]
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
