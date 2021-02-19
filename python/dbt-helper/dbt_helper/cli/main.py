# -*- coding: utf-8 -*-
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
