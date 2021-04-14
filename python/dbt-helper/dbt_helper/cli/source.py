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
from typing import Tuple, Optional

import click

from dbt_helper.parser.v2.source import DbtSources
from dbt_helper.utils import (
    DEFAULT_DBT_CONFIG_VERSION,
    denormalize_gcp_project,
    load_yaml,
    parse_labels,
    is_sharded_identifier)
from dbt_helper.renderer.v2.source import (
    generate_source_for_bq_dataset,
    generate_source_for_bq_table,
    find_source_schema_paths)
from dbt_helper.bigquery import (
    create_bigquery_client,
    get_bigquery_dataset,
    replace_bq_dataset_metadata,
    get_updated_dataset_fields,
    get_bigquery_tables,
    get_bigquery_table,
    replace_bq_table_metadata,
    get_updated_table_fields)
from dbt_helper.parser.bigquery import extract_schema_info
from dbt_helper.tools.v2.source_updater import SourceTableUpdaterV2


# pylint: disable=W0613
@click.group()
@click.pass_context
def source(context):
    """sub commands for dbt source"""


# pylint: disable=W0613
@source.command()
@click.option("--models_dir", type=click.Path(exists=True), required=True,
              help="Path to the dbt model dir")
@click.option("--project", type=str, required=True, help="GCP project")
@click.option("--project_alias", type=str, required=True, help="GCP project alias")
@click.option("--dataset", type=str, required=True, help="BigQuery dataset ID")
@click.option("--table", type=str, required=True, help="BigQuery table ID")
@click.option("--labels", type=str, multiple=True, help="labels (--label ex: 'contains_pii=true')", default=[])
@click.option("--tags", type=str, multiple=True, help="tags", default=[])
@click.option("--version", type=int, help="dbt config version", default=DEFAULT_DBT_CONFIG_VERSION)
@click.option("--overwrite", is_flag=True, help="flag to overwrite")
@click.pass_context
def scaffold(
        context,
        models_dir,
        project,
        project_alias,
        dataset,
        table,
        labels,
        tags,
        version,
        overwrite):
    """Generate scaffold files of a dbt source"""
    labels_dict = parse_labels(labels=labels)
    path = generate_source_for_bq_table(
        models_dir=models_dir,
        project=project,
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        labels=labels_dict,
        tags=tags,
        version=version,
        overwrite=overwrite)
    # Show information on stdout
    click.echo("Scaffold files are generated under {}".format(path))


# pylint: disable=W0613
@source.command()
@click.option("--models_dir", type=click.Path(exists=True), required=True,
              help="Path to the dbt model dir")
@click.option("--project", type=str, required=True, help="GCP project")
@click.option("--project_alias", type=str, required=True, help="GCP project alias")
@click.option("--dataset", type=str, required=True, help="BigQuery dataset ID")
@click.option("--table", type=str, required=False, default=None, help="BigQuery table ID or regular expression")
@click.option("--tags", type=str, multiple=True, help="tags", default=[])
@click.option("--client_project", type=str, required=False, default=None, help="GCP project for BigQuery client")
@click.option("--version", type=str, help="dbt config version", default=DEFAULT_DBT_CONFIG_VERSION)
@click.option("--overwrite", is_flag=True, help="flag to overwrite")
@click.option("--dry_run", is_flag=True, help="dry run mode")
@click.option("--is_shard", is_flag=True, help="import a shard table")
@click.pass_context
def importing(
        context,
        models_dir,
        project,
        project_alias,
        dataset,
        table,
        tags,
        client_project,
        version,
        overwrite,
        dry_run,
        is_shard):
    """Generate dbt sources by importing metadata of existing BigQuery dataset or tables.

    If 'table' is not set, an only BigQuery dataset is imported.

    Args:
        models_dir (str): dbt models dir
        project (str): GCP project of imported BigQuery dataset or tables
        project_alias (str): Alias of GCP prject
        dataset (str): BigQuery dataset ID
        table (str): Regular expression for BigQuery tables
        tags (list): A list of dbt tags
        client_project (str): GCP project for BigQuery client
        version (str): dbt config version
        overwrite (bool): if overwrite or not
        dry_run (bool): if dry run or not
        is_shard (bool): if sharded or not
    """
    # Get tables under the dataset of the project
    client = create_bigquery_client(project=client_project)

    # Import BigQuery dataset
    if table is None:
        bq_dataset = get_bigquery_dataset(client=client, project=project, dataset_id=dataset)
        generate_source_for_bq_dataset(
            models_dir=models_dir,
            project=project,
            project_alias=project_alias,
            dataset=dataset,
            dataset_description=bq_dataset.description,
            dataset_labels=bq_dataset.labels,
            overwrite=overwrite)

    # Import BigQuery tables
    tables = get_bigquery_tables(client=client, project=project, dataset_id=dataset)
    for t in tables:
        # If a table name doesn't match the given pattern, then skip it.
        if table is None or not re.search(table, t):
            continue

        # Get table metadata
        bq_table = get_bigquery_table(
            client=client, project=project, dataset_id=dataset, table_id=t)
        table_description = bq_table.description
        columns = extract_schema_info(bq_table.schema)
        labels = bq_table.labels if bq_table.labels is not None else {}

        # Generate dbt source
        path = generate_source_for_bq_table(
            models_dir=models_dir,
            project=project,
            project_alias=project_alias,
            dataset=dataset,
            table=t,
            table_description=table_description,
            columns=columns,
            labels=labels,
            tags=tags,
            version=version,
            overwrite=overwrite,
            dry_run=dry_run,
            is_shard=is_shard)

        if dry_run is True:
            click.echo("[dry_run] Files are supposed to be generated under {} for {}.{}.{}".format(
                path, project, dataset, t))
        else:
            click.echo("Files are generated under {} for {}.{}.{}".format(
                path, project, dataset, t))


