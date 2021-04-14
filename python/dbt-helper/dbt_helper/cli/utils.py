# -*- coding: utf-8 -*-

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


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
