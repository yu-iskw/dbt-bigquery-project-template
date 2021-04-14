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

import os

from jinja2 import Environment, FileSystemLoader

import dbt_helper
from dbt_helper.utils import (
    DEFAULT_DBT_CONFIG_VERSION,
    get_templates_path,
)


def generate_analysis(
        analysis_dir: str,
        path_to_analysis: str,
        owner: str,
        version=DEFAULT_DBT_CONFIG_VERSION,
        schema_filename="analysis.yml",
        overwrite=False) -> str:
    """Generate dbt analysis files

    Args:
        analysis_dir (str): dbt analysis directory
        path_to_analysis (str): relative path to a dbt analysis from the analysis directory
        owner (str): owner
        version (int): dbt config version
        schema_filename (str): analysis schema file name
        overwrite (bool): flag to overwrite or not

    Returns:
        (str): path to actual saved path
    """
    # Format inputs
    analysis_dir = os.path.realpath(analysis_dir)

    # Render contents
    rendered_sql = _render_analysis_sql()
    rendered_schema = _render_analysis_yaml(
        saved_path=path_to_analysis,
        owner=owner,
        version=version)

    # Create a directory for scaffold files
    full_path = os.path.join(analysis_dir, path_to_analysis)
    if os.path.isdir(full_path) and overwrite is False:
        raise ValueError("{} already exists".format(full_path))
    os.makedirs(full_path, exist_ok=True)

    # Write rendered contents to files
    analysis_name = get_analysis_name(saved_path=path_to_analysis)
    sql_filename = os.path.join(full_path, "{}.sql".format(analysis_name))
    with open(os.path.join(full_path, sql_filename), "w") as f:
        f.write(rendered_sql)
    with open(os.path.join(full_path, schema_filename), "w") as f:
        f.write(rendered_schema)
    return full_path


def _render_analysis_yaml(
        saved_path: str,
        owner,
        version=DEFAULT_DBT_CONFIG_VERSION,
        templates_base_dir=get_templates_path()) -> str:

    """Render a schema YAML file of analysis.

    Args:
        saved_path (str): saved path
        owner (str): owner
        version (int): dbt config version
        templates_base_dir (str): path to the template base directory

    Returns:
        (str): a rendered analysis YAML
    """

    analysis_name = get_analysis_name(saved_path)
    env = Environment(loader=FileSystemLoader(templates_base_dir))
    template = env.get_template(os.path.join('v2', 'analysis', 'analysis.yml.tmpl'))
    return template.render(
        analysis_name=analysis_name,
        owner=owner,
        version=version,
        dbt_helper_version=dbt_helper.VERSION,
    )


def _render_analysis_sql(
        version=DEFAULT_DBT_CONFIG_VERSION,
        templates_base_dir=get_templates_path()) -> str:
    """Render an analysis SQL file

    Args:
        version (int): dbt config version
        templates_base_dir (str): path to the template base directory

    Returns:
        (str): a rendered SQL file
    """
    env = Environment(loader=FileSystemLoader(templates_base_dir))
    template = env.get_template(os.path.join('v2', 'analysis', 'analysis.sql.tmpl'))
    return template.render(
        version=version,
        dbt_helper_version=dbt_helper.VERSION,
    )


def get_analysis_name(saved_path: str) -> str:
    """Get analysis ID

    Args:
        saved_path (str): path to analysis

    Returns:
        (str): analysis ID
    """
    path_elements = [e for e in saved_path.split(os.sep) if e not in ['', '.']]
    return '__'.join(path_elements)
