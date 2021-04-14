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

import click
from dbt_helper.cli.utils import validate_owner_callback
from dbt_helper.renderer.v2.analysis import generate_analysis

from dbt_helper.utils import DEFAULT_DBT_CONFIG_VERSION


# pylint: disable=W0613
@click.group()
@click.pass_context
def analysis(context):
    """sub commands for dbt analysis"""


# pylint: disable=W0613
@analysis.command()
@click.option("--analysis_dir", type=click.Path(exists=True), required=True,
              help="path to the dbt analysis dir")
@click.option("--path", type=str, required=True, help="relative path to a dbt analysis from the analysis directory")
@click.option("--owner", type=str, help="owner name", default="", callback=validate_owner_callback)
@click.option("--version", type=str, help="dbt config version", default=DEFAULT_DBT_CONFIG_VERSION)
@click.option("--overwrite", is_flag=True, help="flag to overwrite")
@click.pass_context
def scaffold(
        context,
        analysis_dir,
        path,
        owner,
        version,
        overwrite):
    """Generate scaffold files of a dbt model with template files."""
    saved_path = generate_analysis(
        analysis_dir=analysis_dir,
        path_to_analysis=path,
        owner=owner,
        version=version,
        overwrite=overwrite,
    )

    # Show information on stdout
    click.echo("Scaffold files are generated under {}".format(saved_path))
