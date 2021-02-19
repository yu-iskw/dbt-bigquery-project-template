# Common custom tags and labels in dbt
**status**: draft

The documentation describes common tags and labels in dbt.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Common tags in dbt](#common-tags-in-dbt)
  - [Tags to specify environments](#tags-to-specify-environments)
  - [Tags to schedule dbt models](#tags-to-schedule-dbt-models)
  - [Tags to schedule dbt tests](#tags-to-schedule-dbt-tests)
  - [Tags for CI](#tags-for-ci)
- [Common labels in dbt](#common-labels-in-dbt)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

----
## Common tags in dbt
We defines common tags to efficiently manage our dbt resources.

### Tags to specify environments
The tag(s) are used to control the target environment.

|tag        |description                                                  |
|-----------|-------------------------------------------------------------|
|`only_dev` |tagged resources are run only in the development environment.|
|`only_prod`|tagged resources are run only in the production environment. |
|`WIP`      |Skip the resources in the scheduler.                         |

Here is the relationship between the tags and scheduled environments.

|environment     |`only_dev`|`only_prod`|`WIP`|no `only_dev`/`only_prod`/`WIP`|
|----------------|----------|-----------|-----|-------------------------------|
|`staging` in dev|O         |X          |X    |O                              |
|`main` in prod  |X         |O          |X    |O                              |


### Tags to schedule dbt models
The tags are used to control intervals of dbt models.
The types of tags should be mutually exclusive.
As well as the tags should not used for dbt tests, the tags are not used in the selectors for dbt tests.
So, dbt tests with the tags are not scheduled as expected.

|tag      |description                            |NOTE                   |
|---------|---------------------------------------|-----------------------|
|`hourly` |tagged resources are scheduled hourly. |Not scheduled          |
|`daily`  |tagged resources are scheduled daily.  |Scheduled with CircleCI|
|`weekly` |tagged resources are scheduled weekly. |Not scheduled          |
|`monthly`|tagged resources are scheduled monthly.|Not scheduled          |

### Tags to schedule dbt tests
The tags are used to control intervals of dbt tests
The types of tags should be mutually exclusive too.

When we run scheduled tests, we have to prioritize them.
Because even running dbt tests consume BigQuery slots.
In order not to use unnecessary BigQuery slots, we run important tests with `daily_test`.
If it is okay to run ones weekly or monthly, we make the frequency less with `weekly_test` or `monthly_test`.

|tag           |description                            |NOTE                   |
|--------------|---------------------------------------|-----------------------|
|`hourly_test` |tagged resources are scheduled hourly. |Scheduled with CircleCI|
|`daily_test`  |tagged resources are scheduled daily.  |Scheduled with CircleCI|
|`weekly_test` |tagged resources are scheduled weekly. |Scheduled with CircleCI|
|`monthly_test`|tagged resources are scheduled monthly.|Scheduled with CircleCI|

### Tags for CI

|tags                   |description                                         |
|-----------------------|----------------------------------------------------|
|`skip_query_validation`|Skip compiled query validations in both dev and prod|

----
## Common labels in dbt
First of all, we have to understand the difference between `config.labels` in dbt models and `models.meta` in dbt schemas.
`config.labels` in dbt models are used to write labels to BigQuery and doesn't appear on the dbt web UI.
On the other hand, `models.meta` in schemas appear only on the dbt web UI.
We have to maintain both respectively.

|label         |description                                    |example                     |
|--------------|-----------------------------------------------|----------------------------|
|`owner`       |Who is the owner of a table/view               |                            |
|`modeled`     |Modeling tool                                  |`dbt`                       |
|`source`      |Original data source                           |`spanner`                   |
|`contains_pii`|Contains PII in a table or a column if `"true"`|`false`                     |
|`status`      |status of table specification                  |`experimental`,`deprecated` |
|`interval`    |Scheduling interval                            |`daily`                     |
|`SLA`         |SLA of a table                                 |                            |

