<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [How to upgrade dbt](#how-to-upgrade-dbt)
  - [Upgrade dbt in requirements.txt](#upgrade-dbt-in-requirementstxt)
  - [[Optional] Upgrade python](#optional-upgrade-python)
    - [CircleCI](#circleci)
    - [Docker image](#docker-image)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# How to upgrade dbt

## Upgrade dbt in requirements.txt
[./requirements.txt](../../requirements.txt) is used to specify the dbt version of the project.
The file is used even for building a docker image with [./docker/dbt](../../docker/dbt).

## [Optional] Upgrade python
If we want to upgrade the python version for scheduled jobs, we have to 

### CircleCI
We use the official docker image of Google Cloud SDK.
Unfortunately, we don't specify a python version at the moment.

### Docker image
We change the docker tag in:
- [./docker/dbt/Dockerfile](../../docker/dbt/Dockerfile)
- [./docker/dbt-helper/Dockerfile](../../docker/dbt-helper/Dockerfile)