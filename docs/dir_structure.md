# Directory Structure

**NOTE: dbt version is 0.18.1 at the time of writing the document.**

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [`models` Directories](#models-directories)
  - [dbt models under `./models`](#dbt-models-under-models)
  - [dbt sources under `./models/`](#dbt-sources-under-models)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## `models` Directories
Our dbt models and sources are under `./models`.

### dbt models under `./models`
A file name of dbt model has to be unique.

Take `users.sql` which we have different tables, but whose names are the same, for instance.
Even if we hold files whose name `users.sql` in different directories, dbt doesn't allow us to name them the same.
So, we decided to put not only table ID, but also GCP project ID and dataset ID.

The naming rule follows `models/${GCP_PROJECT_ALIAS}/${DATASET_ID}/${TABLE_ID}/`
- `${GCP_PROJECT_ALIS}`: An alias of GCP project.
- `${DATASET_ID}`: BigQuery dataset ID
- `${TABLE_ID}`: BigQuery table ID

### dbt sources under `./models/`
On the flip side, a file name of dbt source should not be unique.
But, we make a dbt source file unique to make it easier to understand.
