#!/bin/bash
set -e

# Constants
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
MODULE_DIR="$(dirname "$SCRIPT_DIR")"

pytest -v -s --cache-clear "${MODULE_DIR}/tests"
