# dbt profiles
The documentation describes the dbt profiles used in the project.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [`./profiles/profiles.yml`](#profilesprofilesyml)
- [`./docker/dbt/.dbt/profiles.yml`](#dockerdbtdbtprofilesyml)
- [Environment variables](#environment-variables)
  - [DBT_BIGQUERY_PRIORITY](#dbt_bigquery_priority)
  - [DBT_BIGQUERY_LOCATION](#dbt_bigquery_location)
  - [DBT_THREADS](#dbt_threads)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## `./profiles/profiles.yml`
[`./profiles/profiles.yml`](../../profiles/profiles.yml) is used to directly run dbt jobs without a docker container.
For instance, we use it to run dbt locally as well as CircleCI jobs.

## `./docker/dbt/.dbt/profiles.yml`
[`./docker/dbt/.dbt/profiles.yml`](../../docker/dbt/.dbt/profiles.yml) is used to run dbt job with a docker container.
When we want to run a docker container of the dbt project, the file is required.

## Environment variables
We expose the environment variables to flexibly change a dbt profile.

### DBT_BIGQUERY_PRIORITY
The environment variable is passed to the `priority` feature.
It enables us to use which BigQuery priority, `batch` or `interactive`.

### DBT_BIGQUERY_LOCATION
The environment variable is passed to the `location` feature.
Please see [the official documentation](https://cloud.google.com/bigquery/docs/locations) for available values.

### DBT_THREADS
The environment variable is passed to the `threads` feature.
It enables us to control concurrency of dbt jobs.