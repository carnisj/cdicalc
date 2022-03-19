# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Base class of the model, containing general methods."""

import logging
from pint import Quantity
from pint.errors import UndefinedUnitError
from PyQt5.QtWidgets import QLineEdit, QWidget
from typing import Callable, Dict, List, Optional, Union

from cdicalc.resources.constants import EMPTY_MSG, ERROR_MSG
from cdicalc.resources.mainWindow import Ui_main_window
from cdicalc.utils.snippets_quantities import (
    CallbackParams,
    convert_unit,
    default_units,
    units,
)

logger = logging.getLogger(__name__)


class Model:
    """Base class gathering common methods for interacting with widgets."""

    def clear_widget(self, params: CallbackParams) -> None:
        """
        Clear the text of the target widgets.

        :param params: an instance of CallbackParams
        """
        logger.debug("  -> clear_widget")
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
        logger.debug(f"\nfield changed: {field_name}")
        if not isinstance(callbacks, dict):
            logger.exception(
                "callbacks should be a dict of `callback: target_widgets`"
                f"key-value pairs, got {type(callbacks)}"
            )
            return

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
            logger.exception(f"callbacks should be a dictionary, got {type(callbacks)}")
            return
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
            logger.exception(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
            return
        if params.target_widgets is None:
            return
        if isinstance(params.target_widgets, QWidget):
            params.target_widgets = [params.target_widgets]
        if not isinstance(params.target_widgets, list):
            logger.error(
                "target_widgets should be a list of widgets, got "
                f"{type(params.target_widgets)}"
            )
            return
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
