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

from dataclasses import dataclass
from typing import List, Optional

from google.cloud import bigquery


@dataclass
class SchemaInfo:
    """The class is used to manage information of a column."""
    name: str
    description: str = None


def extract_schema_info(schema: List[bigquery.SchemaField]) -> List[SchemaInfo]:
    """Extract table information

    Args:
        schema: Squence of :class:`~google.cloud.bigquery.schema.SchemaField`

    Returns:
        List[SchemaInfo]: A flattened list of schema field information
    """
    table_info = []
    for schema_field in schema:
        schema_field_info = parse_schema_field(schema_field=schema_field)
        table_info.extend(schema_field_info)
    return table_info


def parse_schema_field(
        schema_field: bigquery.SchemaField,
        parent_field_names: Optional[List[str]] = None) -> List[SchemaInfo]:
    """Parse BigQuery SchemaField

    Args:
        schema_field (google.cloud.bigquery.SchemaField): schema field
        parent_field_names (list): A list of parent field names.

    Returns:
        list: A flattened list of schema field information
    """
    if parent_field_names is None:
        parent_field_names = []

    schema_info = []

    if schema_field.field_type.upper() in ["STRUCT", "RECORD"]:
        for child_schema_field in schema_field.fields:
            next_parent_field_names = parent_field_names.copy()
            next_parent_field_names.append(schema_field.name)
            sub_schema_info = parse_schema_field(
                child_schema_field, parent_field_names=next_parent_field_names)
            schema_info.extend(sub_schema_info)
    else:
        scalar_schema_info = parse_scalar_schema_field(
            schema_field=schema_field, parent_field_names=parent_field_names)
        schema_info.append(scalar_schema_info)
    return schema_info


def parse_scalar_schema_field(
        schema_field: bigquery.SchemaField,
        parent_field_names: Optional[List[str]] = None) -> SchemaInfo:
    """Parse a scalar schema field

    Args:
        schema_field (google.cloud.bigquery.SchemaField): schema field
        parent_field_names (list): A list of parent field names

    Returns:
        dict: parsed schema information
    """
    if parent_field_names is None:
        parent_field_names = []

    full_field_names = parent_field_names.copy()
    full_field_names.append(schema_field.name)
    full_field_name = ".".join(full_field_names)
    schema_info = SchemaInfo(
        name=full_field_name, description=schema_field.description)
    return schema_info
