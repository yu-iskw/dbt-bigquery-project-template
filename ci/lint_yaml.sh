#!/bin/bash
set -e

# The script validates YAML files.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Validate foundation YAML files
yamllint "${PROJECT_DIR}"/docker \
  "${PROJECT_DIR}"/.github \
  "${PROJECT_DIR}"/*.yml

# Validate dbt related YAML files
yamllint "${PROJECT_DIR}"/config \
  "${PROJECT_DIR}"/profiles \
  "${PROJECT_DIR}"/macros \
  "${PROJECT_DIR}"/models \
  "${PROJECT_DIR}"/analysis \
  "${PROJECT_DIR}"/snapshots
