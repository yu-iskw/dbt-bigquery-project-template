#!/bin/bash
set -e

# The script update metadata of BigQuery tables and sources with dbt sources.

# Arguments
models_dir=${1:?"The 1st argument for models_dir is not set"}
vars_path=${2:?"The 3rd argument for path to a vars YAML file is not set"}
client_project=${3:-""}
dry_run=${4:-0}

# Get YAML files for BigQuery datasets
source_paths=$(find "$models_dir" -mindepth 3 -maxdepth 3 -type f -name "*.yml")
if [[ -z "$source_paths" ]]; then
  echo "No YAML files for BigQuery datasets"
  exit 0
fi

# Update metadata of dbt sources one by one.
# NOTE: append `--dry_run` if `$dry_run` is not 0.
# shellcheck disable=SC2046
# shellcheck disable=SC2005
for source_path in ${source_paths}; do
  # Validate the file.
  if [[ ! -f "$source_path" ]]; then
    echo "WARN: ${source_path} is not a file."
    continue
  fi

  # Update metadata.
  # NOTE:
  # It doesn't use '--client_project' option,
  # because we have to set a GCP project with the default credentials.
  echo "update ${source_path}"
  if [[ -z "$client_project" ]]; then
    dbt-helper source update-from-source \
      --models_dir "$models_dir" \
      --vars_path "$vars_path" \
      --source_path "$source_path" \
      --client_project "$client_project" \
      $([[ $dry_run -ne 0 ]] && echo "--dry_run")
  else
    dbt-helper source update-from-source \
      --models_dir "$models_dir" \
      --vars_path "$vars_path" \
      --source_path "$source_path" \
      $([[ $dry_run -ne 0 ]] && echo "--dry_run")
  fi
done
