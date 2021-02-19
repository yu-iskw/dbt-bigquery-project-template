#!/bin/bash
set -e

# The script runs a dbt sub command.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Constants
PROFILES_DIR="${PROJECT_DIR}/profiles"
PROFILE="dbt-jobs"

# Arguments
subcommand=${1:?"The first argument for a sub command is not set"}
target=${2:?"The second argument for dbt target is not set"}
vars_path=${3:?"The third argument for vars YAML is not set"}
selector=${4:?"The fourth argument for dbt selector is not set"}
execution_date=${5:?"The fifth argument for execution_date is not set"}

function get_dbt_resource_type() {
  # Get a dbt resource type corresponding to a sub command.
  # SEE `dbt list --help`.
  subcommand=${1:?}
  if [[ "$subcommand" == "run" ]]; then
    echo "model"
  elif [[ "$subcommand" == "test" ]]; then
    echo "test"
  elif [[ "$subcommand" == "source" ]]; then
    echo "source"
  elif [[ "$subcommand" == "snapshot" ]]; then
    echo "snapshot"
  elif [[ "$subcommand" == "compile" ]]; then
    echo "all"
  else
    echo "Not matched resource type to ${subcommand}"
    exit 1
  fi
}

#
# main
#
resource_type="$(get_dbt_resource_type "${subcommand}")"

# Get resources selected by a selector
#
# NOTE:
# When the number of target resources is 0, dbt CLI returns exist status 1.
# To avoid a process of dbt CLI is failed, we make sure the number of dbt resources.
# If it is 0, then return the exist status 0.
selected_resources=$(
  EXECUTION_DATE="${execution_date}" \
  dbt ls \
    --profiles-dir "$PROFILES_DIR" \
    --profile "$PROFILE" \
    --target "$target" \
    --vars "$(cat "$vars_path")" \
    --resource-type "${resource_type}" \
    --selector "$selector" \
  || :
)

# Completed successfully if there is no selected resources.
if [[ $(echo "$selected_resources" | wc -w) -eq 0 ]] ; then
  echo "No selected resources."
  exit 0
fi

# Run dbt command
# shellcheck disable=SC2046
EXECUTION_DATE="${execution_date}"\
  dbt "${subcommand}" \
    --profiles-dir "$PROFILES_DIR" \
    --profile "$PROFILE" \
    --target "$target" \
    --selector "$selector" \
    --vars "$(cat "$vars_path")"
