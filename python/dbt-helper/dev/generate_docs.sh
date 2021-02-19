#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
MODULE_DIR="$(dirname "$SCRIPT_DIR")"

pdoc3 --html --force "${MODULE_DIR}/dbt_helper"
