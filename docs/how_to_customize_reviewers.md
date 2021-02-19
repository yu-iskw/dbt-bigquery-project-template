# How to Customize Code Reviewers
The document describes how to customize rules to assign pull requests to reviewers automatically.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [`CODEOWNERS`](#codeowners)
- [Recommended rules](#recommended-rules)
  - [GCP project based assignment](#gcp-project-based-assignment)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## `CODEOWNERS`
[GitHub CODEOWNERS](https://docs.github.com/en/free-pro-team@latest/github/creating-cloning-and-archiving-repositories/about-code-owners) are automatically requested for review when someone opens a pull request that modifies code that they own.
We have custom rules to assign pull requests to reviewers automatically.
[`./github/CODEOWNERS`](../.github/CODEOWNERS) is the file to define rules.

## Recommended rules

### GCP project based assignment
As you know, sub directories of `models` and `snapshots` are separated based on GCP projects.
