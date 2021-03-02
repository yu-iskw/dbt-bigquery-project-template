# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Config:
    """This is a class to parse `.disabled[].config` in manifest.json."""
    enabled: bool
    materialized: str

    @classmethod
    def parse(cls, json_block: dict):
        return Config(
            enabled=json_block.get("enabled"),
            materialized=json_block.get("materialized"),
        )


@dataclass
class Disabled:
    """This is a class to parse `.disabled[]` in manifest.json."""
    root_path: str
    path: str
    original_file_path: str

    package_name: str
    unique_id: str
    resource_type: str
    database: str
    schema: str
    alias: str
    name: str
    fqn: List[str]

    config: Optional[Config]

    @classmethod
    def parse(cls, json_block: dict):
        return Disabled(
            package_name=json_block.get("package_name"),
            root_path=json_block.get("root_path"),
            path=json_block.get("path"),
            original_file_path=json_block.get("original_file_path"),
            unique_id=json_block.get("unique_id"),
            resource_type=json_block.get("resource_type"),
            database=json_block.get("database"),
            schema=json_block.get("schema"),
            alias=json_block.get("alias"),
            name=json_block.get("name"),
            fqn=json_block.get("fqn", []),
            config=(Config.parse(json_block["config"]) if "config" in json_block else None),
        )


@dataclass
class ManifestV1:
    """This is a class to parse manifest.json v1.

    The json schema of manifest v1 is at:
    https://schemas.getdbt.com/dbt/manifest/v1.json
    """
    # metadata
    dbt_version: str
    dbt_schema_version: str
    generated_at: str
    adapter_type: str
    env: Dict[str, str]
    # disabled models
    disabled: List[Disabled]

    @classmethod
    def parse(cls, json_block: dict):
        return ManifestV1(
            dbt_version=json_block.get("dbt_version"),
            dbt_schema_version=json_block.get("dbt_schema_version"),
            generated_at=json_block.get("generated_at"),
            adapter_type=json_block.get("adapter_type"),
            env=json_block.get("env", {}),
            disabled=[Disabled.parse(sub) for sub in json_block.get("disabled", [])],
        )
