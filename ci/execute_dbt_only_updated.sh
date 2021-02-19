#!/bin/bash
set -e

# The script runs a dbt sub command with only changed files.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Constants
PROFILES_DIR="${PROJECT_DIR}/profiles"
PROFILE="dbt-jobs"

# Arguments
subcommand=${1:?"The first argument for a sub command is not set"}
target=${2:?"The second argument for dbt target is not set"}
selector=${3:?"The third argument for dbt selector is not set"}
vars_path=${4:?"The fourth argument for vars YAML is not set"}
execution_date=${5:?"The fifth argument for execution_date is not set"}

function get_dbt_resource_type() {
  # Get a dbt resource type corresponding to a sub command.
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
export -f get_dbt_resource_type

function get_dir_name() {
  # Get a directory name
  target_path=${1:?}
  if [[ -f "$target_path" ]]; then
    # Get the parent directory, if it is a file.
    dirname "${target_path}"
  elif [[ -d "$target_path" ]]; then
    # Get the directory, if it is a directory.
    echo "$target_path"
  else
    # Do nothing
    :
  fi
}
export -f get_dir_name

function get_intersected_resources() {
  # Get the same resources in two lists
  file1=${1:?}
  file2=${2:?}
  resource_list1=$(cat <"$file1" | sort)
  resource_list2=$(cat <"$file2" | sort)
  join <(echo "$resource_list1" | sort) <(echo "$resource_list2" | sort)
}
export -f get_intersected_resources

#
# main
#
resource_type="$(get_dbt_resource_type "${subcommand}")"

# Get resources selected by a selector
selected_resources=$(
  EXECUTION_DATE="${execution_date}" \
    dbt ls \
    --profiles-dir "$PROFILES_DIR" \
    --profile "$PROFILE" \
    --target "$target" \
    --vars "$(cat "$vars_path")" \
    --resource-type "${resource_type}" \
    --selector "$selector" ||
    :
)
echo "# selected resources: $(echo "$selected_resources" | wc -w)"

# Get updated directories in models.
pattern='^models\/.*\.\(sql\|yml\|md\)$'
changed_files=$(bash "${SCRIPT_DIR}/get_changed_files.sh" "$pattern")
updated_dirs=$(echo "$changed_files" | xargs -I% bash -c 'get_dir_name %')
echo "# updated dirs: $(echo "$updated_dirs" | wc -w)"

# Halt if there is no changed files.
if [[ -z "${updated_dirs//\ /}" ]]; then
  echo "There is no changed dbt resources."
  exit 0
fi

# Get updated resources based on git commits
# NOTE: can't pass double-quoted `$updated_dirs`
# shellcheck disable=SC2086
updated_resources=$(
  EXECUTION_DATE="${execution_date}" \
    dbt ls \
    --profiles-dir "$PROFILES_DIR" \
    --profile "$PROFILE" \
    --target "$target" \
    --vars "$(cat "$vars_path")" \
    --resource-type "${resource_type}" \
    --select $updated_dirs ||
    :
)

# Get updated resources in the selector
timestamp="$(date '+%s')"
output_file1="/tmp/selected_resources.${timestamp}.txt"
output_file2="/tmp/updated_resources.${timestamp}.txt"
echo "$selected_resources" >"$output_file1"
echo "$updated_resources" >"$output_file2"
updated_resources_in_selector=$(get_intersected_resources "$output_file1" "$output_file2")
echo "# updated resources in the selector: $(echo "$updated_resources_in_selector" | wc -w)"

# Halt if there is no changed files.
if [[ $(echo "$updated_resources_in_selector" | wc -w) -eq 0 ]]; then
  echo "There is no changed dbt resources."
  exit 0
fi

# Run dbt command with updated resources in the selector.
# NOTE:
#   If `updated_resources_in_selector` is large,
#   the command potentially doesn't work due to the shell limitation.
export EXECUTION_DATE="${execution_date}"
if [[ $subcommand == "snapshot" ]]; then
  # shellcheck disable=SC2086
  dbt "$subcommand" \
    --profiles-dir "$PROFILES_DIR" \
    --profile "$PROFILE" \
    --target "$target" \
    --vars "$(cat "$vars_path")" \
    --select $updated_resources_in_selector
else
  # shellcheck disable=SC2086
  dbt "$subcommand" \
    --profiles-dir "$PROFILES_DIR" \
    --profile "$PROFILE" \
    --target "$target" \
    --vars "$(cat "$vars_path")" \
    --models $updated_resources_in_selector
fi
