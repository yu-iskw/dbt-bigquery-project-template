# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import re
from typing import Tuple, Dict

import click


# pylint: disable=W0613
def validate_owner_callback(context, param, value):
    """Validate owner.

    See
    https://click.palletsprojects.com/en/7.x/options/
    """
    (is_valid, error_message) = validate_label_value(value)
    if is_valid is False:
        raise click.BadParameter(error_message)
    return value


def validate_label_value(value: str) -> Tuple[bool, str]:
    """Validate a label value.

    Args:
        value (str): a label value

    Returns:
        (bool, str): (is_valid, error_message)
    """
    pattern = re.compile(r'\s+')
    if pattern.search(value):
        modified_value = re.sub(r'\s+', '_', value)
        error_message = 'A label value contains spaces. It can be {}.'.format(modified_value)
        return False, error_message
    return True, ""


def validate_labels(labels: Dict[str, str]) -> Tuple[bool, str]:
    """Validate labels.

    Args:
        labels (dict): labels

    Returns:
        (bool, str): (is_valid, error_message)
    """
    for _, v in labels.items():
        (is_valid, error_message) = validate_label_value(v)
    return is_valid, error_message
