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

import dbt_helper
from dbt_helper.utils import get_module_root
from dbt_helper.renderer.v2.analysis import _render_analysis_yaml, _render_analysis_sql, get_analysis_name


class TestAnalysisRender(unittest.TestCase):

    def test__render_analysis_sql(self):
        rendered_sql = _render_analysis_sql()
        self.assertTrue(dbt_helper.VERSION in rendered_sql)

    def test__render_analysis_sql_with_custom_templates_dir(self):
        rendered_sql = _render_analysis_sql(
            templates_base_dir=os.path.join(get_module_root(), "tests", "fixtures")
        )
        self.assertTrue("THIS_IS_MY_CUSTOM_TEMPLATE" in rendered_sql)
    
    def test__render_analysis_yaml(self):
        saved_path = "region/service/product/metric_01"
        analysis_name = get_analysis_name(saved_path=saved_path)
        owner = "Product team"
        rendered_yaml = _render_analysis_yaml(
            saved_path=saved_path,
            owner=owner,
        )
        self.assertTrue(analysis_name in rendered_yaml)
        self.assertTrue(owner in rendered_yaml)
        self.assertTrue(dbt_helper.VERSION in rendered_yaml)

    def test__render_analysis_yaml_with_custom_templates_dir(self):
        saved_path = "region/service/product/metric_01"
        owner = "Product team"
        rendered_yaml = _render_analysis_yaml(
            saved_path=saved_path,
            owner=owner,
            templates_base_dir=os.path.join(get_module_root(), "tests", "fixtures")
        )
        self.assertTrue("THIS_IS_MY_CUSTOM_TEMPLATE" in rendered_yaml)
