# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import click

from dbt_helper.cli.utils import validate_owner_callback
from dbt_helper.renderer.v2.snapshots import generate_snapshot
from dbt_helper.utils import DEFAULT_DBT_CONFIG_VERSION, parse_labels


# pylint: disable=W0613
@click.group()
@click.pass_context
def snapshot(context):
    """sub commands for dbt snapshot"""


# pylint: disable=W0613
@snapshot.command()
@click.option("--snapshots_dir", type=click.Path(exists=True), required=True,
              help="Path to the dbt model dir")
@click.option("--strategy", type=str, help="snapshot strategy", default="timestamp")
@click.option("--project_alias", type=str, required=True, help="GCP project alias")
@click.option("--dataset", type=str, required=True, help="BigQuery dataset ID")
@click.option("--table", type=str, required=True, help="BigQuery table ID")
@click.option("--labels", type=str, multiple=True, help="labels (--label ex: 'contains_pii=true')", default=[])
@click.option("--tags", type=str, multiple=True, help="tags", default=[])
@click.option("--owner", type=str, help="owner name", default="", callback=validate_owner_callback)
@click.option("--version", type=str, help="dbt config version", default=DEFAULT_DBT_CONFIG_VERSION)
@click.option("--schema_filename", type=str, help="output schema file name", default="schema.yml")
@click.option("--sql_filename", type=str, default=None,
              help="output sql file name. If it is None, then generate the name")
@click.option("--overwrite", is_flag=True, help="flag to overwrite")
@click.option("--experimental", is_flag=True, help="Create an experimental model")
@click.pass_context
def scaffold(
        context,
        snapshots_dir,
        strategy,
        project_alias,
        dataset,
        table,
        labels,
        tags,
        owner,
        version,
        schema_filename,
        sql_filename,
        overwrite,
        experimental):
    """Generate scaffold files of a dbt model"""
    labels_dict = parse_labels(labels=labels)
    path = generate_snapshot(
        snapshots_dir=snapshots_dir,
        strategy=strategy,
        project_alias=project_alias,
        dataset=dataset,
        table=table,
        labels=labels_dict,
        tags=tags,
        owner=owner,
        version=version,
        schema_filename=schema_filename,
        sql_filename=sql_filename,
        overwrite=overwrite,
        experimental=experimental,
    )

    # Show information on stdout
    click.echo("Scaffold files are generated under {}".format(path))
