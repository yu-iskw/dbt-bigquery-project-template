#!/bin/bash
set -e

# The script tests dbt-helper by generating scaffold files.

SCRIPT_DIR="$(realpath "$(dirname $0)")"

# Generate scaffold of dbt model
dbt-helper model scaffold \
  --models_dir "${SCRIPT_DIR}/models" \
  --project_alias abc-def-123 \
  --dataset intermediate \
  --table user_attributes \
  --owner "analytics_team" \
  --materialization table \
  --tags daily --tags intermediate \
  --labels scheduler=airflow \
  --experimental \
  --overwrite

# Generate scaffold of dbt source
dbt-helper source scaffold \
  --models_dir "${SCRIPT_DIR}/models" \
  --project xyz-opq-987-prod \
  --project_alias xyz-opq-987 \
  --dataset production \
  --table users \
  --tags daily --tags intermediate \
  --labels owner="product_team" \
  --overwrite

# Generate scaffold of dbt analysis
dbt-helper analysis scaffold \
  --analysis_dir "${SCRIPT_DIR}/analysis" \
  --path "region/service/product/metric_01" \
  --owner "product_team" \
  --overwrite

# Generate scaffold of dbt snapshot
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
