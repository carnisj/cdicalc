#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

import argparse
from PyQt5.QtWidgets import QApplication
import os
import sys
import yaml

from cdicalc.gui import gui
from cdicalc.models.model_bcdi import Model_BCDI
from cdicalc.utils.parser import add_cli_parameters, check_args


def main():
    """Main function."""
    # Parse arguments from commandline
    parser = argparse.ArgumentParser()
    parser = add_cli_parameters(parser)
    cli_args = check_args(vars(parser.parse_args()))

    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Load configuration file
    config_path = cli_args.get("config")
    if config_path is not None and os.path.isfile(config_path):
        with open(config_path, "r") as configFile:
            config = yaml.load(configFile, Loader=yaml.Loader)
    else:
        config = None

    # Create an instance of the models
    model_bcdi = Model_BCDI(config=config, verbose=cli_args.get("verbose"))

    # Show the calculator's GUI
    view = gui.ApplicationWindow(model_bcdi=model_bcdi)
    view.show()

    # Execute calculator's main loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
