<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [dbt-helper](#dbt-helper)
  - [Hot wo intall](#hot-wo-intall)
  - [How to use](#how-to-use)
  - [Examples](#examples)
  - [How to contribute](#how-to-contribute)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# dbt-helper
The python module is used to create a custom command line tool which is called `dbt-helper`.
The main objectives are:

1. to generate scaffold files from the templates, and
2. to write metadata of dbt sources.

First, `dbt-helper` enables us to become more productive by automatically following the rule to implement dbt models.
For instance, when we implement a dbt model, we have to follow the rules, such as a path to the dbt model and the file names.
It is hard to ask every dbt model developers to understand the rules.

Second, `dbt-helper` enables us to fill in the missing piece of dbt.
Actually, dbt enables us to persist metadata of dbt models in BigQuery.
However, at the time of dbt==0.18.2, it doesn't have a feature to persist metadata of dbt sources as existing tables.

## Hot wo intall
We don't publish the command line tool.
So, we have to directly install by passing the local path.
```bash
$ pip install -e .
```

## How to use
`dbt-helper --help` enables us to show the help message.
It has nested sub commands.
Please dive into the details.

```bash
$ dbt-helper --help

Usage: dbt-helper [OPTIONS] COMMAND [ARGS]...

  CLI body

  Args:     context: click context

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  analysis    sub commands for dbt analysis
  completion  Install the auto-completion for dbt-helper
  model       sub commands for dbt model
  snapshot    sub commands for dbt snapshot
  source      sub commands for dbt source
```

## Examples
Please take a look at [examples](./examples).

## How to contribute
Please see [`CONTRIBUTING.md`](./CONTRIBUTING.md).