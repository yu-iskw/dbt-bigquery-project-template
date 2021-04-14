#!/bin/bash
set -e

# The script is used to build and push a docker image of dbt.
#
# Usage: build_dbt_docker.sh MODE TARGET DOCKER_TAG
#   - MODE: "build" or "push"
#   - TARGET: "dev" or "prod"
#   - DOCKER_TAG: a docker tag

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Constants
DEV_PROJECT_ID="<< DEV_PROJECT_ID >>"
PROD_PROJECT_ID="<< PROD_PROJECT_ID >>"

# Arguments
mode=${1:?"mode is not set"}
target=${2:?"target is not set"}
docker_tag=${3:?"docker_tag is not set"}

# Validate arguments
if [[ "$mode" != "build" ]] && [[ "$mode" != "push" ]]; then
  echo "model should be 'build' or 'push'."
  exit 1
fi

# Get the docker image name
if [[ "$target" == "dev" ]]; then
  export docker_image="gcr.io/${DEV_PROJECT_ID}/dbt:${docker_tag}"
elif [[ "$target" == "prod" ]]; then
  export docker_image="gcr.io/${PROD_PROJECT_ID}/dbt:${docker_tag}"
else
  echo "target should be dev or prod"
  exit 1
fi

# Build docker image
docker build --rm \
  -f "${PROJECT_DIR}"/docker/dbt/Dockerfile \
  -t "$docker_image" \
  "${PROJECT_DIR}"

# If mode is "push", then push the docker image.
if [[ "$mode" == "push" ]]; then
  docker push "$docker_image"
fi
