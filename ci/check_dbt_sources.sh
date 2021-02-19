#!/bin/bash
set -e

# The script check if YAML files of dbt sources contains expected values,
# such as owner information.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Arguments
models_dir=${1:-"${PROJECT_DIR}/models"}

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

function has_owner() {
  # Check if a dbt source has owner information.
  yaml_content=${1:?}
  RESULT="$(echo "$yaml_content" | yq -M 'select(.sources[]?.tables[]?.meta.owner)')"
  if [[ -z $RESULT ]]; then
    echo 0
  else
    echo 1
  fi
}

function extract_invalid_owner() {
  # Check if an owner contains only available characters.
  # SEE https://cloud.google.com/bigquery/docs/labels-intro#requirements
  yaml_content=${1:?}
  # Build the query to extract invalid owner
  condition=$(
    cat <<'EOS'
    .sources[]?.tables[]?.meta.owner as $owner
        | select($owner)
        | select($owner
        | test("^[A-Za-z0-9_-]+$") | not)
        | $owner
EOS
  )
  # Remove new line codes
  #condition=$(echo "$condition" | tr '\n' ' ')
  # Extract invalid owner
  invalid_owner=$(echo "$yaml_content" | yq -M "$condition")
  echo "$invalid_owner"
}

#
# main
#
FAILED=0
yaml_files=$(find "$models_dir" -type f -a -iname "*.yml" -o -iname "*.yaml")
for yaml_file in $yaml_files; do
  # Set a variable in order to avoid multiple reads from disk
  yaml_content="$(cat "$yaml_file")"

  # Skip non dbt source schema file.
  if [[ $(is_dbt_source_schema "$yaml_content") -eq 0 ]]; then
    continue
  fi

  # Check 'sources[].tables[].meta.owner'
  invalid_owner=$(extract_invalid_owner "$yaml_content")
  if [[ -n "$invalid_owner" ]]; then
    echo "ERROR: ${yaml_file} contains an invalid owner: ${invalid_owner}"
    FAILED=1
  fi

  # TODO ADD a check if owner is defined or not
  if [[ $(has_owner "$yaml_content") ]]; then
    echo "WARN: ${yaml_file} doesn't contain owner"
    #FAILED=1
  fi
done

# If FAILED is not 0, then exit with an error status code
if [[ $FAILED -ne 0 ]]; then
  echo "$0 was failed"
  exit 1
fi
