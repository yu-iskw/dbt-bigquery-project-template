#!/bin/bash
set -e

# The script checks if the `./target` directory exists or not.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

NUM_FILES=$(find "${PROJECT_DIR}/target" -type f | wc -l)

if [[ $NUM_FILES -eq 0 ]] ; then
  echo "There is no file in ./target ."
  exit 1
fi
