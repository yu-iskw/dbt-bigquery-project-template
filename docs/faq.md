# Frequently Asked Questions

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Q: Can we run BigQuery queries on the web UI of dbt?](#q-can-we-run-bigquery-queries-on-the-web-ui-of-dbt)
- [Q: How will we schedule dbt jobs?](#q-how-will-we-schedule-dbt-jobs)
- [Q: How does dbt manage the metadata?](#q-how-does-dbt-manage-the-metadata)
- [Q: Is the web UI open sourced?](#q-is-the-web-ui-open-sourced)
- [Q: What is the license of dbt?](#q-what-is-the-license-of-dbt)
- [Q: Can we control the contents based on the permission?](#q-can-we-control-the-contents-based-on-the-permission)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Q: Can we run BigQuery queries on the web UI of dbt?
No, we can’t. All we can do on the web UI is look for the metadata of BigQuery tables. It is impossible to see the detailed data on it.

## Q: How will we schedule dbt jobs?
We can take advantage of CircleCI scheduled jobs.

## Q: How does dbt manage the metadata?
Dbt doesn’t have any metadata database. Instead, we build a JSON file with the dbt CLI to generate docs.

## Q: Is the web UI open sourced?
Yes, it is open sourced at the github repo. Actually, the creator of dbt offers the cloud version as a commercial service. But, we can use the web UI server for free.

## Q: What is the license of dbt?
The license is Apache License 2.0.

## Q: Can we control the contents based on the permission?
Not really. The contents are the same for everyone. But, in my opinion, it would be acceptable, because we can see only metadata of BigQuery tables and views. If we still want to hide some tables and views, dbt provides the feature to select what contents are included in the web UI.
