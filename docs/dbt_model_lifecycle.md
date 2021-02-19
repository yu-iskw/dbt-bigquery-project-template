# dbt model lifecycle
The documentation briefly describes the model life cycle in the project.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [1. Create a model](#1-create-a-model)
- [2. Schedule a model](#2-schedule-a-model)
- [3. Deprecate a model](#3-deprecate-a-model)
- [4. Drop a model](#4-drop-a-model)
  - [Disable a model](#disable-a-model)
  - [Remove files for a model](#remove-files-for-a-model)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## 1. Create a model
First of all, we create a dbt model.

## 2. Schedule a model
When we want to schedule a model, we annotate a tag like `daily`.
```sql
{{
  config(
    enabled=true,
    ...,
    tags=["daily", ...],
  )
}}
```

## 3. Deprecate a model
When we make a model deprecated, we remove a tag to schedule and annotate `"status": "deprecated"`.
Actually, the label is just shown on the BigQuery UI.
However, that might be useful for the data consumers.
When we want to drop a model immediately, we can skip the step.

```sql
{{
  config(
    enabled=true,
    labels={
      "status": "deprecated",
      ...
    },
    ...,
  )
}}
```

## 4. Drop a model
When we are ready to drop a model on BigQuery, we follow the two steps as below.
dbt doesn't support remove models on warehouses by default.
We implemented the feature by our self. 

### Disable a model
We make a model disabled by setting `config.enabled=false`.
We have a dbt-helper command to drop disabled models on BigQuery.

```sql
{{
  config(
    enabled=false,
    ...,
  )
}}
```

### Remove files for a model
After dropping a model on BigQuery in the development and production environment, it is time to remove files for a model.
Let's create another pull request to remove files of a model.