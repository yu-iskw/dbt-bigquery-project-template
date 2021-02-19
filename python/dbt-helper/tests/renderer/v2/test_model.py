# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import unittest

import yaml

from dbt_helper.renderer.v2.model import _render_model_sql, _render_schema_yaml, _render_doc_md


class TestCliModel(unittest.TestCase):

    def test__render_model_sql(self):
        labels = {
            "key1": "value1",
            "key2": "value2",
        }
        tags = ["tag1", "tag2", "tag3"]
        rendered_sql = _render_model_sql(
            materialization="table",
            project_alias="dummy_project",
            dataset="dummy_dataset",
            table="dummy_table",
            owner="dummy_owner",
            labels=labels,
            tags=tags,
        )
        self.assertTrue("dummy_project" in rendered_sql)
        self.assertTrue("dummy_dataset" in rendered_sql)
        self.assertTrue("dummy_table" in rendered_sql)
        self.assertTrue("dummy_owner" in rendered_sql)
        for k, v in labels.items():
            self.assertTrue(k in rendered_sql)
            self.assertTrue(v in rendered_sql)
        for t in tags:
            self.assertTrue(t in rendered_sql)

    def test__render_schema_yaml(self):
        rendered_schema = _render_schema_yaml(
            project_alias="dummy_project",
            dataset="dummy_dataset",
            table="dummy_table",
        )
        self.assertTrue("dummy_project" in rendered_schema)
        self.assertTrue("dummy_dataset" in rendered_schema)
        self.assertTrue("dummy_table" in rendered_schema)

        # Test as YAML
        rendered_schema_dict = yaml.safe_load(rendered_schema)
        self.assertEqual(rendered_schema_dict["models"][0]["name"],
                         "dummy_project__dummy_dataset__dummy_table")

    def test__render_doc_md(self):
        rendered_doc = _render_doc_md(
            project_alias="dummy_project",
            dataset="dummy_dataset",
            table="dummy_table",
        )
        self.assertTrue("dummy_project" in rendered_doc)
        self.assertTrue("dummy_dataset" in rendered_doc)
        self.assertTrue("dummy_table" in rendered_doc)
