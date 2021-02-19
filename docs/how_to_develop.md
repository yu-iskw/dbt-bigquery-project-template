# How to develop dbt

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Prerequisites](#prerequisites)
- [Set up](#set-up)
  - [Get the source code and a create a new local branch](#get-the-source-code-and-a-create-a-new-local-branch)
  - [Install modules](#install-modules)
  - [Prepare dbt profiles](#prepare-dbt-profiles)
- [How to create dbt resources](#how-to-create-dbt-resources)
  - [How to create dbt model schema file](#how-to-create-dbt-model-schema-file)
  - [How to create dbt source schema file](#how-to-create-dbt-source-schema-file)
- [Basic dbt commands](#basic-dbt-commands)
  - [Generate compiled files](#generate-compiled-files)
  - [Generate and launch docs](#generate-and-launch-docs)
  - [Run dbt](#run-dbt)
  - [Run tests](#run-tests)
  - [Check freshness of dbt source](#check-freshness-of-dbt-source)
- [Appendix](#appendix)
  - [Appendix A: variables as configuration](#appendix-a-variables-as-configuration)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Prerequisites
- Python: 3.7 or later
- (Optional) yamllint: YAML linter
    - `brew install yamllint`

## Set up

### Get the source code and a create a new local branch
The default branch is not `main`, but `staging`.
When we send a pull request, please make sure if the target branch is `staging`.
```bash
$ git clone ${THIS_GIT}

# Create a new local branch from the default branch.
$ git checkout -b new-feature origin/staging
```

### Install modules
```bash
$ pip install -r requirements.txt
$ dbt deps

# Install dbt-helper
$ pip install -e ./python/dbt-helper
```

### Prepare dbt profiles
The default dbt is located in `~/.dbt/profiles.yml`.
As well as, dbt provides a command line options `--profiles-dir` to specify a directory where a profiles YAML file is.

[`./profiles``](../profiles) directory is an example of dbt prfiles.
We can use it, for example `dbt ls --profiles-dir ./profiles`.
As well as we can create a symbolic link of `./profiles` with `ln -s "$(realpath ./profiles/)" ~/.dbt`.
By doing that, dbt automatically load the profiles by default.

While we develop dbt models, it would be nice to use a personal GCP project.
Please modify the project in [../profiles/profiles.yml](../profiles/profiles.yml).

## How to create dbt resources
In this section, we will learn how to create dbt resources using `dbt-helper`.
`deb-helper` is our custom command line tool to boost the development of dbt.
We put some best practices in to `dbt-helper` not to repeat writing the fundamentals of dbt resources.
As well as, we keep the design of dbt resources easily.

### How to create dbt model schema file
`dbt-helper` enables us to generate a scaffold of a dbt model files.
We can generate a scaffold with the command below to create a new dbt model for `project-a-{dev,prod}.components.user_age`.

```bash
$ dbt-helper model scaffold \
    --models_dir ./models/ \
    --project_alias project-a \
    --dataset data_marts \
    --table user_profiles \
    --owner data_manager \
    --materialization view \
    --tags daily \
    --overwrite
```

As a result of executing the command, we can generate the following three files.
We have to edit the generated files for what we want.
``` bash
$ tree ./models/project_a/data_marts/user_profiles
├── docs.md
├── project_a__data_marts__user_profiles.sql
└── schema.yml
```

1. `docs.md`:
    The description about the table. 
    Markdown expressions are available.
    The description is used in `schema.yml` with the `doc()` macro.
2. `project_a__data_marts__user_profiles.sql`
    The `.sql` file is used to define the dbt model of `project-a-{dev,prod}.data_marts.user_profiles`.
3. `schema.yml`:
    The YAML file is used to defined tests of the table and columns as well as descriptions of column.

### How to create dbt source schema file
When dbt models we are creating require new dbt source, we have to create new dbt source schema files.
`dbt-helper` enables us to import existing BigQuery tables to dbt source schema files.

a. Generate a dbt source schema file from an existing BigQuery table
b. Modify the generated dbt source schema file

The command below enables us to import `project-a-prod.users` to a dbt source schema file.
As you can see, regular expression is available with `--table`.
When we want to import multiple tables under a BigQuery dataset, that would be convenient using regular expression.

```bash
$ dbt-helper source importing \
    --models_dir ./models/ \
    --project project-a-prod \
    --project_alias project-a \
    --dataset product \
    --table "^users$" \
    --dry_run false \
    --overwrite true
```

## Basic dbt commands
Please make sure if `projects.dev_project_id` in [./config/local/vars.yml](../config/local/vars.yml) is set to your personal GCP project.
Because dbt models are created in your personal GCP project rather than dev or prod environment.

### Generate compiled files
The compiled files are saved under `./target/compiled`.
```bash
$ dbt compile --vars "$(cat ./config/local/vars.yml)" --profiles-dir "./profiles"
```

### Generate and launch docs
```bash
$ dbt docs generate --vars "$(cat ./config/local/vars.yml)" --profiles-dir "./profiles"

$ dbt docs serve
```

### Run dbt
[Model selection syntax](https://docs.getdbt.com/reference/model-selection-syntax/) is very useful to specify only dbt resources you want to run.
```bash
$ dbt run --vars "$(cat ./config/local/vars.yml)"
```

### Run tests
```bash
$ dbt test --vars "$(cat ./config/local/vars.yml)"
```

### Check freshness of dbt source
```bash
$ dbt source snapshot-freshness --vars "$(cat ./config/local/vars.yml)"
```

## Appendix

### Appendix A: variables as configuration
Some sub commands of `dbt` provides us `--vars` option.
For instance, `dbt run --vars`.
It enables us to pass variables, such as a map between GCP project ID and their alias.
We can use the variables in almost all dbt resources with `var()` macros.

In that way, if we refer new GCP projects from new dbt models and sources, we have to add new definition in the YAML files.

[./config](../config) is the directory for the variables.
```bash
$ tree config
config
├── dev
│  └── vars.yml    # vars for dev environment
├── local
│  └── vars.yml    # vars for local development
└── prod
   └── vars.yml    # vars for prod environment
```
