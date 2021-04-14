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
import click_completion

import dbt_helper
from .model import model
from .source import source
from .completion import completion
from .analysis import analysis
from .snapshot import snapshot

# Initialize click-completion
click_completion.init()


# pylint: disable=W0613
@click.group()
@click.pass_context
@click.version_option(version=dbt_helper.VERSION)
def cli(context):
    """CLI body

    Args:
        context: click context
    """
    if context.invoked_subcommand is None:
        print(context.get_help())
    else:
        print('gonna invoke %s' % context.invoked_subcommand)


# Add sub commands
cli.add_command(model)
cli.add_command(source)
cli.add_command(analysis)
cli.add_command(snapshot)
cli.add_command(completion)
