#!/bin/bash
set -e

# Constants
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
MODULE_DIR="$(dirname "$SCRIPT_DIR")"

# Use pip3 as priority if exists.
if type "pip3" > /dev/null 2>&1; then
  PIP="pip3"
else
  PIP="pip"
fi

# Install required modules.
$PIP install --no-cache-dir --force-reinstall -r "${MODULE_DIR}/requirements/requirements-dev.txt"