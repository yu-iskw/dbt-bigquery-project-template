# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from typing import List, Dict, Any, Union

import dictdiffer

from google.cloud import bigquery

from dbt_helper.parser.bigquery import SchemaInfo, extract_schema_info
from dbt_helper.utils import DEFAULT_DBT_CONFIG_VERSION, extract_diff


@dataclass
class DbtSourceTableColumn:
    """The class is used for `sources[].tables[].columns`."""
    name: str
    description: str = None
    meta: Dict[str, Any] = None
    tests: Union[str, Any] = None
    tags: List[str] = None

    @classmethod
    def parse(cls, yaml_block):
        """Parse a YAML block as `sources[].tables[].columns`

        Args:
            yaml_block (dict): YAML block

        Returns:
            :class:`DbtSourceTableColumn`:
        """
        dbt_source_table_column = DbtSourceTableColumn(
            name=yaml_block["name"],
            description=yaml_block.get("description", None),
            meta=yaml_block.get("meta", {}),
            tests=yaml_block.get("tests", []),
            tags=yaml_block.get("tags", []),
        )
        return dbt_source_table_column

    def compare(self, schema_info: SchemaInfo):
        if self.name != schema_info.name:
            raise ValueError("Given schema field is wrong: ({}, {})".format(self.name, schema_info.name))
        reasons = {}
        if self.description != schema_info.description:
            key = "description of column {} is different".format(self.name)
            diff = extract_diff(self.description, schema_info.description, as_str=True)
            reasons[key] = diff
        return reasons


@dataclass
class DbtSourceTable:
    """The class is used for `sources[].tables`."""
    name: str
    description: str = None
    meta: Dict[str, Any] = None
    identifier: str = None
    loaded_at_field: str = None
    tests: List[Union[str, Any]] = None
    tags: List[str] = None
    columns: List[DbtSourceTableColumn] = None

    @classmethod
    def parse(cls, yaml_block):
        """Parse a YAML block as `sources[].tables[]`

        Args:
            yaml_block (dict): YAML block

        Returns:
            :class:`DbtSourceTable`:
        """
        dbt_source_table = DbtSourceTable(
            name=yaml_block["name"],
            description=yaml_block.get("description", None),
            identifier=yaml_block.get("identifier", None),
            loaded_at_field=yaml_block.get("loaded_at_field", None),
            meta=yaml_block.get("meta", {}),
            tags=yaml_block.get("tags", []),
            tests=yaml_block.get("tests", []),
            columns=[DbtSourceTableColumn.parse(sub_yaml_block)
                     for sub_yaml_block in yaml_block.get("columns", [])],
        )
        return dbt_source_table

    def compare(self, bq_table: bigquery.Table):
        """Compare to a BigQuery table.

        Args:
            bq_table (bigquery.Table): A BigQuery table

        Returns:
            dict: a dictionary contains different reasons
        """
        reasons = {}
        # description
        if self.description != bq_table.description:
            diff = extract_diff(self.description, bq_table.description)
            reasons["table description"] = "\n".join(diff)
        # labels
        diff = list(dictdiffer.diff(self.meta, bq_table.labels))
        num_diff_tags = len(diff)
        if num_diff_tags > 0:
            reasons["table labels"] = str(diff)
        bq_schema_info = extract_schema_info(bq_table.schema)

        # Loop over columns of dbt source schema
        for c in self.columns:
            target_schema_info = [s for s in bq_schema_info if c.name == s.name]
            if len(target_schema_info) == 0:
                reasons["not found column {}".format(c.name)] = "not found column {}".format(c.name)
            else:
                sub_reasons = c.compare(target_schema_info[0])
                reasons.update(sub_reasons)
        return reasons


@dataclass
class DbtSource:
    """The class is used for a dbt source schema."""
    name: str
    description: str = None
    database: str = None
    schema: str = None
    loader: str = None
    loaded_at_field: str = None
    meta: Dict[str, Any] = None
    tags: List[str] = None
    overrides: str = None
    freshness: Dict[str, Any] = None
    quoting: Dict[str, Any] = None
    tables: List[DbtSourceTable] = None

    @classmethod
    def parse(cls, yaml_block):
        """Parse a YAML block as a dbt source schema

        Args:
            yaml_block (dict): YAML block

        Returns:
            :class:`DbtSource`:
        """
        dbt_source = DbtSource(
            name=yaml_block.get("name", None),
            description=yaml_block.get("description", None),
            database=yaml_block.get("database", None),
            loader=yaml_block.get("loader", None),
            schema=yaml_block.get("schema", None),
            meta=yaml_block.get("meta", {}),
            tags=yaml_block.get("tags", []),
            tables=[DbtSourceTable.parse(sub_yaml_block)
                    for sub_yaml_block in yaml_block.get("tables", [])],
        )
        return dbt_source

    def has_tables(self):
        """Check if tables exist or not"""
        return isinstance(self.tables, list) and len(self.tables) > 0

    # def compare(self, bq_table: bigquery.Table):
    #     reasons = {}
    #     gcp_project_id = self.database
    #     dataset_id = self.schema
    #     for t in self.tables:
    #         table_id = t.name
    #         bq_table = get_bigquery_table(
    #             project=gcp_project_id, dataset_id=dataset_id, table_id=table_id)
    #         _reasons = t.compare(bq_table=bq_table)
    #         reasons.update(reasons)
    #     return reasons


@dataclass
class DbtSources:
    sources: List[DbtSource]
    config_version: int = None

    @classmethod
    def parse(cls, yaml_block: dict):
        """Map a dict to a DbtSources class

        Args:
            yaml_block (dict): dict for dbt source YAML

        Returns:
            'DbtSources': a mapped DbtSources class
        """
        # Check if the 'sources' property exists or not.
        if "sources" not in yaml_block.keys():
            raise ValueError("it doesn't have the 'sources' property.")

        dbt_sources = DbtSources(
            config_version=yaml_block.get("version", DEFAULT_DBT_CONFIG_VERSION),
            sources=[DbtSource.parse(x) for x in yaml_block.get("sources", [])],
        )
        return dbt_sources

    def has_tables(self):
        """Check if tables exist or not"""
        return any(s.has_tables() for s in self.sources)
