# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import unittest

import yaml

from google.cloud import bigquery

from dbt_helper.bigquery import (
    replace_bq_dataset_metadata,
    get_updated_dataset_fields,
    get_bigquery_table,
    replace_bq_table_metadata,
    merge_bigquery_labels,
    get_updated_table_fields,
)
from dbt_helper.parser.v2.source import DbtSources


def create_test_dataset(description=None, labels=None):
    """Create a test BigQuery dataset."""
    if description is None:
        description = ""
    if labels is None:
        labels = {}

    dataset_ref = bigquery.DatasetReference(project="test_project", dataset_id="test_dataset")
    dataset = bigquery.Dataset(dataset_ref=dataset_ref)
    dataset.description = description
    dataset.labels = labels
    return dataset


def create_test_table(labels=None):
    """Create a test table."""
    if labels is None:
        labels = {}

    schema = [
        bigquery.SchemaField("id", "INTEGER", description="user ID"),
        bigquery.SchemaField(
            "address",
            "STRUCT",
            fields=[
                bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("state", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("zip", "STRING", mode="NULLABLE"),
            ],
        ),
    ]
    table = bigquery.Table("test-project.test_dataset.test_table", schema=schema)
    table.description = "original table description"
    table.labels = labels
    return table


# pylint: disable=C0116
def create_test_dbt_sources_yaml():
    """Create a test source schema YAML."""
    yaml_str = '''
version: 2
sources:
  - name: test_name
    database: "test-project"
    description: "test description"
    meta:
      x: a
      y: b
      z: c
    tables:
      - name: test_table
        description: "updated table description"
        identifier: test_table
        meta:
          owner: "dummy owner"
          contains_pii: "false"
        columns:
          - name: id
            description: "updated user ID"
          - name: address.city
            description: "city"
          - name: address.state
            description: "state"
          - name: zip
            description: "zip code"
    '''
    return yaml.safe_load(yaml_str)


class TestBigQuery(unittest.TestCase):

    def test_replace_bigquery_dataset_metadata(self):
        # Create a test BigQuery dataset
        dataet = create_test_dataset(description="old",
                                     labels={"old": "old_value", "x": "old_value"})
        # Load DbtSource
        dbt_sources = DbtSources.parse(yaml_block=create_test_dbt_sources_yaml())
        dbt_source = dbt_sources.sources[0]

        replaced_dataset = replace_bq_dataset_metadata(
            dataset=dataet,
            dbt_source=dbt_source)
        self.assertEqual(replaced_dataset.description, "test description")
        self.assertDictEqual(replaced_dataset.labels,
                             {'old': None, 'x': 'a', 'y': 'b', 'z': 'c'})

    # This test requires a real GCP credentials.
    @unittest.SkipTest
    def test_get_table(self):
        project = "test-project"
        dataset_id = "test_dataset"
        table_id = "test_table"

        client = bigquery.Client(project=project)
        table = get_bigquery_table(
            client=client, project=project, dataset_id=dataset_id, table_id=table_id)
        self.assertEqual(table.schema, None)

    def test_update_bigquery_table_metadata(self):
        # Create a mock DbtSources
        yaml_block = create_test_dbt_sources_yaml()
        dbt_sources = DbtSources.parse(yaml_block=yaml_block)
        dbt_source_table = dbt_sources.sources[0].tables[0]
        # Create a mock BigQuery table
        existing_labels = {"label1": "value1"}
        bq_table = create_test_table(labels=existing_labels)
        replaced_bq_table = replace_bq_table_metadata(
            table=bq_table, dbt_source_table=dbt_source_table)
        # Test schema
        self.assertEqual(replaced_bq_table.schema[0].description, dbt_source_table.columns[0].description)
        self.assertEqual(replaced_bq_table.schema[1].fields[0].description,
                         dbt_source_table.columns[1].description)
        self.assertEqual(replaced_bq_table.schema[1].fields[1].description,
                         dbt_source_table.columns[2].description)
        # Test labels
        self.assertDictEqual(bq_table.labels, existing_labels)
        expected = {'contains_pii': 'false', 'label1': None, 'owner': 'dummy owner'}
        self.assertDictEqual(replaced_bq_table.labels, expected)

    def test_merge_bigquery_labels(self):
        old_labels = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        new_labels = {
            "key1": "value1",
            "key3": "value3-new",
            "key4": "value4",
        }
        merged_labels = merge_bigquery_labels(
            base_labels=old_labels, new_labels=new_labels)
        expected = {
            'key1': 'value1',
            'key2': None,
            'key3': 'value3-new',
            'key4': 'value4',
        }
        self.assertDictEqual(merged_labels, expected)

    def test_get_updated_dataset_fields(self):
        # description and labels are empty
        dataset = create_test_dataset(description=None, labels={})
        fields = get_updated_dataset_fields(dataset)
        self.assertEqual(fields, [])
        # description exists
        dataset = create_test_dataset(description="test description", labels={})
        fields = get_updated_dataset_fields(dataset)
        self.assertEqual(fields, ["description"])
        # labels exist
        dataset = create_test_dataset(description=None, labels={"x": "a"})
        fields = get_updated_dataset_fields(dataset)
        self.assertEqual(fields, ["labels"])
        # description and labels exist
        dataset = create_test_dataset(description="test description", labels={"x": "a"})
        fields = get_updated_dataset_fields(dataset)
        self.assertEqual(fields, ['description', "labels"])

    def test_get_updated_table_fields(self):
        # without labels
        table = create_test_table()
        fields = get_updated_table_fields(table)
        expected = ['description', 'schema']
        self.assertEqual(fields, expected)
        # with labels
        table = create_test_table(labels={"key": "value"})
        fields = get_updated_table_fields(table)
        expected = ['description', 'labels', 'schema']
        self.assertEqual(fields, expected)
