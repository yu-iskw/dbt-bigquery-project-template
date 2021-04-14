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

import difflib
import re
import os
import glob
from datetime import datetime
from typing import Optional, Union, List, Dict
import json

import ruamel
import ruamel.yaml

import yaml

DEFAULT_DBT_CONFIG_VERSION = 2


def get_module_root() -> str:
    """Get the root path of the module."""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_templates_path() -> str:
    """Get the path to templates directory"""
    return os.path.join(get_module_root(), "dbt_helper", "templates")


def normalize_gcp_project(project: str) -> str:
    """Normalize GCP project ID

    Args:
        project (str): GCP project ID

    Returns:
        str: normalized GCP project ID
    """
    return project.replace("-", "_")


def denormalize_gcp_project(project: str) -> str:
    """Denormalize GCP project ID

    Args:
        project (str): normalized GCP project ID

    Returns:
        str: denormalized GCP project ID
    """
    return project.replace("_", "-")


def generate_reference_id(project: str, dataset: str, table: str = None) -> str:
    """Generate a reference ID

    Args:
        project (str): GCP project ID
        dataset (str): BigQuery dataset ID
        table (str): BigQuery table ID

    Returns:
        str: A reference ID
    """
    normalized_project = normalize_gcp_project(project)
    if table is None:
        return "{}__{}".format(normalized_project, dataset)
    else:
        return "{}__{}__{}".format(normalized_project, dataset, table)


def get_dataset_dir(models_dir: str, project: str, dataset: str) -> str:
    """Get a path to a directory to store dbt files

    Args:
        models_dir (str): path to dbt models
        project (str): GCP project ID
        dataset (str): BigQuery dataset ID

    Returns:
        str: path to a directory to store dbt files
    """
    normalized_project = normalize_gcp_project(project)
    return os.path.join(models_dir, normalized_project, dataset)


def get_table_dir(
        models_dir: str, project: str, dataset: str, table: str) -> str:
    """Get a path to a directory to store dbt files

    Args:
        models_dir (str): path to dbt models
        project (str): GCP project ID
        dataset (str): BigQuery dataset ID
        table (str): BigQuery table ID

    Returns:
        str: path to a directory to store dbt files
    """
    normalized_project = normalize_gcp_project(project)
    return os.path.join(models_dir, normalized_project, dataset, table)


def parse_labels(labels: List[str] = None) -> Dict[str, str]:
    """Parse labels given by click

    Args:
        labels: A list of key-value pairs (`KEY=VALUE`)

    Returns:
        dict: A dictionary
    """
    if labels is None:
        labels = []

    label_dict = {}
    for label in labels:
        (key, value) = [x.strip() for x in label.split("=")[0:2]]
        if key in label_dict.keys():
            raise ValueError("key: {} is duplicated".format(key))
        label_dict[key] = value
    return label_dict


def find_yaml_files(path: str):
    """Find YAML files in a directory

    Args:
        path (str): path to a directory

    Returns:
        iterator:
    """
    pattern = re.compile(r"\.(yml|tools)$")
    base_dir = os.path.join(path, '**', '*')
    for file_or_dir in glob.iglob(base_dir, recursive=True):
        if os.path.isfile(file_or_dir) and pattern.search(file_or_dir):
            yield file_or_dir


def extract_diff(x: Optional[str],
                 y: Optional[str],
                 as_str=False) -> Union[List[str], str]:
    """Extract only differences between two strings.

    Args:
        x (str): string
        y (str): string
        as_str (bool): return str if it is True

    Returns:
        Union[List[str], str]:
    """
    x = x if x is not None else ""
    y = y if y is not None else ""

    differ = difflib.Differ()
    diff = differ.compare(x.splitlines(True), y.splitlines(True))
    pattern = re.compile(r'^[\-?+]')
    only_diff = [
        line for line in diff if line is not None and pattern.search(line)
    ]
    if as_str is True:
        return "\n".join(only_diff) if len(only_diff) > 0 else ""
    else:
        return only_diff


def load_yaml(path: str) -> str:
    """Load a YAML file

    Args:
        path (str): path to a YAML file

    Returns:
        dict: YAML block
    """
    with open(path, "r") as f:
        schema_source = yaml.safe_load(f.read())
        # If it can't parse the file, raise an exception.
        if not isinstance(schema_source, dict):
            raise ValueError("invalid YAML file")
        return schema_source


def load_json(path: str) -> str:
    """Load a JSON file

    Args:
        path (str): path to a JSON file

    Returns:
        dict: JSON block
    """
    with open(path, "r") as fp:
        json_block = json.load(fp)
        # If it can't parse the file, raise an exception.
        if not isinstance(json_block, dict):
            raise ValueError("invalid JSON file")
    return json_block


def strip_date_suffix(table_id: str) -> str:
    """Strip date suffix (e.g. '_20200101')

    Args:
        table_id (str): BigQuery table ID

    Returns:
        (str) stripped table ID if contains
    """
    pattern = r'_(\d{8})$'
    match_obj = re.search(pattern, table_id)
    # table_id doesn't have a pattern whose format is likely date.
    if not match_obj:
        return table_id
    try:
        # Parse date
        # NOTE: if string is not matched with the patter, raise ValueError.
        datetime.strptime(match_obj.group(1), "%Y%m%d")
        result = table_id.replace(match_obj.group(1), '')
        return result
    except ValueError:
        return table_id


def is_sharded_identifier(identifier: str):
    """Check if an identifier matches '_*$'.

    Args:
        identifier (str): table identifier

    Returns:
        bool: return true if it is a sharded identifier.
    """
    pattern = re.compile(r"_[*]$")
    if pattern.search(identifier):
        return True
    return False


def get_ruamel_yaml() -> ruamel.yaml.YAML:
    """Get a defined ruamel.tools.YAML object

    Returns:
        ruamel.tools.YAML: a defined ruamel.tools.YAML object
    """
    ruamel_yaml_obj = ruamel.yaml.YAML()
    ruamel_yaml_obj.explicit_start = True
    ruamel_yaml_obj.preserve_quotes = True
    ruamel_yaml_obj.indent(mapping=2, sequence=4, offset=2)
    return ruamel_yaml_obj
