#!/bin/bash
set -e

# dbt generates `target/manifest.json` by executing `dbt docs generate`.
# The file contains information about dbt model.
# We can check metadata of dbt models, parsing the json file.
#
# NOTE: manifest.json doesn't contain information of dbt sources.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Arguments
manifest_json=${1:-"${PROJECT_DIR}/target/manifest.json"}

# Flag to manage failed or not
export FAILED=0

# Check config.owner in SQL file
selected_models="$(jq '.nodes as $nodes | select(.config.owner == null) | .nodes | keys' "$manifest_json")"
if [[ "$(echo "$selected_models" | wc -l)" -ne 0 ]]; then
  echo "The files don't contain \`config.owner\` in the SQL files."
  echo "$selected_models"
  export FAILED=1
fi

# Check meta.owner in schema.yml
selected_models="$(jq '.nodes as $nodes | select(.meta.owner == null) | .nodes | keys' "$manifest_json")"
if [[ "$(echo "$selected_models" | wc -l)" -ne 0 ]]; then
  echo "The files don't contain \`meta.owner\` in the schema files."
  echo "$selected_models"
  export FAILED=1
fi

# If any checker was failed, then exit 1.
if [[ $FAILED -eq 1 ]]; then
  echo "$0 was failed"
  exit 1
fi
