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
    "crystal_size": ("nm", "~.0f"),
    "detector_distance": ("m", "~.2f"),
    "detector_pixelsize": ("um", "~.0f"),
    "fringe_spacing": ("", "~.1f"),
    "sampling_ratio": ("", "~.1f"),
    "unknown": ("", "~.2f"),
    "xray_energy": ("keV", "~.2f"),
    "xray_wavelength": ("angstrom", "~.4f"),
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
                quantity=_pixelsize,
                default_unit=default_units["detector_pixelsize"][0]
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

    @staticmethod
    def fringe_spacing_changed(ui: Ui_MainWindow):
        # FIXME: this is a placeholder
        input_text = ui.fringe_spacing.text()
        try:
            _fringe_spacing: Optional[Quantity] = units.Quantity(input_text)
            _fringe_spacing = convert_unit(
                quantity=_fringe_spacing,
                default_unit=default_units["fringe_spacing"][0]
            )
            if _fringe_spacing is None:
                ui.helptext.setText("The fringe spacing should be a number")
            else:
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
                default_unit=default_units["sampling_ratio"][0]
            )
            if _sampling_ratio is None:
                ui.helptext.setText("The sampling ratio should be a number")
            else:
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText(
                "The sampling ratio should be a unit-less string: e.g. '3'"
            )

    @staticmethod
    def xray_energy_changed(ui: Ui_MainWindow):
        input_text = ui.xray_energy.text()
        try:
            _energy: Optional[Quantity] = units.Quantity(input_text)
            _energy = convert_unit(
                quantity=_energy, default_unit=default_units["xray_energy"][0]
            )
            if _energy is None:
                ui.xray_wavelength.setText(ERROR_MSG)
                ui.helptext.setText("The X-ray energy should be in keV")
            else:
                new_wavelength = (
                        planck_constant * speed_of_light / _energy
                ).to_base_units()
                ui.xray_wavelength.setText(
                    "{number:{precision}}".format(
                        number=new_wavelength.to(default_units["xray_wavelength"][0]
                                                 ),
                        precision=default_units["xray_wavelength"][1],
                    )
                )
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText("The X-ray energy should be a string: e.g. '10 keV'")
            ui.xray_wavelength.setText(ERROR_MSG)

    @staticmethod
    def xray_wavelength_changed(ui: Ui_MainWindow):
        input_text = ui.xray_wavelength.text()
        try:
            _wavelength: Optional[Quantity] = units.Quantity(input_text)
            _wavelength = convert_unit(
                quantity=_wavelength, default_unit=default_units["xray_wavelength"][0]
            )
            if _wavelength is None:
                ui.xray_energy.setText(ERROR_MSG)
                ui.helptext.setText("The X-ray wavelength should be in angstrom")
            else:
                new_energy = (
                        planck_constant * speed_of_light / _wavelength
                ).to_base_units()
                ui.xray_energy.setText(
                    "{number:{precision}}".format(
                        number=new_energy.to(default_units["xray_energy"][0]
                                             ),
                        precision=default_units["xray_energy"][1],
                    )
                )
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            ui.helptext.setText(
                "The X-ray wavelength should be a string: e.g. '1.5 angstrom'"
            )
            ui.xray_energy.setText(ERROR_MSG)
