# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

"""Utilities for argument parsing."""

from argparse import ArgumentParser
import os
from typing import Any, Dict, Tuple


def add_cli_parameters(argument_parser: ArgumentParser) -> ArgumentParser:
    """
    Add generic parameters to the argument parser.

    :param argument_parser: an instance of argparse.ArgumentParser
    :return: the updated instance
    """
    argument_parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to the YAML configuration file",
        default="./conf.yml",
    )
    argument_parser.add_argument(
        "-v",
        "--verbose",
        type=str,
        help="True for more logging output",
        default="False",
    )
    return argument_parser


def check_args(dic: Dict[str, Any]) -> Dict[str, Any]:
    """Apply some validation on each parameter."""
    checked_keys = []
    for key, value in dic.items():
        value, is_valid = valid_param(key, value)
        if is_valid:
            dic[key] = value
            checked_keys.append(key)
        else:
            print(f"'{key}' is an unexpected key, " "its value won't be considered.")
    return {key: dic[key] for key in checked_keys}


def valid_param(key: str, value: Any) -> Tuple[Any, bool]:
    """
    Validate a key value pair corresponding to an input parameter.

    It will raise an exception if the check fails.

    :param key: name of the parameter
    :param value: the value of the parameter
    :return: a tuple (formatted_value, is_valid). is_valid is True if the key
     is valid, False otherwise.
    """
    is_valid = True

    # convert 'None' to None
    if value == "None":
        value = None

    # convert 'True' to True
    if isinstance(value, str) and value.lower() == "true":
        value = True

    # convert 'False' to False
    if isinstance(value, str) and value.lower() == "false":
        value = False

    # test the booleans first
    if key == "verbose":
        if not isinstance(value, bool):
            raise TypeError(f"verbose should be a boolean, got {type(value)}")
    elif key == "config":
        if not isinstance(value, str):
            raise TypeError(f"config should be a str, got {type(value)}")
        if not os.path.isfile(value):
            value = None
    else:
        # this key is not in the known parameters
        is_valid = False

    return value, is_valid