# pylint: disable=W0613,C0116
@source.command()
@click.option("--vars_path", type=click.Path(exists=True), required=True,
              help="Path to a YAML file of `vars`")
@click.option("--models_dir", type=click.Path(exists=True), required=True,
              help="Path to the dbt model dir")
@click.option("--source_path", type=click.Path(exists=True), required=True,
              help="Path to a dtt souce schema YAML file")
@click.option("--client_project", type=str, required=False, default=None, help="GCP project for BigQuery client")
@click.pass_context
def update_dbt_source(
        context,
        vars_path,
        models_dir,
        client_project,
        source_path):
    """Update a dbt source YAML with a BigQuery table"""
    # Load vars YAML file.
    vars_yaml = load_yaml(vars_path)

    # Check if the given YAML file has tables or not.
    try:
        schema_yaml = load_yaml(source_path)
        dbt_sources = DbtSources.parse(schema_yaml)
        if not dbt_sources.has_tables():
            click.echo("{} doesn't have tables".format(source_path))
            return
    except ValueError:
        click.echo("{} is not a dbt source schema".format(source_path))
        return

    # Skip if the identifier is sharded.
    if (dbt_sources.has_tables()
            and is_sharded_identifier(dbt_sources.sources[0].tables[0].identifier)):
        click.echo("{} has a sharded identifier".format(source_path))
        return

    # Extract table reference.
    gcp_project_alias, dataset, table = _extract_table_reference(
        models_dir=models_dir, source_schema_path=source_path)
    # Get the GCP project ID based on the alias.
    gcp_project = vars_yaml['projects'][denormalize_gcp_project(gcp_project_alias)]
    # Get a BigQuery table.
    client = create_bigquery_client(project=client_project)
    bq_table = get_bigquery_table(
        client=client, project=gcp_project, dataset_id=dataset, table_id=table)

    # Update dbt source schema YAML file.
    source_updater = SourceTableUpdaterV2.load(source_path)
    source_updater.update_with_bq_table(bq_table)

    # Dump the YAML
    source_updater.dump(source_path)

    # Show information on stdout
    click.echo("Updated {}".format(source_path))

# pylint: disable=W0613,C0116
@source.command()
@click.option("--models_dir", type=click.Path(exists=True), required=True,
              help="Path to the dbt model dir")
@click.option("--vars_path", type=click.Path(exists=True), required=True,
              help="Path to a YAML file of `vars`")
@click.option("--project_alias", type=str, required=False, help="GCP project alias", default=None)
@click.option("--dataset", type=str, required=False, help="BigQuery dataset ID", default=None)
@click.option("--table", type=str, required=False, help="BigQuery table ID or regular expression", default=None)
@click.option("--dry_run", is_flag=True, help="dry run mode")
@click.pass_context
def update(
        context,
        models_dir,
        vars_path,
        project_alias,
        dataset,
        table,
        dry_run):
    # Load vars YAML file.
    vars_yaml_block = load_yaml(vars_path)
    # Get source schema files
    models_dir = os.path.abspath(models_dir)
    source_schema_paths = find_source_schema_paths(
        models_dir=models_dir,
        project_alias=project_alias,
        dataset=dataset,
        table=table)

    # Loop over dbt source schema files.
    for source_schema_path in source_schema_paths:
        # Load a dbt source schema.
        yaml_block = load_yaml(source_schema_path)
        # Parse the loaded schema.
        dbt_sources = DbtSources.parse(yaml_block)
        # Extract table reference
        gcp_project_alias, _, _ = _extract_table_reference(
            models_dir=models_dir, source_schema_path=source_schema_path)
        # Get the GCP project ID based on the alias.
        gcp_project = vars_yaml_block['projects'][denormalize_gcp_project(gcp_project_alias)]
        # Update metadata
        update_bigquery_metadata(
            gcp_project=gcp_project,
            dbt_sources=dbt_sources,
            dry_run=dry_run)


