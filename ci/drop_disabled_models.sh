#!/bin/bash
set -e

# The script is used to drop disabled dbt models on BigQuery.
#
# NOTE
# When 'dbt docs generate' is executed, 'manifest.json' should be created.

# Constants
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Arguments
dry_run="${1:-1}"
manifest_json_path="${2:-"${PROJECT_DIR}/target/manifest.json"}"
schema_version="${3:-"v1"}"
client_project="${4:-""}"

# Drop disabled models
# shellcheck disable=SC2046
dbt-helper model drop-disabled-models \
  --manifest "$manifest_json_path" \
  --schema_version "$schema_version"  \
  --resource_types "model" \
  --resource_types "snapshot" \
  --client_project "${client_project}" \
  --delete_empty_dataset \
  $([[ $dry_run -eq 1 ]] && echo "--dry_run")
