# Example of dbt-helper

## `dbt-helper model`

### `dbt-helper model scaffold`
The command is used to generate a scaffold of dbt model.
`dbt-helper model scaffold --help` shows the help message.
```bash
$ dbt-helper model scaffold \
    --models_dir ./examples/ \
    --project_alias abc-def-123 \
    --dataset intermediate \
    --table user_attributes \
    --owner "analytics_team" \
    --materialization table \
    --tags daily --tags intermediate \
    --labels scheduler=airflow \
    --overwrite true

Files are generated under ./examples/abc_def_123/intermediate/user_attributes
```

## `dbt-helper source`

### `dbt-helper source scaffold`
The command is used to generate a scaffold of dbt source.
```bash
$ dbt-helper source scaffold \
    --models_dir ./examples/ \
    --project xyz-opq-987-prod \
    --project_alias xyz-opq-987 \
    --dataset production \
    --table users \
    --tags daily --tags intermediate \
    --labels owner="product_team" \
    --overwrite

Files are generated under ./examples/xyz_opq_987/production/users
```

### `dbt-helper source importing`
The command is used to import existing BigQuery tables as dbt sources.
```bash
$ dbt-helper source importing \
    --models_dir ./examples/ \
    --project xyz-opq-987-prod \
    --project_alias xyz-opq-987 \
    --dataset production \
    --table '^users$' \
    --overwrite
```

### `dbt-helper source update`
The command is used to update BigQuery metadata, such as descriptions of table and columns, with dbt source schema files.
```bash
$ dbt-helper source update \
    --models_dir ./examples/ \
    --dry_run false \
    --overwrite
```

## `dbt-helper analysis`

### `dbt-helper analysis scaffold`
The command is used to generate a scaffold of dbt analysis.
`dbt-helper analysis scaffold --help` shows the help message.

```bash
dbt-helper analysis scaffold \
  --analysis_dir "${SCRIPT_DIR}/analysis" \
  --path "region/service/product/metric_01" \
  --owner "product_team" \
  --overwrite
```

## `dbt-helper snapshot`

### `dbt-helper snapshot scaffold`
The command is used to generate a scaffold of dbt snapshot.
`dbt-helper snapshot scaffold --help` shows the help message.

```bash
dbt-helper snapshot scaffold \
  --snapshots_dir "${SCRIPT_DIR}/snapshots" \
  --project_alias abc-def-123 \
  --dataset snapshots \
  --table user_attributes \
  --owner "analytics_team" \
  --tags daily --tags snapshots \
  --labels scheduler=airflow \
  --experimental \
  --overwrite
```