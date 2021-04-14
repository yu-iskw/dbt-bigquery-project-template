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

import unittest

import yaml

from dbt_helper.renderer.v2.source import _render_source_yaml_for_bq_table, get_source_yaml_file_name


class TestSource(unittest.TestCase):

    def test_get_source_yaml_file_name(self):
        result = get_source_yaml_file_name(
            project_alias="test_project", dataset="test_dataset", table="test_table")
        expected = "src_test_project__test_dataset__test_table.yml"
        self.assertEqual(result, expected)

    def test__render_source_yaml(self):
        project = "dummy-project-prod"
        project_alias = "dummy-project"
        dataset = "dummy_dataset"
        table = "dummy_table"
        labels = {
            "key1": "value1",
            "key2": "value2",
        }
        tags = ["tag1", "tag2", "tag3"]
        columns = [
            {"name": "id"},
            {"name": "name", "description": "name"},
        ]
        rendered_source = _render_source_yaml_for_bq_table(
            project=project,
            project_alias=project_alias,
            dataset=dataset,
            table=table,
            columns=columns,
            labels=labels,
            tags=tags,
        )
        self.assertTrue(project_alias in rendered_source)
        self.assertTrue(dataset in rendered_source)
        self.assertTrue(table in rendered_source)
        for k, v in labels.items():
            self.assertTrue(k in rendered_source)
            self.assertTrue(v in rendered_source)
        for t in tags:
            self.assertTrue(t in rendered_source)

        # Tests with YAML
        rendered_source_dict = yaml.safe_load(rendered_source)
        self.assertEqual(rendered_source_dict["sources"][0]["name"], dataset)
        self.assertEqual(
            rendered_source_dict["sources"][0]["database"],
            "{{ var('projects')['dummy-project'] }}")
        self.assertEqual(
            rendered_source_dict["sources"][0]["tables"][0]["name"],
            "dummy_project__dummy_dataset__dummy_table")
        self.assertEqual(
            rendered_source_dict["sources"][0]["tables"][0]["identifier"],
            "dummy_table")
        self.assertEqual(
            rendered_source_dict["sources"][0]["tables"][0]["tags"],
            tags)
        self.assertDictEqual(
            rendered_source_dict["sources"][0]["tables"][0]["meta"],
            labels)
        # Test columns
        self.assertEqual(
            rendered_source_dict["sources"][0]["tables"][0]["columns"][0]["name"],
            "id")
        self.assertEqual(
            rendered_source_dict["sources"][0]["tables"][0]["columns"][0]["description"],
            "")
        self.assertEqual(
            rendered_source_dict["sources"][0]["tables"][0]["columns"][1]["name"],
            "name")
        self.assertEqual(
            rendered_source_dict["sources"][0]["tables"][0]["columns"][1]["description"],
            "name")
