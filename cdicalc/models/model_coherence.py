# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Model to handle the calculations in the secondary source tab."""

from cdicalc.models.model import EMPTY_MSG, ERROR_MSG, Model
from cdicalc.utils.snippets_quantities import (
    CallbackParams,
    to_quantity,
)


class Model_Coherence(Model):
    """
    Specific class gathering methods for the calculations in the secondary source tab.

    :param config:
    :param verbose: True to have more logging output.
    """

    def __init__(self, config, verbose=False):
        super().__init__(verbose=verbose)
        self._config = config

    def update_horizontal_divergence(self, params: CallbackParams) -> None:
        """
        Update the horizontal divergence widget.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> update_angular_sampling")
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
        widget = params.ui.horizontal_divergence
        primary_source_distance = to_quantity(
            params.ui.primary_source_distance.text(),
            field_name=params.ui.primary_source_distance.objectName(),
        )
        horizontal_source_size = to_quantity(
            params.ui.horizontal_source_size.text(),
            field_name=params.ui.horizontal_source_size.objectName(),
        )

        if primary_source_distance is None or horizontal_source_size is None:
            # not beautiful but mypy does not understand any()
            widget.setText(EMPTY_MSG)
        elif primary_source_distance == 0:
            widget.setText(ERROR_MSG)
        else:
            horizontal_divergence = (
                horizontal_source_size / primary_source_distance
            ).to("radian")
            self.update_text(
                CallbackParams(
                    value=horizontal_divergence,
                    target_widgets=widget,
                    ui=params.ui,
                )
            )
        self.update_transverse_coherence(params)

    def update_vertical_divergence(self, params: CallbackParams) -> None:
        """
        Update the vertical divergence widget.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> update_angular_sampling")
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )
        widget = params.ui.vertical_divergence
        primary_source_distance = to_quantity(
            params.ui.primary_source_distance.text(),
            field_name=params.ui.primary_source_distance.objectName(),
        )
        vertical_source_size = to_quantity(
            params.ui.vertical_source_size.text(),
            field_name=params.ui.vertical_source_size.objectName(),
        )

        if primary_source_distance is None or vertical_source_size is None:
            # not beautiful but mypy does not understand any()
            widget.setText(EMPTY_MSG)
        elif primary_source_distance == 0:
            widget.setText(ERROR_MSG)
        else:
            vertical_divergence = (vertical_source_size / primary_source_distance).to(
                "radian"
            )
            self.update_text(
                CallbackParams(
                    value=vertical_divergence,
                    target_widgets=widget,
                    ui=params.ui,
                )
            )
        self.update_transverse_coherence(params)

    def update_transverse_coherence(self, params: CallbackParams) -> None:
        """
        Update the horizontal and vertical coherence length widget.

        :param params: an instance of CallbackParams
        """
        if self.verbose:
            print("  -> update_d2theta")
        if not isinstance(params, CallbackParams):
            raise TypeError(
                "params should be an instance of type Callback_params, "
                f"got {type(params)}"
            )

        wavelength = to_quantity(
            params.ui.xray_wavelength.text(),
            field_name=params.ui.xray_wavelength.objectName(),
        )
        if wavelength is None:
            params.target_widgets = [
                params.ui.horizontal_coherence_length,
                params.ui.vertical_coherence_length,
            ]
            self.clear_widget(params)
            return

        target_widget = params.ui.horizontal_coherence_length
        horizontal_divergence = to_quantity(
            params.ui.horizontal_divergence.text(),
            field_name=params.ui.horizontal_divergence.objectName(),
        )
        if horizontal_divergence is None:
            target_widget.setText(EMPTY_MSG)
        elif horizontal_divergence == 0:
            target_widget.setText(ERROR_MSG)
        else:
            horizontal_coherence = wavelength / horizontal_divergence
            self.update_text(
                CallbackParams(
                    value=horizontal_coherence,
                    target_widgets=target_widget,
                    ui=params.ui,
                )
            )

        target_widget = params.ui.vertical_coherence_length
        vertical_divergence = to_quantity(
            params.ui.vertical_divergence.text(),
            field_name=params.ui.vertical_divergence.objectName(),
        )
        if vertical_divergence is None:
            target_widget.setText(EMPTY_MSG)
        elif vertical_divergence == 0:
            target_widget.setText(ERROR_MSG)
        else:
            vertical_coherence = wavelength / vertical_divergence
            self.update_text(
                CallbackParams(
                    value=vertical_coherence,
                    target_widgets=target_widget,
                    ui=params.ui,
                )
            )
