# How to make dbt analysis

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Overview](#overview)
- [Generate scaffold files of a dbt analysis with `dbt-helper`](#generate-scaffold-files-of-a-dbt-analysis-with-dbt-helper)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview
dbt's notion of `models` makes it easy for data teams to version control and collaborate on data transformations.
Sometimes though, a certain sql statement doesn't quite fit into the mold of a dbt model.
These more "analytical" sql files can be versioned inside of your dbt project using the `analysis` functionality of dbt.

Any `.sql` files found in the `analysis/` directory of a dbt project will be compiled, but not executed. 
This means that analysts can use dbt functionality like {{ ref(...) }} to select from models in an environment-agnostic way.

* SEE ALSO: [Analysis properties](https://docs.getdbt.com/reference/analysis-properties/)

## Generate scaffold files of a dbt analysis with `dbt-helper`
[Examples of dbt-helper](../python/dbt-helper/examples/README.md) describes how to use the sub command to generate scaffold files of a dbt analysis.
