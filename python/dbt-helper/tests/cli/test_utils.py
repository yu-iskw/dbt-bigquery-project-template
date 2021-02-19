# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import unittest

import click
from click.testing import CliRunner

from dbt_helper.cli import utils as cli_utils


@click.command()
@click.option('--owner', callback=cli_utils.validate_owner_callback, type=str, required=True)
def test_command(owner):
    click.echo(owner)


class TestCliUtils(unittest.TestCase):

    def test_validate_label_value(self):
        runner = CliRunner()

        valid_input = "data_science_team"
        result = runner.invoke(test_command, ["--owner", valid_input])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "{}\n".format(valid_input))

        invalid_value = "data science  team"
        expected = 'A label value contains spaces. It can be data_science_team'
        result = runner.invoke(test_command, ["--owner", invalid_value])
        self.assertTrue(result.exit_code != 0)
        self.assertTrue(expected in result.output)

    def test___validate_owner(self):
        valid_input = "data_science_team"
        (is_valid, _) = cli_utils.validate_label_value(valid_input)
        self.assertTrue(is_valid)

        invalid_value = "data science  team"
        (is_valid, _) = cli_utils.validate_label_value(invalid_value)
        self.assertFalse(is_valid)
