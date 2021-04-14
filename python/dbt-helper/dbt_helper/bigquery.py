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

import copy
from typing import List, Dict, Optional

from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from google.cloud.bigquery.dataset import DatasetReference

from dbt_helper.parser.v2.source import DbtSource, DbtSourceTable


def create_bigquery_client(project: Optional[str] = None):
    """Create a BigQuery client object

    Args:
        project (str): GCP project for BigQuery client

    Returns:
        `bigquery.Client`: A BigQuery client object
    """
    if project is None or project == "":
        return bigquery.Client()
    else:
        return bigquery.Client(project=project)


def replace_bq_dataset_metadata(
        dataset: bigquery.Dataset, dbt_source: DbtSource):
    """Update

    Args:
        dataset (bigquery.Dataset): BigQuery dataset
        dbt_source (DbtSource): DbtSource object

    Returns:
        bigquery.Dataset: updated BigQuery dataset
    """
    if dbt_source.description is not None:
        dataset.description = dbt_source.description
    if dbt_source.meta is not None:
        dataset.labels = merge_bigquery_labels(
            base_labels=dataset.labels, new_labels=dbt_source.meta)
    return dataset


def get_bigquery_dataset(
        client: bigquery.Client, project: str,
        dataset_id: str) -> bigquery.Table:
    """Get BigQuery dataset

    Args:
        client (bigquery.Client): BigQuery client
        project (str): GCP project _ID
        dataset_id (str): BigQuery dataset ID

    Returns:
        google.cloud.bigquery.Dataset:
            A ``Dataaset`` instance.
    """
    dataset_ref = DatasetReference(project=project, dataset_id=dataset_id)
    try:
        return client.get_dataset(dataset_ref=dataset_ref)
    except NotFound:
        return None


def drop_bigquery_dataset(
        client: bigquery.Client, project: str,
        dataset_id: str) -> bigquery.Table:
    """Drop BigQuery dataset if it doesn't have any table

    Args:
        client (bigquery.Client): BigQuery client
        project (str): GCP project _ID
        dataset_id (str): BigQuery dataset ID
    """
    # Get tables in the dataset.
    tables = get_bigquery_tables(
        client=client, project=project, dataset_id=dataset_id)
    # Drop the dataset if it doesn't contain any table.
    if len(tables) == 0:
        dataset_ref = DatasetReference(project=project, dataset_id=dataset_id)
        client.delete_dataset(
            dataset=dataset_ref, delete_contents=False, not_found_ok=True)


def get_bigquery_tables(client: bigquery.Client, project: str,
                        dataset_id: str) -> List[str]:
    """Get BigQuery tables

    Args:
        client (bigquery.Client): BigQuery client
        project (str): GCP project ID
        dataset_id (str): BigQuery dataset ID

    Returns:
        list: A list of table IDs
    """
    dataset_ref = DatasetReference(project=project, dataset_id=dataset_id)
    dataset = get_bigquery_dataset(
        client=client, project=project, dataset_id=dataset_id)
    if dataset is None:
        return []
    else:
        tables = client.list_tables(dataset=dataset_ref)
        return [table.table_id for table in tables]


def get_bigquery_table(
        client: bigquery.Client, project: str, dataset_id: str,
        table_id: str) -> bigquery.Table:
    """Get BigQuery table

    Args:
        client (bigquery.Client): BigQuery client
        project (str): GCP project _ID
        dataset_id (str): BigQuery dataset ID
        table_id (str): BigQuery table ID

    Returns:
        google.cloud.bigquery.table.Table:
            A ``Table`` instance.
    """
    dataset_ref = DatasetReference(project=project, dataset_id=dataset_id)
    table_ref = bigquery.TableReference(
        dataset_ref=dataset_ref, table_id=table_id)
    table: bigquery.Table = client.get_table(table=table_ref)
    return table


def drop_bigquery_table(
        client: bigquery.Client, project: str, dataset_id: str,
        table_id: str) -> bigquery.Table:
    """Delete BigQuery table

    Args:
        client (bigquery.Client): BigQuery client
        project (str): GCP project _ID
        dataset_id (str): BigQuery dataset ID
        table_id (str): BigQuery table ID
    """
    dataset_ref = DatasetReference(project=project, dataset_id=dataset_id)
    table_ref = bigquery.TableReference(
        dataset_ref=dataset_ref, table_id=table_id)
    client.delete_table(table=table_ref, not_found_ok=True)


def get_updated_dataset_fields(dataset: bigquery.Dataset):
    """Get updated fields of a BigQuery dataset

    Args:
        dataset (bigquery.Dataset): BigQuery dataset

    Returns:
        (list): A list of field
    """
    fields = []
    if dataset.description is not None and len(dataset.description) > 0:
        fields.append("description")
    if dataset.labels is not None and len(dataset.labels) > 0:
        fields.append("labels")
    return sorted(fields)


def get_updated_table_fields(table: bigquery.Table):
    """Get updated fields of a BigQuery table

    Args:
        table (bigquery.Table): A BigQuery table

    Returns:
        (list): A list of field
    """
    fields = ["schema"]
    if table.description is not None and len(table.description) >= 0:
        fields.append("description")
    if table.labels is not None and len(table.labels) > 0:
        fields.append("labels")
    return sorted(fields)


