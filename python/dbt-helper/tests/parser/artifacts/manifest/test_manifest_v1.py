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

from dbt_helper.parser.artifacts.manifest import manifest_v1
from dbt_helper.utils import (
    get_module_root,
    load_json,
)


class TestManifestV1(unittest.TestCase):

    def setUp(self):
        # Load the testing manifest.json.
        # The JSON file was generated using the jaffle_shop example.
        # SEE https://github.com/fishtown-analytics/jaffle_shop
        path = os.path.join(get_module_root(),
                            "tests",
                            "fixtures",
                            "artifacts",
                            "manifest",
                            "test_manifest_v1.json")
        self.json_block = load_json(path)

    def test_parse(self):
        result = manifest_v1.ManifestV1.parse(self.json_block)

        # ManifestJson
        self.assertEqual(len(result.disabled), 1)

        # Disabled
        disabled_model = result.disabled[0]
        self.assertEqual(disabled_model.package_name, "jaffle_shop")
        self.assertEqual(disabled_model.resource_type, "model")
        self.assertEqual(disabled_model.database, "test-gcp-project")
        self.assertEqual(disabled_model.schema, "test_dbt")
        self.assertEqual(disabled_model.name, "dim_customers")
        self.assertEqual(disabled_model.alias, "dim_customers")
        self.assertEqual(disabled_model.unique_id, "model.jaffle_shop.dim_customers")

        # Config
        config = disabled_model.config
        self.assertFalse(config.enabled)
        self.assertEqual(config.materialized, "table")
