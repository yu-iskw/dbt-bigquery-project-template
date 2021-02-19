# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import unittest

import dbt_helper
from dbt_helper.renderer.v2.analysis import _render_analysis_yaml, _render_analysis_sql, get_analysis_name


class TestAnalysisRender(unittest.TestCase):

    def test__render_analysis_sql(self):
        rendered_sql = _render_analysis_sql()
        self.assertTrue(dbt_helper.VERSION in rendered_sql)

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

