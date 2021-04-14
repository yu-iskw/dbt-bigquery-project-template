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


import os
import unittest

import ruamel

from dbt_helper.utils import (
    get_module_root,
    get_templates_path,
    get_table_dir,
    normalize_gcp_project,
    parse_labels,
    find_yaml_files,
    extract_diff,
    strip_date_suffix,
    load_yaml,
    load_json,
    is_sharded_identifier,
    get_ruamel_yaml,
)


class TestUtils(unittest.TestCase):

    def test_get_templates_path(self):
        templates_path = get_templates_path()
        self.assertTrue(os.path.isdir(templates_path))

    def test_normalize_project(self):
        result = normalize_gcp_project("abc-def-123")
        expected = "abc_def_123"
        self.assertEqual(result, expected)

    def test_get_model_dir(self):
        model_dir = "test_models"
        project = "test_project"
        dataset = "test_dataset"
        table = "test_table"
        result = get_table_dir(models_dir=model_dir,
                               project=project,
                               dataset=dataset,
                               table=table)
        expected = "test_models/test_project/test_dataset/test_table"
        self.assertEqual(result, expected)

    def test_parse_labels(self):
        labels = ["k1=v1", "k2=v2", "k3 = v3"]
        result = parse_labels(labels=labels)
        expected = {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
        self.assertDictEqual(result, expected)

        result = parse_labels(labels=None)
        expected = {}
        self.assertDictEqual(result, expected)

    def test_find_yaml_files(self):
        path = os.path.join(get_module_root(), "tests")
        result = list(find_yaml_files(path))
        expected = 2
        self.assertEqual(len(result), expected)

    def test_extract_diff(self):
        x = "a\nb\nc\n\n"
        y = "a\nx\nc\nd"
        result = extract_diff(x, y)
        expected = ['- b', '+ x', '- \n', '+ d']
        expected = ['- b\n', '+ x\n', '- \n', '+ d']
        self.assertEqual(result, expected)

        result = extract_diff(x, y, as_str=True)
        expected = '- b\n\n+ x\n\n- \n\n+ d'
        self.assertEqual(result, expected)

    def test_strip_date_suffix(self):
        self.assertEqual(strip_date_suffix('test_table_1'),
                         'test_table_1')
        self.assertEqual(strip_date_suffix('test_table_20200101'),
                         'test_table_')
        self.assertEqual(strip_date_suffix('test_table_2020_01_01'),
                         'test_table_2020_01_01')

    def test_load_yaml(self):
        # Test loading a YAML file
        path = os.path.join(
            get_module_root(),"tests", "fixtures", "v2", "test_source_schema.yml")
        result = load_yaml(path)
        self.assertTrue(isinstance(result, dict))
        # Test invalid string
        path = os.path.join(
            get_module_root(),"tests", "fixtures", "dummy.txt")
        with self.assertRaises(ValueError):
            result = load_yaml(path)

    def test_load_json(self):
        # Test loading a JSON file
        path = os.path.join(
            get_module_root(),"tests", "fixtures", "artifacts", "manifest", "test_manifest_v1.json")
        result = load_json(path)
        self.assertTrue(isinstance(result, dict))
        # Test invalid string
        path = os.path.join(
            get_module_root(),"tests", "fixtures", "dummy.txt")
        with self.assertRaises(ValueError):
            result = load_json(path)

    def test_is_sharded_identifier(self):
        self.assertFalse(is_sharded_identifier("regular_table"))
        self.assertFalse(is_sharded_identifier("regular_table_"))
        self.assertFalse(is_sharded_identifier("regular_table_01"))
        self.assertTrue(is_sharded_identifier("regular_table_*"))

    def test_get_ruamel_yaml(self):
        ruamel_yaml = get_ruamel_yaml()
        self.assertTrue(isinstance(ruamel_yaml, ruamel.yaml.main.YAML))
