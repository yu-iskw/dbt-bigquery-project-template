#!/bin/bash
set -e

# The script check if YAML files of dbt sources contains expected values,
# such as owner information.
#
# NOTE:
# The environment variable 'GCLOUD_PROJECT' enables us to specify the GCP project
# for Google Cloud SDK. In the case of dbt-helper, it is used for a BigQuery client.
# SEE https://cloud.google.com/functions/docs/env-var
# For instance,
# GCLOUD_PROJECT="YOUR_PROJECT_ID" bash ci/sync_dbt_sources.sh

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Arguments
models_dir=${1:-"${PROJECT_DIR}/models"}
vars_path=${2:-"${PROJECT_DIR}/config/prod/vars.yml"}

#
# functions
#
function is_dbt_source_schema() {
  # Check if a YAML file is a dbt source.
  yaml_content=${1:?}
  result="$(echo "$yaml_content" | yq -M 'select(.sources != null)')"
  if [[ -z $result ]]; then
    echo 0
  else
    echo 1
  fi
}

#
# main
#

# Get paths to dbt source YAML files.
yaml_files=$(find "$models_dir" -iname '*.yml')

# Synchronize dbt sources
for yaml_file in $yaml_files; do
  # Skip non dbt source schema file.
  yaml_content="$(cat "$yaml_file")"
  if [[ $(is_dbt_source_schema "$yaml_content") -eq 0 ]]; then
    continue
  fi

  # Synchronize a dbt source with BigQuery
  echo "Synchronize ${yaml_file}"
  dbt-helper source update-dbt-source \
    --models_dir "$models_dir" \
    --vars_path "$vars_path" \
    --source_path "$yaml_file"
done