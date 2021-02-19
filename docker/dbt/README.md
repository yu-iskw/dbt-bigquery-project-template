# Docker image of dbt
The docker image is used to run the dbt CLI.

## How to use
The permission to pull docker images from `YOUR_PROJECT_PROD` is required.

```bash
# Pull the latest docker image from GCR
docker pull gcr.io/YOUR_PROJECT_PROD/dbt:latest

# Call the dbt CLI
# The `./config` directory is included in the docker image.
docker run --rm  gcr.io/YOUR_PROJECT_PROD/dbt:latest \
    ls --vars "$(cat ./config/prod/vars.yml)"

# Launch a web UI
# The docker image contains already built dbt docs.
docker run --rm -p 8080:8080 \
    gcr.io/YOUR_PROJECT_PROD/dbt:latest \
    docs serve
```

## NOTES

### dbt profiles
`.dbt` is a directory to store the default dbt profiles.
When we want to change the GCP projects to run dbt, we have to change the profiles.

### CircleCI
When we use CircleCI to schedule jobs, we don't use the docker image.
