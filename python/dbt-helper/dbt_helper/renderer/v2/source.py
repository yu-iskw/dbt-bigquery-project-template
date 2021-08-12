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
import re
from typing import Iterable, Optional, List, Dict, Any

from jinja2 import Environment, FileSystemLoader

import dbt_helper
from dbt_helper.parser.v2.source import DbtSources
from dbt_helper.utils import (
    DEFAULT_DBT_CONFIG_VERSION,
    get_dataset_dir,
    get_table_dir,
    generate_reference_id,
    get_templates_path,
    normalize_gcp_project,
    find_yaml_files,
    load_yaml,
    strip_date_suffix,
)


def generate_source_for_bq_dataset(
        models_dir: str,
        project: str,
        project_alias: str,
        dataset: str,
        dataset_description: Optional[str] = None,
        dataset_labels: Optional[Dict[str, str]] = None,
        version=DEFAULT_DBT_CONFIG_VERSION,
        overwrite=False,
        dry_run=False,
        templates_base_dir: Optional[str] = None) -> str:
    """Generate dbt source for a BigQuery dataset

    Args:
        models_dir (str): dbt models dir
        project (str): GCP project ID
        project_alias (str): GCP project ID alias
        dataset (str): BigQuery dataset ID
        dataset_description (str): BigQuery dataset description
        dataset_labels (str): BigQuery dataset labels
        version (str): dbt config version
        overwrite (bool): flag to overwrite
        dry_run (bool): dry run mode
        templates_base_dir (str): the base directory of template files

    Returns:
        str: path to the created directory
    """
    if dataset_labels is None:
        dataset_labels = {}

    # Render contents
    rendered_source = _render_source_yaml_for_bq_dataset(
        project=project,
        project_alias=project_alias,
        dataset=dataset,
        dataset_description=dataset_description,
        dataset_labels=dataset_labels,
        version=version,
        templates_base_dir=templates_base_dir,
    )

    # Create a directory to store
    source_filename = get_source_yaml_file_name(
        project_alias=project_alias, dataset=dataset)
    path = get_dataset_dir(
        models_dir=models_dir, project=project_alias, dataset=dataset)

    if dry_run is True:
        # TODO replace it with logging
        print(
            "[WARN] {} already exists".format(
                os.path.join(path, source_filename)))
    else:
        if os.path.isdir(path) and overwrite is False:
            raise ValueError("{} already exists".format(path))
        os.makedirs(path, exist_ok=True)

        # Write rendered contents to files
        with open(os.path.join(path, source_filename), "w") as f:
            f.write(rendered_source)
    return path


def generate_source_for_bq_table(
        models_dir: str,
        project: str,
        project_alias: str,
        dataset: str,
        table: str,
        table_description=None,
        columns=None,
        labels=None,
        tags=None,
        version=DEFAULT_DBT_CONFIG_VERSION,
        overwrite=False,
        dry_run=False,
        is_shard=False,
        templates_base_dir: Optional[str] = None) -> str:
    """Generate dbt source

    Args:
        models_dir (str): dbt models dir
        project (str): GCP project ID
        project_alias (str): GCP project ID alias
        dataset (str): BigQuery dataset ID
        table (str): BigQuery table ID
        table_description (str): table description
        columns (list): A list of columns. Each column is a dict.
        labels (dict): dict of labels
        tags (list): list of tags
        version (str): dbt config version
        overwrite (bool): flag to overwrite
        dry_run (bool): dry run mode
        is_shard (bool): shard table mode

    Returns:
        str: path to the created directory
    """
    if tags is None:
        tags = []
    if labels is None:
        labels = {}
    if columns is None:
        columns = []

    # If table ID contains date suffix, then automatically strip it.
    identifier = table
    # Strip data suffix
    if is_shard is True:
        table = strip_date_suffix(table_id=table)
        # Append `*` (e.g 'event_log_' => 'event_log_*')
        identifier = "{}*".format(table)

    # Render contents
    rendered_source = _render_source_yaml_for_bq_table(
        project=project,
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        identifier=identifier,
        table_description=table_description,
        columns=columns,
        tags=tags,
        labels=labels,
        version=version,
        templates_base_dir=templates_base_dir
    )

    # Create a directory to store
    source_filename = get_source_yaml_file_name(
        project_alias=project_alias, dataset=dataset, table=table)
    path = get_table_dir(
        models_dir=models_dir,
        project=project_alias,
        dataset=dataset,
        table=table)

    if dry_run is True:
        # TODO replace it with logging
        print(
            "[WARN] {} already exists".format(
                os.path.join(path, source_filename)))
    else:
        if os.path.isdir(path) and overwrite is False:
            raise ValueError("{} already exists".format(path))
        os.makedirs(path, exist_ok=True)

        # Write rendered contents to files
        with open(os.path.join(path, source_filename), "w") as f:
            f.write(rendered_source)
    return path


