#!/bin/bash
set -e

# The script runs 'dbt source snapshot-freshness'.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Constants
PROFILES_DIR="${PROJECT_DIR}/profiles"
PROFILE="dbt-jobs"

# Arguments
target=${1:?"The 1st argument for dbt target is not set"}
vars_path=${2:?"The 2nd argument for vars YAML is not set"}

# Run dbt command
dbt source snapshot-freshness \
  --profiles-dir "$PROFILES_DIR" \
  --profile "$PROFILE" \
  --target "$target" \
  --vars "$(cat "$vars_path")"