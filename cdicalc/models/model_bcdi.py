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

from cdicalc.resources.mainWindow import Ui_main_window
from cdicalc.utils.snippets_quantities import (
    CallbackParams,
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
    """
    Base class gathering common methods for interacting with widgets.

    :param verbose: True to have more logging output.
    """

    def __init__(self, verbose=False):
        if not isinstance(verbose, bool):
            raise TypeError(f"verbose should be a boolean, got {type(verbose)}")
        self.verbose = verbose

    def clear_widget(self, params: CallbackParams) -> None:
        """
        Clear the text of the target widgets.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> clear_widget")
        params.value = None
        self.update_text(params)

    def field_changed(
        self,
        field_name: str,
        ui: Ui_main_window,
        callbacks: Dict[Callable, Optional[Union[List[QLineEdit], QLineEdit]]],
    ) -> None:
        """
        Update the slots connected to the modified signal.

        :param field_name: name of the field which was modified
        :param ui: a pointer to the main window
        :param callbacks: a dictionary of (Callable, target widgets) key-value pairs
        """
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
                ui.helptext.setText(EMPTY_MSG)
        except (AttributeError, ValueError, UndefinedUnitError):
            value = None
            self.send_error(callbacks=callbacks)
            ui.helptext.setText(
                f" enter a valid {field_name}: " f"e.g. {default_units[field_name][2]}"
            )

        for _, callback in enumerate(callbacks):
            callback(
                CallbackParams(
                    value=value,
                    target_widgets=callbacks[callback],
                    ui=ui,
                )
            )

    @staticmethod
    def format_field(widget: QLineEdit) -> None:
        """
        Edit the widget string using the defined unit and format.

        :param widget: the widget to be formatted
        """
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
        Update all target widgets with the error message.

        :param callbacks: a dictionary of (Callable, target widgets) key-value pairs
        """
        if not isinstance(callbacks, dict):
            raise TypeError(f"callbacks should be a dictionary, got {type(callbacks)}")
        for _, target_widgets in callbacks.items():
            if target_widgets is not None:
                if isinstance(target_widgets, QWidget):
                    target_widgets = [target_widgets]
                for _, widget in enumerate(target_widgets):
                    if isinstance(widget, QWidget) and hasattr(widget, "setText"):
                        widget.setText(ERROR_MSG)

    @staticmethod
    def update_text(params: CallbackParams) -> None:
        """
        Update the text of the target widgets with the new value.

        :param params: an instance of CallbackParams
        """
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
        if params.target_widgets is None:
            return
        if isinstance(params.target_widgets, QWidget):
            params.target_widgets = [params.target_widgets]
        if not isinstance(params.target_widgets, list):
            raise TypeError(
                "target_widgets should be a list of widgets, got "
                f"{type(params.target_widgets)}"
            )

        if isinstance(params.value, units.Quantity):
            for _, widget in enumerate(params.target_widgets):
                if isinstance(widget, QWidget) and hasattr(widget, "setText"):
                    try:
                        widget.setText(
                            "{number:{precision}}".format(
                                number=params.value.to(
                                    default_units[widget.objectName()][0]
                                ),
                                precision=default_units[widget.objectName()][1],
                            )
                        )
                    except KeyError:
                        params.ui.helptext.setText(
                            f" {widget.objectName()} not defined in default units"
                        )
                        widget.setText(str(params.value))
        elif isinstance(params.value, str):
            for _, widget in enumerate(params.target_widgets):
                if isinstance(widget, QWidget) and hasattr(widget, "setText"):
                    widget.setText(params.value)
        else:  # None
            for _, widget in enumerate(params.target_widgets):
                if isinstance(widget, QWidget) and hasattr(widget, "setText"):
                    widget.setText(EMPTY_MSG)


class Model_BCDI(Model):
    """
    Specific class gathering the methods for the calculations in the BCDI tab.

    :param config:
    :param verbose: True to have more logging output.
    """

    def __init__(self, config, verbose=False):
        super().__init__(verbose=verbose)
        self._config = config
        self._d2theta: Optional[Quantity] = None
        self._dq: Optional[Quantity] = None

    def update_angular_sampling(self, params: CallbackParams) -> None:
        """
        Update the angular sampling widget.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> update_angular_sampling")
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
        if params.ui.rocking_angle.text() == "":
            return
        widget = params.ui.angular_sampling
        crystal_size = to_quantity(
            params.ui.crystal_size.text(),
            field_name=params.ui.crystal_size.objectName(),
        )
        rocking_angle = to_quantity(
            params.ui.rocking_angle.text(),
            field_name=params.ui.rocking_angle.objectName(),
        )
        wavelength = to_quantity(
            params.ui.xray_wavelength.text(),
            field_name=params.ui.xray_wavelength.objectName(),
        )

        if crystal_size is None or rocking_angle is None or wavelength is None:
            # not beautiful but mypy does not understand any()
            widget.setText(EMPTY_MSG)
        elif any(val == 0 for val in [crystal_size, rocking_angle, wavelength]):
            widget.setText(ERROR_MSG)
        else:
            angular_sampling = np.arcsin(
                wavelength / (2 * crystal_size)
            ) / rocking_angle.to("radian")
            self.update_text(
                CallbackParams(
                    value=angular_sampling,
                    target_widgets=widget,
                    ui=params.ui,
                )
            )

    def _update_crystal_size(self, ui: Ui_main_window) -> None:
        """
        Update the crystal size widget.

        :param ui: a pointer to the main window
        """
        if self.verbose:
            print("  -> _update_crystal_size")
        widget = ui.crystal_size
        if self._dq is None:
            widget.setText(EMPTY_MSG)
        elif self._dq == 0:
            widget.setText(ERROR_MSG)
        else:
            crystal_size = (2 * np.pi / self._dq).to("nm")
            self.update_text(
                CallbackParams(
                    value=crystal_size,
                    target_widgets=widget,
                    ui=ui,
                )
            )

        self.update_angular_sampling(CallbackParams(ui=ui))

    def update_d2theta(self, params: CallbackParams) -> None:
        """
        Update the value of d2theta.

        d2theta is the angle in radian between two detector pixels, the origin of the
        reference frame being at the sample position.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> update_d2theta")
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
        if params.ui.detector_distance.text() == "":
            return
        fringe_spacing = to_quantity(
            params.ui.fringe_spacing.text(),
            field_name=params.ui.fringe_spacing.objectName(),
        )
        detector_pixelsize = to_quantity(
            params.ui.detector_pixelsize.text(),
            field_name=params.ui.detector_pixelsize.objectName(),
        )
        # use the detector distance if defined, or try with the minimum detector
        # distance in the contrary
        detector_distance = to_quantity(
            params.ui.detector_distance.text(),
            field_name=params.ui.detector_distance.objectName(),
        ) or to_quantity(
            params.ui.min_detector_distance.text(),
            field_name=params.ui.min_detector_distance.objectName(),
        )

        if (
            fringe_spacing is None
            or detector_distance is None
            or detector_pixelsize is None
            or detector_distance == 0
        ):
            # not beautiful but mypy does not understand any()
            self._d2theta = None
        else:
            self._d2theta = units.Quantity(
                fringe_spacing * detector_pixelsize / detector_distance, "radian"
            )
        self._update_dq(ui=params.ui)

    def _update_dq(self, ui: Ui_main_window) -> None:
        """
        Update the value of dq.

        dq is the difference in diffusion vector between two detector pixels, the origin
        of the reference frame being at the sample position.

        :param ui: a pointer to the main window
        """
        if self.verbose:
            print("  -> _update_dq")
        xray_wavelength = to_quantity(
            ui.xray_wavelength.text(), field_name="xray_wavelength"
        )

        if self._d2theta is None or xray_wavelength is None or xray_wavelength == 0:
            # not beautiful but mypy does not understand any()
            self._dq = None
        else:
            self._dq = 4 * np.pi / xray_wavelength * np.sin(self._d2theta / 2)
        self._update_crystal_size(ui=ui)

    def update_max_rocking_angle(self, params: CallbackParams) -> None:
        """
        Update the max_rocking_angle widget.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> update_max_rocking_angle")
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
        if params.ui.rocking_angle.text() != "":
            params.ui.max_rocking_angle.setText(EMPTY_MSG)
            return
        widget = params.ui.max_rocking_angle
        crystal_size = to_quantity(
            params.ui.crystal_size.text(),
            field_name=params.ui.crystal_size.objectName(),
        )
        angular_sampling = to_quantity(
            params.ui.angular_sampling.text(),
            field_name=params.ui.angular_sampling.objectName(),
        )
        wavelength = to_quantity(
            params.ui.xray_wavelength.text(),
            field_name=params.ui.xray_wavelength.objectName(),
        )

        if angular_sampling is None or crystal_size is None or wavelength is None:
            # not beautiful but mypy does not understand any()
            widget.setText(EMPTY_MSG)
        elif any(val == 0 for val in [angular_sampling, crystal_size, wavelength]):
            widget.setText(ERROR_MSG)
        else:
            max_rocking_angle: Quantity = units.Quantity(
                np.arcsin(wavelength / (2 * crystal_size)) / angular_sampling, "radian"
            )
            self.update_text(
                CallbackParams(
                    value=max_rocking_angle,
                    target_widgets=widget,
                    ui=params.ui,
                )
            )
            params.ui.rocking_angle.setText(EMPTY_MSG)

    def update_min_distance(self, params: CallbackParams) -> None:
        """
        Update the min_distance widget.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> update_min_distance")
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
        if params.ui.detector_distance.text() != "":
            params.ui.min_detector_distance.setText(EMPTY_MSG)
            return
        widget = params.ui.min_detector_distance
        fringe_spacing = to_quantity(
            params.ui.fringe_spacing.text(),
            field_name=params.ui.fringe_spacing.objectName(),
        )
        detector_pixelsize = to_quantity(
            params.ui.detector_pixelsize.text(),
            field_name=params.ui.detector_pixelsize.objectName(),
        )
        crystal_size = to_quantity(
            params.ui.crystal_size.text(),
            field_name=params.ui.crystal_size.objectName(),
        )
        wavelength = to_quantity(
            params.ui.xray_wavelength.text(),
            field_name=params.ui.xray_wavelength.objectName(),
        )
        if (
            crystal_size is None
            or detector_pixelsize is None
            or fringe_spacing is None
            or wavelength is None
        ):
            # not beautiful but mypy does not understand any()
            widget.setText(EMPTY_MSG)
        elif any(
            val == 0
            for val in [crystal_size, detector_pixelsize, fringe_spacing, wavelength]
        ):
            widget.setText(ERROR_MSG)
        else:
            min_detector_distance = (
                fringe_spacing
                * detector_pixelsize
                / (2 * np.arcsin(wavelength / (2 * crystal_size)))
            )
            self.update_text(
                CallbackParams(
                    value=min_detector_distance,
                    target_widgets=widget,
                    ui=params.ui,
                )
            )
            params.ui.detector_distance.setText(EMPTY_MSG)

    def update_xrays(self, params: CallbackParams) -> None:
        """
        Update the X-ray related widgets..

        The target field can be the X-ray energy or the X-ray wavelength.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> update_xrays")
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
        if params.target_widgets is None:
            raise ValueError(
                "target_widgets should be a widget or a list of widgets, not None"
            )
        elif isinstance(params.target_widgets, list):
            if len(params.target_widgets) != 1:
                raise ValueError("target_widgets should be a single widget")
            else:
                target_widget = params.target_widgets[0]
        elif isinstance(params.target_widgets, QLineEdit):
            target_widget = params.target_widgets
        else:
            raise TypeError(
                f"Invalid type for target_widgets: {type(params.target_widgets)}"
            )

        if params.value is None or params.value == 0:
            target_widget.setText(ERROR_MSG)
        else:
            new_value = (
                planck_constant * speed_of_light / params.value
            ).to_base_units()

            self.update_text(
                CallbackParams(
                    value=new_value,
                    target_widgets=target_widget,
                    ui=params.ui,
                )
            )
