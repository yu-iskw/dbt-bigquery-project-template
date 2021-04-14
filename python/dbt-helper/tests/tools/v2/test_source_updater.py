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
import unittest
import tempfile

from google.cloud import bigquery

from dbt_helper.utils import get_module_root
from dbt_helper.tools.v2.source_updater import SourceTableUpdaterV2


def create_test_table():
    """Create an updating table."""
    schema = [
        bigquery.SchemaField("id", "INTEGER", description="user ID"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", description="updated timestamp"),
        bigquery.SchemaField("created_at", "TIMESTAMP", description="created timestamp"),
    ]
    table = bigquery.Table("test-project.test_dataset.test_table", schema=schema)
    table.description = "updated description"
    table.labels = {
        "x": "a",
        "y": "bb",
        "z": "c",
        "w": "d",
    }
    return table


class TestSourceUpdatorV2(unittest.TestCase):

    def setUp(self) -> None:
        path = os.path.join(get_module_root(),
                            "tests", "fixtures", "v2", "test_source_schema.yml")
        self.source_yaml = SourceTableUpdaterV2.load(path)

    def test_load_succeeded(self):
        self.assertEqual(self.source_yaml.data["sources"][0]["name"], "test_name")

    def test_table_description(self):
        description = "updated description"
        self.source_yaml.table_description = description
        self.assertEqual(self.source_yaml.table_description, description)

    def test_table_labels(self):
        labels = {"a": "x", "b": "y"}
        self.source_yaml.table_labels = labels
        self.assertDictEqual(self.source_yaml.table_labels, labels)

    def test_update_column(self):
        updating_table = create_test_table()
        result = self.source_yaml.update_columns(updating_table.schema)
        updated_table = SourceTableUpdaterV2.loads(result.data)
        self.assertEqual(
            updated_table.columns[0]["description"],
            updating_table.schema[0].description)
        self.assertTrue("updated" not in [c["name"] for c in updated_table.columns])
        self.assertTrue("updated_at" in [c["name"] for c in updated_table.columns])
        self.assertTrue("created_at" in [c["name"] for c in updated_table.columns])

    def test_update_with_bq_table(self):
        updating_table = create_test_table()
        result = self.source_yaml.update_with_bq_table(updating_table)
        updated_table = SourceTableUpdaterV2.loads(result.data)
        # Test table
        self.assertEqual(updated_table.table_description, "updated description")
        # Test column
        self.assertEqual(
            updated_table.columns[0]["description"],
            updating_table.schema[0].description)
        # 'updated' is removedA.
        self.assertTrue("updated" not in [c["name"] for c in updated_table.columns])
        # 'updated_at' and 'created_at' are added.
        self.assertTrue("updated_at" in [c["name"] for c in updated_table.columns])
        self.assertTrue("created_at" in [c["name"] for c in updated_table.columns])

    def test_dump(self):
        # Update the table.
        updating_table = create_test_table()
        result = self.source_yaml.update_with_bq_table(updating_table)
        updated_table = SourceTableUpdaterV2.loads(result.data)
        # Dump the table to a YAML file.
        _, temp_file = tempfile.mkstemp()
        updated_table.dump(temp_file)
        # Load the dumped YAML file.
        loaded = SourceTableUpdaterV2.load(temp_file)
        self.assertEqual(loaded.table_description, "updated description")
