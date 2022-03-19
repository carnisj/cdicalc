# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Configure logging."""

import logging


def configure_logging(path: str, verbose: bool = False):
    """Create handlers and configure logging."""
    if not isinstance(path, str):
        raise TypeError(f"'path' should be a string, got {type(path)}")
    # create console and file handlers
    console_hdl = logging.StreamHandler()
    file_hdl = logging.FileHandler(path, mode="w", encoding="utf-8")

    # set levels
    if verbose:
        console_hdl.setLevel(logging.DEBUG)
    else:
        console_hdl.setLevel(logging.ERROR)
    file_hdl.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # add formatter to handlers
    console_hdl.setFormatter(formatter)
    file_hdl.setFormatter(formatter)

    # configure the root logger
    logging.basicConfig(level=logging.DEBUG, handlers=[console_hdl, file_hdl])
