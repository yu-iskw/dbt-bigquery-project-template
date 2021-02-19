#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
MODULE_DIR="$(dirname "$SCRIPT_DIR")"

pylint -v "${MODULE_DIR}"/dbt_helper "${MODULE_DIR}"/tests