def get_source_yaml_file_name(
        project_alias: str, dataset: str, table: str = None):
    """Get source YAML file name

    Args:
        project_alias (str): GCP project ID alias
        dataset (str): BigQuery dataset ID
        table (str): BigQuery table ID

    Returns:
        str: source YAML file name
    """
    source_filename = "src_{}.yml".format(
        generate_reference_id(
            project=project_alias, dataset=dataset, table=table))
    return source_filename


def _render_source_yaml_for_bq_dataset(
    project: str,
    project_alias: str,
    dataset: str,
    dataset_description: Optional[str] = None,
    dataset_labels: Optional[Dict[str, str]] = None,
    version=DEFAULT_DBT_CONFIG_VERSION,
    templates_base_dir: Optional[str] = None,
) -> str:
    """Render a dbt source YAML

    Args:
        project (str): GCP project ID
        project_alias (str): GCP project ID alias
        dataset (str): BigQuery dataset ID
        dataset_description (str): BigQuery dataset description
        dataset_labels (dict): BigQuery dataset labels
        version (str): DBT spec version
        templates_base_dir (str): Path to the dbt models directory

    Returns:
        str: A rendered source YAML for a BigQuery dataset
    """
    if dataset_labels is None:
        dataset_labels = {}
    
    if templates_base_dir is None:
        templates_base_dir = get_templates_path()

    path = os.path.join(templates_base_dir)
    env = Environment(loader=FileSystemLoader(path))
    template = env.get_template(
        os.path.join('v2', 'source', 'dataset.source.yml.tmpl'))
    return template.render(
        project=project,
        project_alias=project_alias,
        dataset=dataset,
        dataset_description=dataset_description,
        dataset_labels=dataset_labels,
        version=version,
        dbt_helper_version=dbt_helper.VERSION,
    )


def _render_source_yaml_for_bq_table(
    project: str,
    project_alias: str,
    dataset: str,
    table: str,
    identifier: Optional[str] = None,
    table_description: Optional[str] = None,
    columns: Optional[List[Dict[str, Any]]] = None,
    labels: Optional[Dict[str, str]] = None,
    tags: Optional[List[str]] = None,
    version=DEFAULT_DBT_CONFIG_VERSION,
    templates_base_dir: Optional[str] = None,
) -> str:
    """Render a dbt source YAML

    Args:
        project (str): GCP project ID
        project_alias (str): GCP project ID alias
        dataset (str): BigQuery dataset ID
        table (str): BigQuery table ID
        identifier (str): identifer for dbt source schema
        table_description (str): table description
        columns (list): A list of columns. Each column is a dict.
        labels (dict): A dict of lables
        tags (list): A list of tags
        version (str): DBT config version
        templates_base_dir (str): Path to the dbt models directory

    Returns:
        str: A rendered source YAML for a BigQuery table
    """

    if labels is None:
        labels = {}
    if columns is None:
        columns = []
    if tags is None:
        tags = []
    
    if templates_base_dir is None:
        templates_base_dir = get_templates_path()

    path = os.path.join(templates_base_dir)
    env = Environment(loader=FileSystemLoader(path))
    template = env.get_template(
        os.path.join('v2', 'source', 'table.source.yml.tmpl'))
    return template.render(
        project=project,
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        identifier=identifier,
        table_description=table_description,
        columns=columns,
        labels=labels,
        tags=tags,
        version=version,
        dbt_helper_version=dbt_helper.VERSION,
    )


def find_source_schema_paths(
        models_dir: str,
        project_alias: str = None,
        dataset: str = None,
        table: str = None) -> Iterable[str]:
    """Find paths to dbt source schema files.

    Args:
        models_dir (str): path to dbt models.
        project_alias (str): GCP project ID alias
        dataset (str): BigQuery dataset
        table (str): BigQuery table

    Returns:
        iter: paths of dbt source schema files
    """
    # Initialize parameters
    project_alias = '.*' if project_alias is None else normalize_gcp_project(
        project=project_alias)
    dataset = '.*' if dataset is None else dataset
    table = '.*' if table is None else table

    # Create patterns
    pattern_project_alias = re.compile(r"{}".format(project_alias))
    pattern_dataset = re.compile(r"{}".format(dataset))
    pattern_table = re.compile(r"{}".format(table))

    # Get YAML files
    models_dir = os.path.abspath(models_dir)
    yaml_files = find_yaml_files(path=models_dir)
    for f in yaml_files:
        yaml_block = load_yaml(f)
        dbt_sources = DbtSources.parse(yaml_block=yaml_block)
        if dbt_sources.has_tables() is True:
            path = f.replace(models_dir, '')
            path_elements = [e for e in path.split('/') if len(e) > 0]
            tmp_project_alias = path_elements[0]
            tmp_dataset = path_elements[1]
            tmp_table = path_elements[2]
            if (pattern_project_alias.search(tmp_project_alias) and
                    pattern_dataset.search(tmp_dataset) and
                    pattern_table.search(tmp_table)):
                yield f
