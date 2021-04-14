#!/bin/bash
set -e

# The script generate dbt docs.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

EXECUTION_DATE="$(date '+%Y-%m-%dT%H:%M')"
export EXECUTION_DATE
dbt docs generate \
  --profiles-dir "${PROJECT_DIR}/profiles" \
  --profile "dbt-metadata" \
  --target "prod" \
  --vars "$(cat "${PROJECT_DIR}/config/prod/vars.yml")"
