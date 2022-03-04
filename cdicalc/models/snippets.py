#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Utilities to define default units and manipulate quantities."""

from dataclasses import dataclass
from pint import Quantity, UnitRegistry
from pint.errors import DimensionalityError, UndefinedUnitError
from PyQt5.QtWidgets import QLineEdit
from typing import List, Optional, Union

from cdicalc.gui.mainWindow import Ui_main_window

units = UnitRegistry(system="mks")
planck_constant = units.Quantity(1, units.h).to_base_units()
speed_of_light = units.Quantity(1, units.speed_of_light).to_base_units()

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


@dataclass
class CallbackParams:
    """Utility class to store callback parameters."""

    ui: Ui_main_window
    value: Optional[Quantity] = None
    target_widgets: Optional[Union[List[QLineEdit], QLineEdit]] = None


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