def replace_bq_table_metadata(
        table: bigquery.Table,
        dbt_source_table: DbtSourceTable) -> bigquery.Table:
    """Replace a BigQuery table metadata with dbt source schema.

    Args:
        table (bigquery.Table): BigQuery table object
        dbt_source_table (DbtSourceTable): dbt source table

    Returns:
        bigquery.Table: BigQuery table object whose metadata is updated
    """
    # Deeply copy table object
    replaced_table = copy.deepcopy(table)
    # Update table meta
    if (dbt_source_table.description is not None and
            len(dbt_source_table.description) >= 0):
        replaced_table.description = dbt_source_table.description
    # Update labels
    if (dbt_source_table.meta is not None and len(dbt_source_table.meta) >= 0):
        merged_labels = merge_bigquery_labels(
            base_labels=replaced_table.labels, new_labels=dbt_source_table.meta)
        replaced_table.labels = merged_labels
    # Update schema metadata
    replaced_table.schema = update_schema_metadata_with_dbt_source_table(
        schema=table.schema, dbt_source_table=dbt_source_table)
    return replaced_table


def update_schema_metadata_with_dbt_source_table(
        schema: List[bigquery.SchemaField],
        dbt_source_table: DbtSourceTable) -> List[bigquery.SchemaField]:
    """Update schema

    Args:
        schema (List[bigquery.SchemaField]): A list of bigquery.SchemaField
        dbt_source_table (DbtSourceTable): DbtSourceTable object

    Returns:
        List[bigquery.SchemaField]: A list of updated bigquery.SchemaField
    """
    updated_schema_fields = []
    for schema_field in schema:
        updated_schema_field = update_schema_field_with_dbt_source_table(
            schema_field=schema_field, dbt_source_table=dbt_source_table)
        updated_schema_fields.append(updated_schema_field)
    return updated_schema_fields


def update_schema_field_with_dbt_source_table(
        schema_field: bigquery.SchemaField,
        dbt_source_table: DbtSourceTable,
        parent_field_names=None) -> bigquery.SchemaField:
    """Update schema field

    Args:
        schema_field (bigquery.SchemaField): bigquery.SchemaField object
        dbt_source_table (DbtSourceTable): DbtSourceTable object
        parent_field_names (List[str]): A list of nested schema field name

    Returns:
        bigquery.SchemaField: updated bigquery.SchemaField object
    """
    if parent_field_names is None:
        parent_field_names = []

    if schema_field.field_type.upper() in ["STRUCT", "RECORD"]:
        sub_schema_fields = []
        for child_schema_field in schema_field.fields:
            next_parent_field_names = parent_field_names.copy()
            next_parent_field_names.append(schema_field.name)
            sub_schema_field = update_schema_field_with_dbt_source_table(
                schema_field=child_schema_field,
                dbt_source_table=dbt_source_table,
                parent_field_names=next_parent_field_names)
            sub_schema_fields.append(sub_schema_field)
        schema_field._fields = sub_schema_fields
    else:
        schema_field = update_scalar_schema_field_with_dbt_source_table(
            schema_field=schema_field,
            dbt_source_table=dbt_source_table,
            parent_field_names=parent_field_names)
    return schema_field


def update_scalar_schema_field_with_dbt_source_table(
        schema_field: bigquery.SchemaField,
        dbt_source_table: DbtSourceTable,
        parent_field_names=None) -> bigquery.SchemaField:
    """Update a scalar schema field

    Args:
        schema_field (bigquery.SchemaField): bigquery.SchemaField object
        dbt_source_table (DbtSourceTable):  DbtSourceTable object
        parent_field_names (List[str]): A list of nested schema field name

    Returns:
        bigquery.SchemaField: updated bigquery.SchemaField object
    """
    # Create a full field name
    if parent_field_names is None:
        parent_field_names = []

    full_field_names = parent_field_names.copy()
    full_field_names.append(schema_field.name)
    full_field_name = ".".join(full_field_names)
    # Update description
    for c in dbt_source_table.columns:
        if (c.name == full_field_name and c.description is not None and
                len(c.description) > 1 and
                schema_field.description != c.description):
            # pylint: disable=W0212
            schema_field._description = c.description
            break
    return schema_field


def merge_bigquery_labels(
        base_labels: Dict[str, str], new_labels: Dict[str,
                                                      str]) -> Dict[str, str]:
    """Merge old BigQuery labels and new one.

    We have to set removed labels to None due to the specification.
    SEE: https://cloud.google.com/bigquery/docs/deleting-labels#python

    Args:
        base_labels (dict): A dict of old BigQuery labels
        new_labels (dict): A sict of new BigQuery labels

    Returns:
        (dict) A dict of updated BigQuery labels
    """
    merged_labels = {}
    # Assign all new labels.
    for new_key, new_value in new_labels.items():
        merged_labels[new_key] = new_value
    # Remove labels which don't exist in new labels.
    for base_key in base_labels.keys():
        if base_key not in new_labels.keys():
            merged_labels[base_key] = None
    return merged_labels