# pylint: disable=W0613,C0116
@source.command()
@click.option("--models_dir", type=click.Path(exists=True), required=True,
              help="Path to the dbt model dir")
@click.option("--vars_path", type=click.Path(exists=True), required=True,
              help="Path to a YAML file of `vars`")
@click.option("--source_path", type=click.Path(exists=True), required=True,
              help="Path to a YAML file of dbt source")
@click.option("--client_project", type=str, required=False, default=None, help="GCP project")
@click.option("--dry_run", is_flag=True, help="dry run mode")
@click.pass_context
def update_from_source(
        context,
        models_dir,
        vars_path,
        source_path,
        client_project,
        dry_run):
    """Update metadata of a BigQuery table/view with a dbt source"""
    # Load vars YAML file.
    vars_yaml_block = load_yaml(vars_path)
    # Load a dbt source YAML file.
    yaml_block = load_yaml(source_path)
    dbt_sources = DbtSources.parse(yaml_block)
    # Extract table reference.
    gcp_project_alias, _, _ = _extract_table_reference(
        models_dir=models_dir, source_schema_path=source_path)
    # Get the GCP project ID based on the alias.
    # NOTE:
    # It is impossible to render something like "{{ var("projects")["project-1"] }}" here.
    # So, we have no choise to use the config file.
    gcp_project = vars_yaml_block['projects'][denormalize_gcp_project(gcp_project_alias)]
    # Update metadata
    update_bigquery_metadata(
        gcp_project=gcp_project,
        dbt_sources=dbt_sources,
        client_project=client_project,
        dry_run=dry_run)


def update_bigquery_metadata(
        gcp_project: str,
        dbt_sources: DbtSources,
        client_project: Optional[str] = None,
        dry_run=False) -> None:
    """Update metadata of a BigQuery table

    Args:
        gcp_project (str): A GCP project ID to call BigQuery API
        dbt_sources (DbtSources): An object of DbtSources
        client_project (str): A GCP project for BigQuery client
        dry_run (bool): dry run flag
    """
    client = create_bigquery_client(project=client_project)
    for dbt_source in dbt_sources.sources:
        # Get dataset ID from `sources[].name` of dbt source schema.
        dataset_id = dbt_source.name

        # Update metadata of BigQuery dataset
        bq_dataset = get_bigquery_dataset(
            client=client, project=gcp_project, dataset_id=dbt_source.name)
        replaced_dataset = replace_bq_dataset_metadata(
            dataset=bq_dataset, dbt_source=dbt_source)
        dataset_fields = get_updated_dataset_fields(replaced_dataset)
        if len(dataset_fields) > 0:
            client.update_dataset(dataset=replaced_dataset, fields=dataset_fields)

        # Update metadata of BigQuery tables
        for dbt_source_table in dbt_source.tables:
            # Get a table identifier.
            identifier = dbt_source_table.identifier
            # Skip a sharded table
            if is_sharded_identifier(identifier=identifier):
                continue
            # Get a BigQuery table with the API.
            bq_table = get_bigquery_table(
                client=client, project=gcp_project, dataset_id=dataset_id, table_id=identifier)
            # Update metadata of the table using the dbt source schema.
            bq_table = replace_bq_table_metadata(
                table=bq_table, dbt_source_table=dbt_source_table)
            # Save updated table metadata in BigQuery.
            if dry_run is False:
                table_fiields = get_updated_table_fields(bq_table)
                client.update_table(table=bq_table, fields=table_fiields)
    client.close()


def _extract_table_reference(
        models_dir: str, source_schema_path: str) -> Tuple[str, str, str]:
    """Extract table reference

    Args:
        models_dir (str):  path to dbt models dir
        source_schema_path (str): path to source schema

    Returns:
        Tuple[str, str, str]: GCP project alias, dataset ID, table ID
    """
    models_dir = os.path.abspath(models_dir)
    source_schema_path = os.path.abspath(source_schema_path)
    relative_path = source_schema_path.replace(models_dir, '')
    path_elements = [e for e in relative_path.split(os.sep) if len(e) > 0]
    (project_alias, dataset, table) = path_elements[0:3]

    if (project_alias is None or len(project_alias) == 0
            or dataset is None or len(dataset) == 0
            or table is None or len(table) == 0):
        raise ValueError("cannot extract table reference from {} and {}".format(
            models_dir, source_schema_path))
    return project_alias, dataset, table
