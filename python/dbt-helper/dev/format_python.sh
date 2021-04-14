#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
MODULE_ROOT="$(dirname "$SCRIPT_DIR")"

yapf --recursive --parallel --in-place "${MODULE_ROOT}/dbt_helper"