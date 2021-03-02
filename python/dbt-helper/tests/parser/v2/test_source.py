# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import unittest

from google.cloud.bigquery import SchemaField, Table

from dbt_helper.parser.v2 import source
from dbt_helper.utils import (
    get_module_root,
    load_yaml,
)


def create_correct_bq_table():
    """Create a correct table"""
    schema = [
        SchemaField("id", "INTEGER", description="ID"),
        SchemaField("updated", "TIMESTAMP", description="updated timestamp"),
    ]
    table = Table("test-project.test_dataset.test_table", schema=schema)
    table.description = "test_description"
    table.labels = {"a": "x", "b": "y", "c": "z"}
    return table


def create_wrong_bq_table():
    """Create a wrong table"""
    table = Table("test-project.test_dataset.test_table")
    table.labels = {"x": "a"}
    return table


class TestDbtUtils(unittest.TestCase):

    def setUp(self):
        # Load the testing source schema YAML.
        path = os.path.join(get_module_root(),
                            "tests",
                            "fixtures",
                            "v2",
                            "test_source_schema.yml")
        self.yaml_block = load_yaml(path)["sources"][0]

    def test_parse(self):
        result = source.DbtSource.parse(self.yaml_block)

        # DbtSource
        self.assertEqual(result.name, "test_name")
        self.assertEqual(result.description, "test_description")
        self.assertEqual(result.database, "test-project")
        self.assertEqual(result.schema, "test_schema")
        self.assertEqual(result.loader, "test_loader")
        self.assertDictEqual(result.meta, {'x': 'a', 'y': 'b', 'z': 'c'})
        self.assertEqual(len(result.tables), 1)

        # DbtSourceTable
        table = result.tables[0]
        self.assertEqual(table.name, "test_table")
        self.assertEqual(table.description, "test_description")
        self.assertEqual(table.identifier, "test_table_alias")
        self.assertDictEqual(table.meta, {'a': 'x', 'b': 'y', 'c': 'z'})
        self.assertEqual(table.tags, ['tag1', 'tag2', 'tag3'])
        self.assertEqual(len(table.columns), 2)

        # DbtSourceTableColmun
        column_1 = table.columns[0]
        self.assertEqual(column_1.name, "id")
        self.assertEqual(column_1.description, "ID")
        self.assertDictEqual(column_1.meta, {'contains_pii': 'true'})
        self.assertEqual(column_1.tags, ['tag1', 'tag2'])
        self.assertEqual(column_1.tests, ['unique', 'not_null'])
        column_2 = table.columns[1]
        self.assertEqual(column_2.name, "updated")
        self.assertEqual(column_2.description, "updated timestamp")

    def test_parse_invalid_values(self):
        # Test with an empty dict.
        yaml_block = {}
        with self.assertRaises(ValueError):
            source.DbtSources.parse(yaml_block)
        # Test with a dbt model schema YAML
        path = os.path.join(get_module_root(), "tests", "fixtures", "v2", "test_model_schema.yml")
        yaml_block = load_yaml(path)
        with self.assertRaises(ValueError):
            source.DbtSources.parse(yaml_block)

    def test_table_compare(self):
        dbt_source = source.DbtSource.parse(self.yaml_block)
        parsed_table = dbt_source.tables[0]
        result = parsed_table.compare(create_correct_bq_table())
        self.assertDictEqual(result, {})

        result = parsed_table.compare(create_wrong_bq_table())
        expected = {
            'not found column id': 'not found column id',
            'not found column updated': 'not found column updated',
            'table description': '- test_description',
            'table labels': "[('add', '', [('x', 'a')]), ('remove', '', [('a', 'x'), ('b', 'y'), ('c', 'z')])]"
        }
        self.assertDictEqual(result, expected)

