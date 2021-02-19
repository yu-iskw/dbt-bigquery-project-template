#!/bin/bash
set -e

# The script gets changed files in terms of git.

# Arguments
pattern="${1:?"the first argument for pattern is not set"}"

# Constants
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# Determine the target
if [[ "$CURRENT_BRANCH" == "main" ]] || [[ "$CURRENT_BRANCH" == "staging" ]]; then
  # Compare with only the previous commit
  DIFF_TARGET="HEAD^ HEAD"
else
  DIFF_TARGET="origin/staging"
fi

# Get changed files which match the pattern.
# NOTE:
# `|| :` is used to avoid exit by grep, when no line matches the pattern.
changed_files=$(git diff $DIFF_TARGET --name-only --no-color | grep -e "$pattern" || :)

# Remove empty lines and lines start with `./`
echo "$changed_files" | grep -v -e '^\s*$' | sed -e 's/^\.\///g'