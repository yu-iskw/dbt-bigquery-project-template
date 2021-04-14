#!/bin/bash
set -e

# The script validates Dockerfiles.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

FAILED=0
dockerfiles=$(find "${PROJECT_DIR}/docker" -name "Dockerfile*")
for dockerfile in $dockerfiles; do
  echo "Check $dockerfile"
  hadolint --config "${PROJECT_DIR}/.hadolint.yml" "$dockerfile"
done

if [[ $FAILED -eq 1 ]]; then
  exit 1
fi
