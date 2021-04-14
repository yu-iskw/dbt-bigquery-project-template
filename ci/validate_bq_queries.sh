#!/bin/bash
set -e

# This script is used to validate BigQuery queries in a directory.
# The extension should be ".sql".

# Arguments
input_dir=${1:?"The 1st argument for a directory which contains query files is not set."}
ignore_schema_tests=${2:-0}
project_id=${3:-''}
verbose=${4:-0}

function is_schema_test {
  # TODO support data test
  # Check if a given path
  local _path=${1:?"path is not set."}
  if [[ "$_path" =~ /schema_test/.*\.sql ]]; then
    echo 1
  else
    echo 0
  fi
}
export -f is_schema_test

# Check if SQL files exist.
if [[ ! -d "$input_dir" ]] || [[ $(echo "$sql_files" | wc -l) == 0 ]]; then
  echo "No SQL files"
  exit 0
fi
echo "# SQL files: $(echo "$sql_files" | wc -l)"

# Validate BigQuery queries and permissions with 'bq'.
export FAILED=0
sql_files=$(find "$input_dir" -iname "*.sql")
for sql_file in $sql_files; do
  # Check if a file exists.
  if [[ ! -f "$sql_file" ]]; then
    echo "WARN: ${sql_file} is not a file."
  fi

  # If a SQL file is a schema test, then skip it.
  if [[ "$ignore_schema_tests" != "0" ]] && [[ $(is_schema_test "$sql_file") -ne 0 ]]; then
    if [[ $verbose -ne 0 ]]; then
      echo "Skip ${sql_file}, because it is a schema test."
    fi
    continue
  fi
  echo "check ${sql_file}"

  # `bq query --dry_run` can validate a query and GCP permissions.
  # '|| status=$?' looks hacky, but it is required not to immediate stop the shell script.
  if [[ -z $project_id ]]; then
    bq query --use_legacy_sql=false --dry_run <"${sql_file}" || status=$?
  else
    bq query --use_legacy_sql=false --dry_run --project_id="$project_id" <"${sql_file}" || status=$?
  fi
  if [[ $status -ne 0 ]]; then
    export FAILED=1
  fi
done

# Exit as error if failed is 1.
if [[ $FAILED -eq 1 ]]; then
  echo "Failed"
  exit 1
else
  echo "All checked queries are valid."
fi
