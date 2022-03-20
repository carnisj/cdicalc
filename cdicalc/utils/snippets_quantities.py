# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Utilities to define default units and manipulate quantities."""

from dataclasses import dataclass
import logging
from pint import Quantity, UnitRegistry
from pint.errors import DimensionalityError, UndefinedUnitError
from PyQt5.QtWidgets import QLineEdit
from typing import List, Optional, Union

from cdicalc.resources.constants import ERROR_MSG
from cdicalc.resources.mainWindow import Ui_main_window

logger = logging.getLogger(__name__)

units = UnitRegistry(system="mks")
planck_constant = units.Quantity(1, units.h).to_base_units()
speed_of_light = units.Quantity(1, units.speed_of_light).to_base_units()

default_units = {
    "angular_sampling": ("", "~.1f", "3"),
    "beam_size": ("um", "~.1f", "1 um"),
    "crystal_size": ("nm", "~.0f", "250 nm"),
    "detector_distance": ("m", "~.2f", "1.5 m"),
    "detector_pixelsize": ("um", "~.0f", "55 um"),
    "fringe_spacing": ("", "~.1f", "5"),
    "horizontal_coherence_length": ("um", "~.1f", "20 um"),
    "horizontal_source_size": ("um", "~.1f", "900 um"),
    "horizontal_divergence": ("urad", "~.2f", "12.5 urad"),
    "max_rocking_angle": ("deg", "~.4f", "0.01 deg"),
    "min_detector_distance": ("m", "~.2f", "1.5 m"),
    "primary_slits_horizontal": ("um", "~.0f", "20 um"),
    "primary_slits_vertical": ("um", "~.0f", "20 um"),
    "primary_source_distance": ("m", "~.2f", "31.5 m"),
    "rocking_angle": ("deg", "~.4f", "0.01 deg"),
    "sampling_ratio": ("", "~.1f", "3"),
    "secondary_slits_horizontal": ("um", "~.0f", "20 um"),
    "secondary_slits_vertical": ("um", "~.0f", "20 um"),
    "secondary_source_distance": ("m", "~.2f", "1.5 m"),
    "speckle_size": ("um", "~.0f", "50 um"),
    "unknown": ("", "~.2f", "unknown"),
    "vertical_coherence_length": ("um", "~.1f", "100 um"),
    "vertical_divergence": ("urad", "~.2f", "0.5 urad"),
    "vertical_source_size": ("um", "~.1f", "20 um"),
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
        logger.error(f"quantity should be a Quantity, got {type(quantity)}")
        return None
    if not isinstance(default_unit, str):
        logger.error(f"default_unit should be a str, got {type(default_unit)}")
        return None
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
    if text == ERROR_MSG:
        return None
    try:
        value: Optional[Quantity] = units.Quantity(text)
        return convert_unit(quantity=value, default_unit=default_units[field_name][0])
    except (AttributeError, ValueError, UndefinedUnitError):
        logger.info(f"can't convert {text, field_name} to a Quantity")
        return None
