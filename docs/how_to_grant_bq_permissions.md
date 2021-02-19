# How to grant BigQuery permissions for dbt
The documentation describes the service accounts to run dbt and how to grant appropriate permissions to them.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [GCP service accounts for dbt](#gcp-service-accounts-for-dbt)
  - [Production environment](#production-environment)
  - [Development environment](#development-environment)
- [Edit `vars.yml`](#edit-varsyml)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## GCP service accounts for dbt
We have some GCP service accounts for the dbt project.
We carefully separate them based on their roles and based on the environments.
There are two perspectives:
- One is about the environment which is for the development one or the production one.
- The other is about data manipulation or metadata manipulation.

If the service accounts don't have enough permission in a GCP project, we have to grant ones to the service account.

### Production environment
- Service account to run dbt jobs
  - Description: The service account is used to deal with data on BigQuery in the production environment.
  - Email: `dbt-job@YOUR_PROJECT_PRD.iam.gserviceaccount.com`
- Service account for metadata
  - Description: The service account is used to deal with metadata of BigQuery, such as table description, in the production environment.
  - Email: `dbt-metadata@YOUR_PROJECT_PRD.iam.gserviceaccount.com`

### Development environment
- Service account to run dbt jobs
  - Description: The service account is used to deal with data on BigQuery in the development environment.
  - Email: `dbt-job@YOUR_PROJECT_DEV.iam.gserviceaccount.com`
- Service account for metadata
  - **No service account**.
    Because some tables exist only in the production environment. 
    As well as, it is annoying to manage ones in both of dev/prod.
    
## Edit `vars.yml`
We have `vars.yml` depending on the environment.
We manage aliases of GCP project in the YAML file.
Please add a new project to the YAML files respectively.

```
config
├── dev
│ └── vars.yml
├── local
│ └── vars.yml
└── prod
   └── vars.yml
```

