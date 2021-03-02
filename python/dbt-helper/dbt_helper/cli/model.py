# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import sys
import click

from dbt_helper.cli.utils import validate_owner_callback
from dbt_helper.renderer.v2.model import generate_model
from dbt_helper.parser.artifacts.manifest.manifest_v1 import ManifestV1
from dbt_helper.bigquery import (
    create_bigquery_client,
    drop_bigquery_dataset,
    drop_bigquery_table,
)
from dbt_helper.utils import DEFAULT_DBT_CONFIG_VERSION, parse_labels, load_json


# pylint: disable=W0613
@click.group()
@click.pass_context
def model(context):
    """sub commands for dbt model"""


# pylint: disable=W0613
@model.command()
@click.option("--models_dir", type=click.Path(exists=True), required=True,
              help="Path to the dbt model dir")
@click.option("--project_alias", type=str, required=True, help="GCP project alias")
@click.option("--dataset", type=str, required=True, help="BigQuery dataset ID")
@click.option("--table", type=str, required=True, help="BigQuery table ID")
@click.option("--materialization", help="materializing strategy", required=True,
              type=click.Choice(["table", "view", "incremental", "ephemeral"]))
@click.option("--labels", type=str, multiple=True, help="labels (--label ex: 'contains_pii=true')", default=[])
@click.option("--tags", type=str, multiple=True, help="tags", default=[])
@click.option("--owner", type=str, help="owner name", required=True, callback=validate_owner_callback)
@click.option("--version", type=str, help="dbt config version", default=DEFAULT_DBT_CONFIG_VERSION)
@click.option("--schema_filename", type=str, help="output schema file name", default="schema.yml")
@click.option("--sql_filename", type=str, default=None,
              help="output sql file name. If it is None, then generate the name")
@click.option("--overwrite", is_flag=True, help="flag to overwrite")
@click.option("--experimental", is_flag=True, help="Create an experimental model")
@click.pass_context
def scaffold(
        context,
        models_dir,
        project_alias,
        dataset,
        table,
        materialization,
        labels,
        tags,
        owner,
        version,
        schema_filename,
        sql_filename,
        overwrite,
        experimental):
    """Generate scaffold files of a dbt model based on template fiiles."""
    labels_dict = parse_labels(labels=labels)
    path = generate_model(
        models_dir=models_dir,
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        materialization=materialization,
        owner=owner,
        labels=labels_dict,
        tags=tags,
        version=version,
        schema_filename=schema_filename,
        sql_filename=sql_filename,
        overwrite=overwrite,
        experimental=experimental,
    )

    # Show information on stdout
    click.echo("Scaffold files are generated under {}".format(path))


# pylint: disable=W0613
@model.command()
@click.option("--manifest", type=click.Path(exists=True), required=True, help="Path to manifest.json")
@click.option("--schema_version", type=str, help="dbt version", required=False, default="v1")
@click.option("--delete_empty_dataset", is_flag=True,
              help="Delete a dataset if it is empty after removing disabled models")
@click.option("--resource_types", type=str, multiple=True, help="deleted resource types", default=["model", "snapshot"])
@click.option("--client_project", type=str, required=False, default=None, help="GCP project")
@click.option("--dry_run", is_flag=True, help="dry run mode")
@click.pass_context
def drop_disabled_models(
        context,
        manifest,
        schema_version,
        delete_empty_dataset,
        resource_types,
        client_project,
        dry_run):
    """Drop disabled models based on 'manifest.json'.
    We have to parepare for 'manifest.json' by executing 'dbt compile'.

    Args:
        context:
        manifest (str): path to manifest.json
        schema_version (str): schema version of manifest.json
        delete_empty_dataset (bool): drop empty datasets after dropping tables.
        resource_types (list): A list of dbt resources (e.g. 'model', 'snapshot')
        client_project (str): GCP project ID for BigQuery client
        dry_run (bool): dry run mode
    """
    click.echo("dry run: {}".format(dry_run))
    click.echo("resource_types: {}".format(",".join(resource_types)))
    click.echo("schema version: {}".format(schema_version))
    click.echo("client project: {}".format(client_project))

    # Load manifest.json
    manifest_json = load_json(manifest)
    if schema_version == "v1":
        manifest = ManifestV1.parse(json_block=manifest_json)
        # Drop tables
        client = create_bigquery_client(project=client_project)
        for disabled in manifest.disabled:
            project = disabled.database
            dataset_id = disabled.schema
            table_id = disabled.alias
            resource_type = disabled.resource_type
            # Skip if the resource type is not the acceptable resource types.
            if resource_type not in resource_types:
                click.echo("Skip dropping {}.{}.{}, since the resource type {} is not in {}".format(
                    project, dataset_id, table_id, resource_types, ",".join(resource_types)))
                continue
            # Drop a table and a dataset
            click.echo("Drop table:{}.{}.{} if exists".format(project, dataset_id, table_id))
            if dry_run is False:
                drop_bigquery_table(client=client,
                                    project=project,
                                    dataset_id=dataset_id,
                                    table_id=table_id)
                # Drop a dataset if it is empty.
                click.echo("Drop dataset:{}.{} if exists and empty".format(project, dataset_id))
                drop_bigquery_dataset(client=client,
                                      project=project,
                                      dataset_id=dataset_id)
    else:
        click.echo("The manifest version {} is not supported".format(schema_version))
        sys.exit(1)
