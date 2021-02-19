
# How to model dbt (Beginner)
This is an entry-level documentation to develop dbt.
Actually, deep understanding is necessary to make the best of dbt.
But, this focus on relatively easier topics to develop dbt.
We will learn more advanced topics in the intermediate-level and advanced-level documents.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Terminologies](#terminologies)
- [Goals of the documentation](#goals-of-the-documentation)
- [Set up a local environment](#set-up-a-local-environment)
  - [Prerequisites](#prerequisites)
  - [Get the source code and a create a new local branch](#get-the-source-code-and-a-create-a-new-local-branch)
  - [Install required libraries](#install-required-libraries)
  - [Prepare dbt profiles](#prepare-dbt-profiles)
  - [Specify the GCP project in development](#specify-the-gcp-project-in-development)
- [Implement dbt models and sources](#implement-dbt-models-and-sources)
  - [Implement a dbt model](#implement-a-dbt-model)
  - [Implement a dbt source](#implement-a-dbt-source)
- [Run dbt](#run-dbt)
  - [Create a BigQuery table](#create-a-bigquery-table)
  - [Test the created table](#test-the-created-table)
- [Daily schedule dbt models and tests](#daily-schedule-dbt-models-and-tests)
  - [Basic knowledge about dbt tags](#basic-knowledge-about-dbt-tags)
  - [Tags for daily scheduling](#tags-for-daily-scheduling)
- [Release workflow](#release-workflow)
- [Summary](#summary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Terminologies
We define some words in our case in order to more clearly share the context.

- **dbt model**: SQL and YAML files for BigQuery tables and views modeled by dbt.
- **dbt source**: YAML files for existing BigQuery tables and views loaded by other tools.
- **dbt test**: tests for data quality by dbt in YAML files.
- **dbt resources**: all of dbt model, dbt source and so on.

## Goals of the documentation
We learn:
- how to develop dbt models and sources using `dbt-helper`,
- basic knowledge to test data quality of our models and sources, and
- how to schedule our models as daily jobs.

## Set up a local environment

### Prerequisites
- Git
- Github account
- Python: 3.7 (or 3.8)
- (Optional) yamllint: YAML linter
    - `brew install yamllint`

### Get the source code and a create a new local branch
The default branch is not `main`, but `staging`.
When we send a pull request, please make sure if the target branch is `staging`.
```bash
$ git clone << this project >>

# All commands below have to be executed under the cloned directory.
$ cd << this project >>

# Create a new local branch from the default branch.
$ git checkout -b new-feature origin/staging
```

### Install required libraries
If you have `make` command, `make setup` enables us to execute the same commands as below.
```bash
# Install dbt and dbt-helper
$ pip install -r requirements.txt

# Install dbt packages
$ dbt deps
```

Once you have installed the libraries, please try `dbt --version` and `dbt-helper --version`.
```bash
$ dbt --version
installed version: 0.18.1
   latest version: 0.18.1

Up to date!

Plugins:
  - bigquery: 0.18.1
  - snowflake: 0.18.1
  - redshift: 0.18.1
  - postgres: 0.18.1

$ dbt-helper --version
dbt-helper, version 0.8.4
```

**NOTE**:
`dbt-helper completion` enables us to add a definition for completion.
Please make sure `dbt-helper completion --help`, if you are interested.

### Prepare dbt profiles
We have to configure dbt profiles to define connections to our data warehouse (BigQuery).
The default dbt is located in `~/.dbt/profiles.yml`.
As well as, dbt provides a command line option `--profiles-dir` to specify a directory where a profiles YAML file is.

[`./profiles`](../profiles) directory contains pre-defined dbt profiles.
We can use it, for example `dbt ls --profiles-dir ./profiles`.

If it is bothersome to pass the arguments every time, we can make it the default profiles.
To do that, we create a symbolic link of `./profiles` with `ln -s "$(realpath ./profiles/)" ~/.dbt`.
Then, dbt automatically load './profiles' by default.

While we develop dbt models locally, it would be good to use a personal GCP project.
Please replace the value of `project` with an available GCP project in [../profiles/profiles.yml](../profiles/profiles.yml).
The GCP project is used to select authentication or credentials to run BigQuery jobs.
It is different from the GCP project to create tables and views in the local development.

After modifying the value, let's make sure if the connection works as expected.
```bash
$ dbt debug
```

### Specify the GCP project in development
Some sub commands of `dbt` provide us `--vars` option.
For instance, `dbt run --vars`.
It enables us to pass variables from a YAML file, for instance a map between GCP project ID and their alias.
We can refer to variables in almost all dbt resources with `var()` macro.
So, if we want to refer to not defined GCP projects from new dbt models and sources, we have to add new definition in the YAML files.

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

Moreover, as we define a GCP project in the profiles YAML file, we have to change the GCP project in [./config/local/vars.yml](./config/local/vars.yml) for local development.
When the value of `projects.dev_project_id` is defined, we can switch the destination GCP project.

**NOTE**:
`{% set gcp_project = var('projects')['dev_project_id']|default(var('projects')['project-a'], True) %}` in a generated `.sql` file by dbt-helper is the expression to select the destination GCP project.
We will learn how to generate such a `.sql` file later.

## Implement dbt models and sources
We have set up the local environment.
So, let's start to develop dbt.

Here, we track how we created `project-a-{dev,prod}.components.notifications`.

### Implement a dbt model
We develop a dbt model for `project-a-{jp,prod}.components.notifications`.
We generate scaffold files of a dbt model with `dbt-helper model scaffold`.

```bash
# Generate scaffold files for a dbt model.
$ dbt-helper model scaffold \
    --models_dir ./models/ \
    --project_alias project-a \
    --dataset components \
    --table notifications \
    --owner data_managers \
    --materialization view \
    --overwrite
```

As a result of executing the command, we can generate the three files below.
We have to edit the generated files for a dbt model.
```bash
$ tree ./models/project_a/components/notifications
./models/project_a/components/notifications
├── docs.md
├── project_a__components__notifications.sql
└── schema.yml
```

1. docs.md:
    The description about the table.
    Markdown expressions are available.
    The description is used in `schema.yml` with the `doc()` macro.
2. project_a__components__notifications.sql:
    The `.sql` file is used to define the dbt model of `project-a-{dev,prod}.components.notifications`.
3. schema.yml:
    The YAML file is used to define tests of the table and columns as well as column descriptions.

**NOTE**:
You might think why the `.sql` file name is composed of the project ID, the dataset ID and the table ID and we should simply name it like `notification_settings.sql`.
dbt (0.18.x) identify each model with its file name.
Consider if we use `users.sql`.
There are conflicts by using the same name in different projects and datasets.
To avoid the situation, we name a file with a full table reference.

#### Implement `.sql` file
We model an intermediate BigQuery table or view with a `.sql` file.
We can basically use the BigQuery standard SQL and [jinja2](https://jinja.palletsprojects.com/en/2.11.x/) expressions.

As we can see, `.sql` file contains not only SQL statements but also `{{ config(..) }}`.
`{{ config(..) }}` enables us to configure a dbt model.
For instance, we can define a partitioned table and a clustered table.
Let's briefly look over the defined values.

- `owner`: owner of a dbt model
- `materialization`: strategy for persisting dbt models in a warehouse (e.g. `table`, `view`)
- `database`: a GCP project ID for a model
- `schema`: a dataset ID for a model
- `alias`: a table ID for a model
- `persist_docs`: flags to write metadata of a table or view
- `labels`: labels of a table or view, which are actually registered on BigQuery
- `tags`: tags to select dbt models. It is not directly related to BigQuery resources

Moreover, we would like to learn the most important macros to implement dbt models.
dbt automatically replaces the two macro with an actual reference of a table/view and interprets dependencies of dbt models and sources.
When we run `dbt run` with the two macros, it automatically executes dbt models with the right order.

- `{{ ref() }}`: used to refer to another dbt model.
- `{{ source() }}`: used to refer to a dbt source as an existing BigQuery table.

**NOTE**:
If you are interested in dbt jinja2 macros, please see '[dbt Jinja Functions](https://docs.getdbt.com/reference/dbt-jinja-functions/)'.

#### Implement `schema.yml`
The YAML file is used to define column descriptions and tests.

The builtin tests below are supported in dbt==0.18.1.
Please see the documentation about [tests](https://docs.getdbt.com/reference/resource-properties/tests/#test_name)..
- `not_null`: This test validates that there are no null values present in a column.
- `unique`: This test validates that there are no duplicate values present in a field.
- `accepted_values`: This test validates that all of the values in a column are present in a supplied list of values.
- `relationships`: This test validates that all of the records in a child table have a corresponding record in a parent table.

**NOTE**:
We can create a custom test and use test provided by 3rd party packages, such as dbt-utils.

#### Implement `docs.md`
We can add a table description by filling out `docs.md`.
A table description is put in a table or view of BigQuery.
The dbt web UI allows us to use markdown expressions.
However, BigQuery doesn't allow us to use markdown expressions.

### Implement a dbt source
Since the model we just implemented refers to `project-a.product.notifications` which is an existing BigQuery table, we have to define a dbt source for it as well.
`dbt-helper source importing` enables us to make a YAML file by importing metadata and schema information of the existing table.

**NOTE**:
We can use regular expression with `--table` option, when we want to import multiple tables in a dataset.

```bash
$ dbt-helper source importing \
    --models_dir ./models/ \
    --project project-a-prod \
    --project_alias project-a \
    --dataset product \
    --table "^notifications$" \
    --overwrite
```

Those are the basic properties of a source schema YAML file at dbt==0.18.1.
- `sources[].name`: a dataset ID
- `sources[].database` a GCP project ID
- `sources[].tables[].name`: unique ID in dbt
- `sources[].tables[].identifier`: a table ID
- `sources[].tables[].description`: a table description
- `sources[].tables[].tag`: tags to select the dbt source
- `sources[].tables[].meta`: labels of the dbt source
- `sources[].tables[].columns[].name`: a column name
- `sources[].tables[].columns[].description`: a column description
- `sources[].tables[].columns[].tests`: schema tests


## Run dbt
We have implemented the dbt mode and dbt source.
So, now let's run them on our machine to create an actual BigQuery table.

### Create a BigQuery table
First, we create a BigQuery table with the dbt model.
We don't look into the command line options of `dbt run` now.
If you want to see the help message of `dbt run`, please execute `dbt run --help`.

- `--vars`: passed variables from a YAML file. We can refer with `{{ var() }}` macro.
- `--models`: model selection. 

```bash
$ dbt run \
  --vars "$(cat ./config/local/vars.yml)" \
  --models models/project_a/components/notifications/

Running with dbt=0.18.1
Found 39 models, 239 tests, 0 snapshots, 3 analyses, 308 macros, 0 operations, 0 seed files, 40 sources

09:48:13 | Concurrency: 1 threads (target='dev')
09:48:13 |
09:48:13 | 1 of 1 START view model components.notification_settings............. [RUN]
09:48:16 | 1 of 1 OK created view model components.notification_settings........ [CREATE VIEW in 3.17s]
09:48:16 |
09:48:16 | Finished running 1 view model in 5.37s.

Completed successfully

Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

The command above enables us to create a table in the GCP project defined with `dev_project_id` of `./config/local/vars.yml`.
If we use a personal development GCP project, the table is located at `YOUR_PROJECT.components.notification_settings`.

**NOTE**:
If you are interested in model selection syntax, please see ["Syntax overview"](https://docs.getdbt.com/reference/node-selection/syntax/).

### Test the created table
We have created the table on BigQuery.
So, let's test the table with the tests defined in `schema.yml`.
`dbt test`(in reality `dbt test`) enables us to run tests of the created table.

```bash
$ dbt test \
  --vars "$(cat ./config/local/vars.yml)" \
  --models models/project_a/components/notifications/

Running with dbt=0.18.1
Found 39 models, 239 tests, 0 snapshots, 3 analyses, 308 macros, 0 operations, 0 seed files, 40 sources

09:59:18 | Concurrency: 1 threads (target='dev')
....
09:59:44 | Finished running 7 tests in 26.51s.

Completed successfully

Done. PASS=7 WARN=0 ERROR=0 SKIP=0 TOTAL=7
```

## Daily schedule dbt models and tests
We have learned how to implement a dbt model and a dbt source.
We might want to know how to schedule your models next.
Here, we learn how to schedule dbt models and tests.

All we have to do is to annotate specific dbt tags.
dbt developers don't care about other tools.

**NOTE**:
At the time of writing the documentation, we schedule daily jobs with CircleCI tentatively.
As well as, only daily jobs are supported.
We plan to migrate them to Apache Airflow in the future.

### Basic knowledge about dbt tags
Before describing the way to schedule dbt resources, we want to learn the basic knowledge about dbt tags.
In reality, dbt tags play various roles.
One of the important roles is to select specif models.
For example, when we want to run only dbt models with `daily` tag, we can pass the condition to `--models` option.

```bash
$ dbt run --models "tag:daily"
```

As well as, dbt enables us to express more complicated conditions with [YAML Selectors](https://docs.getdbt.com/reference/node-selection/yaml-selectors).

### Tags for daily scheduling
We defined custom tags and labels.
We have the list in ["Common custom tags and labels in dbt"](./tags_and_labels.md).
By following the rule, we can control the running environment, scheduling and so on.

In the documentation, we learn only the two tags below for daily scheduling.
- `daily`: used to daily schedule dbt models
- `daily_test`: used to daily schedule dbt tests

#### Annotate `daily` to a dbt model
`daily` tag is used like the below in a `.sql` file.
We put it into `{{ config() }}` as a "table-level tag" to run it every day.

```sql
{{
  config(
    ...
    tags=["daily"],
  )
}}
```

#### Annotate `daily_test` to a dbt test
`daily_test` tag is used with each test as the below in a schema YAML file.
When we annotate a tag to a test, we can call it "test-level tag".
In the case below, we can test uniqueness of `user_id` column every day.

```yaml
  columns:
    - name: user_id
      tests:
        - unique:
            tags: ["daily_test']
```

**CAUTION**:
Please tag `daily_test` to only significant tests in order to consume BigQuery slots as less as possible.

## Release workflow
[The documentation about CircleCI](../.circleci/README.md) describes the release workflow.
We have three stages on GitHub, a pull request, `staging` branch and `main` branch.

Only things we keep in mind here is the followings:
- When merging a pull request into `staging` branch, the corresponding environment is the development one.
- When merging `staging` branch into `main` branch, the corresponding environment is the production one.

## Summary
In the documentation, we mainly learned the followings:

- implementing `.sql` file, `schema.yml` and `docs.md` for a dbt model, generating scaffold files with `dbt-helper`,
- implementing a YAML file for a dbt source, generating scaffold file(s) with `dbt-helper`,
- running the model to create tables and views on BigQuery, 
- testing data quality of the created table, and
- scheduling daily models and tests with `daily` and `daily_test` tags.
