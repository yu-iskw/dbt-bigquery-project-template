# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import unittest

from google.cloud import bigquery

from dbt_helper.parser.bigquery import (
    SchemaInfo,
    parse_schema_field,
    parse_scalar_schema_field,
    extract_schema_info
)

scalar_schema_field = bigquery.SchemaField(
    "user_id", "STRING", mode="NULLABLE", description="user ID")

array_schema_field = bigquery.SchemaField(
    "addresses",
    "RECORD",
    mode="REPEATED",
    fields=[
        bigquery.SchemaField("status", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("state", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("zip", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("numberOfYears", "STRING", mode="NULLABLE"),
    ],
)

struct_schema_field = bigquery.SchemaField(
    "user",
    "STRUCT",
    fields=[
        scalar_schema_field,
        array_schema_field,
    ],
)


class TestBigQuery(unittest.TestCase):

    def test_extract_schema_info(self):
        inputs = [scalar_schema_field, array_schema_field, struct_schema_field]
        results = extract_schema_info(inputs)
        expected = [
            SchemaInfo(name='user_id', description='user ID'),
            SchemaInfo(name='addresses.status', description=None),
            SchemaInfo(name='addresses.address', description=None),
            SchemaInfo(name='addresses.city', description=None),
            SchemaInfo(name='addresses.state', description=None),
            SchemaInfo(name='addresses.zip', description=None),
            SchemaInfo(name='addresses.numberOfYears', description=None),
            SchemaInfo(name='user.user_id', description='user ID'),
            SchemaInfo(name='user.addresses.status', description=None),
            SchemaInfo(name='user.addresses.address', description=None),
            SchemaInfo(name='user.addresses.city', description=None),
            SchemaInfo(name='user.addresses.state', description=None),
            SchemaInfo(name='user.addresses.zip', description=None),
            SchemaInfo(name='user.addresses.numberOfYears', description=None)
        ]
        self.assertEqual(results, expected)

    def test_parse_scalar_schema_field(self):
        result = parse_scalar_schema_field(
            schema_field=scalar_schema_field,
            parent_field_names=["parent1", "parent2"])
        expected = SchemaInfo(name='parent1.parent2.user_id', description='user ID')
        self.assertEqual(result, expected)

    def test_parse_schema_with_array(self):
        result = parse_schema_field(
            schema_field=array_schema_field, parent_field_names=[])
        expected = [
            SchemaInfo(name='addresses.status'),
            SchemaInfo(name='addresses.address'),
            SchemaInfo(name='addresses.city'),
            SchemaInfo(name='addresses.state'),
            SchemaInfo(name='addresses.zip'),
            SchemaInfo(name='addresses.numberOfYears'),
        ]
        self.assertEqual(result, expected)

    def test_parse_schema_with_struct(self):
        result = parse_schema_field(
            schema_field=struct_schema_field, parent_field_names=[])
        expected = [
            SchemaInfo(name="user.user_id", description="user ID"),
            SchemaInfo(name='user.addresses.status'),
            SchemaInfo(name='user.addresses.address'),
            SchemaInfo(name='user.addresses.city'),
            SchemaInfo(name='user.addresses.state'),
            SchemaInfo(name='user.addresses.zip'),
            SchemaInfo(name='user.addresses.numberOfYears'),
        ]
        self.assertEqual(result, expected)
