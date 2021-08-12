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
import yaml

import dbt_helper
from dbt_helper.utils import get_module_root
from dbt_helper.renderer.v2.snapshots import (
    _render_snapshot_sql,
    _render_schema_yaml
)


class TestSnapshotRender(unittest.TestCase):

    def test__render_snapshot_sql(self):
        strategy = "check"
        project_alias = "test-project-01"
        dataset = "test_dataset"
        table = "test_snapshot_table"
        owner = "product_team"

        rendered_sql = _render_snapshot_sql(
            strategy=strategy,
            project_alias=project_alias,
            dataset=dataset,
            table=table,
            owner=owner,
        )
        self.assertTrue(strategy in rendered_sql)
        self.assertTrue(project_alias in rendered_sql)
        self.assertTrue(dataset in rendered_sql)
        self.assertTrue(table in rendered_sql)
        self.assertTrue(dbt_helper.VERSION in rendered_sql)
    
    def test__render_snapshot_sql_with_custom_templates_dir(self):
        strategy = "check"
        project_alias = "test-project-01"
        dataset = "test_dataset"
        table = "test_snapshot_table"
        owner = "product_team"

        rendered_sql = _render_snapshot_sql(
            strategy=strategy,
            project_alias=project_alias,
            dataset=dataset,
            table=table,
            owner=owner,
            templates_base_dir=os.path.join(get_module_root(), "tests", "fixtures")
        )
        self.assertTrue(strategy in rendered_sql)
        self.assertTrue(project_alias in rendered_sql)
        self.assertTrue(dataset in rendered_sql)
        self.assertTrue(table in rendered_sql)
        self.assertTrue(dbt_helper.VERSION in rendered_sql)
        
        self.assertTrue("THIS_IS_MY_CUSTOM_TEMPLATE" in rendered_sql)
    
    def test__render_schema_yaml(self):
        project_alias = "test-project-01"
        dataset = "test_dataset"
        table = "test_snapshot_table"
        owner = "product_team"
        rendered_yaml = _render_schema_yaml(
            project_alias=project_alias,
            dataset=dataset,
            table=table,
            owner=owner,
        )

        rendered_yaml_dict = yaml.safe_load(rendered_yaml)
        self.assertEqual(len(rendered_yaml_dict["snapshots"]), 1)
        self.assertEqual(rendered_yaml_dict["snapshots"][0]["name"],
                         "test_project_01__test_dataset__test_snapshot_table")
        self.assertTrue(len(rendered_yaml_dict["snapshots"][0]["description"]) > 0)
        self.assertEqual(len(rendered_yaml_dict["snapshots"][0]["columns"]), 1)

    def test__render_schema_yaml_with_custom_templates_dir(self):
        project_alias = "test-project-01"
        dataset = "test_dataset"
        table = "test_snapshot_table"
        owner = "product_team"
        rendered_yaml = _render_schema_yaml(
            project_alias=project_alias,
            dataset=dataset,
            table=table,
            owner=owner,
            templates_base_dir=os.path.join(get_module_root(), "tests", "fixtures"),
        )
        self.assertTrue("THIS_IS_MY_CUSTOM_TEMPLATE" in rendered_yaml)

        rendered_yaml_dict = yaml.safe_load(rendered_yaml)
        self.assertEqual(len(rendered_yaml_dict["snapshots"]), 1)
        self.assertEqual(rendered_yaml_dict["snapshots"][0]["name"],
                         "test_project_01__test_dataset__test_snapshot_table")
        self.assertTrue(len(rendered_yaml_dict["snapshots"][0]["description"]) > 0)
        self.assertEqual(len(rendered_yaml_dict["snapshots"][0]["columns"]), 1)