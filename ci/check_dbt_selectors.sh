#!/bin/bash
set -e

# The script validates `selectors.yml` of dbt.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# A list of skipped selectors
SKIPPED_SELECTORS=(
  "hourly-dev"
  "hourly-prod"
  "hourly-tests-dev"
  "hourly-tests-prod"
  "weekly-dev"
  "weekly-prod"
  "weekly-tests-dev"
  "weekly-tests-prod"
  "monthly-dev"
  "monthly-prod"
  "monthly-tests-dev"
  "monthly-tests-prod"
)

# Path to selectors.yml
selectors_yaml_path=${1:-"${PROJECT_DIR}/selectors.yml"}

selector_names=$(yq '.selectors[].name' "$selectors_yaml_path")

FAILED=0
for selector_name in $selector_names; do
  # Replace `"` with ``.
  selector_name="${selector_name//\"/}"

  # Skip a selector if matched
  is_skipped=0
  for skipped_selector in ${SKIPPED_SELECTORS[*]}
  do
    if [[ "$selector_name" == "$skipped_selector" ]] ; then
      echo "${selector_name} is skipped due to the while list."
      is_skipped=1
    fi
  done
  if [[ $is_skipped == 1 ]] ; then
    continue
  fi

  # Count the number of selected models, tests and so on.
  echo "Check selector:${selector_name}"
  result=$(
    dbt ls \
      --selector "${selector_name}" \
      --profiles-dir "${PROJECT_DIR}/profiles" \
      --profile "dbt-metadata" \
      --target "prod" \
      --vars "$(cat "${PROJECT_DIR}/config/prod/vars.yml")" | wc -l)
  echo "Selector:${selector_name} selects ${result} dbt resources."

  if [[ $result -eq 0 ]]; then
    echo "Could not find any dbt models with ${selector_name}"
    FAILED=1
  fi
done

if [[ $FAILED -eq 1 ]]; then
  exit 1
fi
