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
from typing import Optional, Dict, List

from jinja2 import Environment, FileSystemLoader

import dbt_helper
from dbt_helper.utils import (
    DEFAULT_DBT_CONFIG_VERSION,
    get_templates_path,
    generate_reference_id,
    get_table_dir,
)


def generate_model(
        models_dir: str,
        project_alias: str,
        dataset: str,
        table: str,
        materialization: str,
        owner: str,
        labels: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        version=DEFAULT_DBT_CONFIG_VERSION,
        schema_filename="schema.yml",
        sql_filename=None,
        doc_filename="docs.md",
        overwrite=False,
        experimental=False) -> str:
    """Generate dbt model files"""
    if tags is None:
        tags = []
    if labels is None:
        labels = {}

    # Put experimental as a label
    if experimental is True:
        labels["status"] = "experimental"

    # Render contents
    reference_id = generate_reference_id(
        project=project_alias, dataset=dataset, table=table)
    rendered_sql = _render_model_sql(
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        materialization=materialization,
        tags=tags,
        labels=labels,
        owner=owner)
    rendered_schema = _render_schema_yaml(
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        version=version,
        owner=owner)
    rendered_docs = _render_doc_md(
        project_alias=project_alias, dataset=dataset, table=table)

    # Create a directory to store
    path = get_table_dir(
        models_dir=models_dir,
        project=project_alias,
        dataset=dataset,
        table=table)
    if os.path.isdir(path) and overwrite is False:
        raise ValueError("{} already exists".format(path))
    os.makedirs(path, exist_ok=True)

    # Write rendered contents to files
    if sql_filename is None:
        sql_filename = "{}.sql".format(reference_id)
    with open(os.path.join(path, sql_filename), "w") as f:
        f.write(rendered_sql)
    with open(os.path.join(path, schema_filename), "w") as f:
        f.write(rendered_schema)
    with open(os.path.join(path, doc_filename), "w") as f:
        f.write(rendered_docs)
    return path


def _render_schema_yaml(
    project_alias: str,
    dataset: str,
    table: str,
    owner="",
    version=2,
    templates_base_dir=get_templates_path()) -> str:
    """Render a model SQL file

    Args:
        project_alias (str): GCP project IDd
        dataset (str): BigQuery dataset ID
        table (str): BigQuery table ID
        alias (str): Actual BigQuery table ID (default: `table`)
        templates_base_dir (str): the base directory of template files

    Returns:
        str: rendered schema YAML file
    """
    path = os.path.join(templates_base_dir)
    env = Environment(loader=FileSystemLoader(path))
    template = env.get_template(os.path.join('v2', 'model', 'schema.yml.tmpl'))
    return template.render(
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        version=version,
        owner=owner,
        model_reference_id=generate_reference_id(
            project=project_alias, dataset=dataset, table=table),
        dbt_helper_version=dbt_helper.VERSION,
    )


def _render_model_sql(
    materialization: str,
    project_alias: str,
    dataset: str,
    table: str,
    owner: str,
    labels: Optional[Dict[str, str]] = None,
    tags: Optional[List[str]] = None,
    templates_base_dir=get_templates_path()
) -> str:
    """Render a model SQL file

    Args:
        materialization (str): dbt materialization
        project_alias (str): GCP project ID alias
        dataset (str): BigQuery dataset ID
        table (str): BigQuery table ID
        owner (str): Owner name
        labels (dict): A dict of labels
        tags (list): A list of tags
        templates_base_dir (str): the base directory of template files

    Returns:
        str: rendered SQL file
    """
    if tags is None:
        tags = []
    if labels is None:
        labels = {}

    path = os.path.join(templates_base_dir)
    env = Environment(loader=FileSystemLoader(path))
    template = env.get_template(os.path.join('v2', 'model', 'model.sql.tmpl'))
    model_reference_id = generate_reference_id(
        project=project_alias, dataset=dataset, table=table)
    return template.render(
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        model_reference_id=model_reference_id,
        materialization=materialization,
        labels=labels,
        tags=tags,
        owner=owner,
        dbt_helper_version=dbt_helper.VERSION,
    )


def _render_doc_md(
    project_alias: str,
    dataset: str,
    table: str,
    templates_base_dir=get_templates_path()) -> str:
    """Render a model SQL file

    Args:
        project_alias (str): GCP project IDd
        dataset (str): BigQuery dataset ID
        table (str): BigQuery table ID
        templates_base_dir: the base directory of template files

    Returns:
        str: rendered SQL file
    """
    path = os.path.join(templates_base_dir)
    env = Environment(loader=FileSystemLoader(path))
    template = env.get_template(os.path.join('v2', 'model', 'docs.md.tmpl'))
    return template.render(
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        model_reference_id=generate_reference_id(
            project=project_alias, dataset=dataset, table=table),
        dbt_helper_version=dbt_helper.VERSION,
    )
