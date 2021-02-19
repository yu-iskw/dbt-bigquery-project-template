# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import unittest
import yaml

import dbt_helper
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
