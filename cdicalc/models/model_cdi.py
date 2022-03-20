# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle the calculations in the CDI tab."""

import logging
import numpy as np
from pint import Quantity
from PyQt5.QtWidgets import QLineEdit
from typing import Optional

from cdicalc.models.model import Model
from cdicalc.resources.constants import EMPTY_MSG, ERROR_MSG
from cdicalc.resources.mainWindow import Ui_main_window
from cdicalc.utils.snippets_quantities import (
    CallbackParams,
    to_quantity,
    planck_constant,
    speed_of_light,
    units,
)

logger = logging.getLogger(__name__)


class ModelCDI(Model):
    """Specific class gathering the methods for the calculations in the CDI tab."""

    def update_speckle_size(self, params: CallbackParams) -> None:
        """
        Update the speckle size widget.

        :param params: an instance of CallbackParams
        """
        logger.debug("  -> update_speckle_size")
        if not isinstance(params, CallbackParams):
            logger.exception(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
            return
        widget = params.ui.speckle_size
        beam_size = to_quantity(
            params.ui.beam_size.text(),
            field_name=params.ui.beam_size.objectName(),
        )
        detector_distance = to_quantity(
            params.ui.detector_distance.text(),
            field_name=params.ui.detector_distance.objectName(),
        )
        wavelength = to_quantity(
            params.ui.xray_wavelength.text(),
            field_name=params.ui.xray_wavelength.objectName(),
        )
        if beam_size is None or detector_distance is None or wavelength is None:
            # not beautiful but mypy does not understand any()
            widget.setText(EMPTY_MSG)
        elif any(val == 0 for val in [beam_size, detector_distance, wavelength]):
            widget.setText(ERROR_MSG)
        else:
            speckle_size = wavelength * detector_distance / beam_size
            self.update_text(
                CallbackParams(
                    value=speckle_size,
                    target_widgets=widget,
                    ui=params.ui,
                )
            )
