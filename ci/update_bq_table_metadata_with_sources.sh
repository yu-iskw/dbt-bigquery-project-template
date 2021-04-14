#!/bin/bash
set -e

# The script update metadata of BigQuery tables and sources with dbt sources.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Constants
PROFILES_DIR="${PROJECT_DIR}/profiles"
PROFILE="dbt-metadata"

# Arguments
models_dir=${1:?"The 1st argument for models_dir is not set"}
target=${2:?"The 2nd argument for dbt target is not set"}
vars_path=${3:?"The 3rd argument for path to a vars YAML file is not set"}
selector=${4:?"The 4th argument for dbt selector is not set"}
dry_run=${5:-0}

# Get updated sources.
# NOTE: `dbt list --output path` returns non-unique paths.
#       So, we have to unique them.
source_paths=$(
  dbt list \
    --profiles-dir "$PROFILES_DIR" \
    --profile "$PROFILE" \
    --target "$target" \
    --selector "$selector" \
    --vars "$(cat "$vars_path")" \
    --resource source \
    --output path |
    sort | uniq
)
echo "# selected resources: $(echo "$source_paths" | wc -w)"

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
  dbt-helper source update-from-source \
    --models_dir "$models_dir" \
    --vars_path "$vars_path" \
    --source_path "$source_path" \
    $([[ $dry_run -ne 0 ]] && echo "--dry_run")
done
