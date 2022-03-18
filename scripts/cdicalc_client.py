#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

import argparse

from pathlib import Path
from PyQt5.QtWidgets import QApplication
import sys

from cdicalc.gui import gui
from cdicalc.models.model_bcdi import Model_BCDI
from cdicalc.models.model_coherence import ModelCoherence
from cdicalc.models.model_config import ModelConfig
from cdicalc.utils.parser import add_cli_parameters, check_args
from cdicalc.utils.serialization import ConfigFile
from cdicalc.utils.snippets_logging import configure_logging

here = Path(__file__).parent
DEFAULT_CONFIG = str(here.parents[0] / "cdicalc/resources/config.yml")
DEFAULT_LOG = str(here.parents[0] / "cdicalc/resources/log.txt")


def main():
    """Main function."""
    configure_logging(path=DEFAULT_LOG)

    # Parse arguments from commandline
    parser = argparse.ArgumentParser()
    parser = add_cli_parameters(parser)
    cli_args = check_args(vars(parser.parse_args()))

    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Load the configuration file if provided via the command line
    config_path = cli_args.get("config")
    config_path = config_path or DEFAULT_CONFIG
    config_file = ConfigFile(path=config_path)

    # Create an instance of the models
    model_bcdi = Model_BCDI(verbose=True)# cli_args.get("verbose"))
    model_coherence = ModelCoherence(verbose=cli_args.get("verbose"))
    model_config = ModelConfig(config_file=config_file, verbose=cli_args.get("verbose"))
    # Show the calculator's GUI
    view = gui.ApplicationWindow(
        model_bcdi=model_bcdi,
        model_coherence=model_coherence,
        model_config=model_config,
    )
    view.show()

    # Execute calculator's main loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
