# Docker image of dbt-helper
The docker image is used to run `dbt-helper`.

## How to use
The permission to pull docker images from `YOUR_PROJECT_PROD` is required.

```bash
# Pull the latest docker image from GCR
docker pull gcr.io/YOUR_PROJECT_PROD/dbt-helper:latest

# The entrypoint is `dbt-helper`.
docker run --rm gcr.io/YOUR_PROJECT_PROD/dbt-helper:latest \
  --help
```