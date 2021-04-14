#!/bin/bash
set -e

# The script validates YAML files.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

shell_scripts=$(find "${PROJECT_DIR}/ci" -iname "*.sh")

for shell_script in $shell_scripts; do
  shfmt -l -w -i 2 "$shell_script"
done
