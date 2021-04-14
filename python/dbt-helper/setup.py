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

#!/usr/bin/env python

import os
import sys

import dbt_helper
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def parse_requirements(path: str):
    """Parse requirements.txt

    Args:
        path (str): path to requirements.txt

    Returns:
        list: a list of python modules
    """
    with open(path, "r") as fp:
        return [line.strip() for line in fp.readlines()]


# Please maintain `./requirements/requirements.txt` directly.
requirements_path = os.path.join(
    os.path.dirname(__file__), "requirements", "requirements.txt")
setup(
    name='dbt-helper',
    version=dbt_helper.VERSION,
    packages=find_packages(),
    install_requires=parse_requirements(requirements_path),
    entry_points={
        "console_scripts": [
            "dbt-helper = dbt_helper.cli.main:cli",
        ],
    },
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
