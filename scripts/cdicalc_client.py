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


def main():
    """Main function."""
    # Parse arguments from commandline
    parser = argparse.ArgumentParser()
    parser.add_argument("--chdir", help="Path to active directory", default="./")
    parser.add_argument(
        "--conf",
        help="Path to the YAML configuration file",
        default="./conf.yml",
    )
    parser.add_argument(
        "-v", "--verbose", help="True for more logging output", default="False"
    )
    args = parser.parse_args()
    # FIXME: parse args

    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Load configuration file
    if os.path.isfile(args.conf):
        with open(args.conf, "r") as configFile:
            config = yaml.load(configFile, Loader=yaml.Loader)
    else:
        config = None

    # Create an instance of the models
    model_bcdi = Model_BCDI(config=config, verbose=True)

    # Show the calculator's GUI
    view = gui.ApplicationWindow(model_bcdi=model_bcdi)
    view.show()

    # Execute calculator's main loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
