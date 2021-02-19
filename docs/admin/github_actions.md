# GitHub Actions

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Code reviewer assignments](#code-reviewer-assignments)
- [Add labels to PRs](#add-labels-to-prs)
- [Generate "Table of Contents" of markdown files.](#generate-table-of-contents-of-markdown-files)
- [Create a PR to merge staging into main](#create-a-pr-to-merge-staging-into-main)
- [Create a git tag on the latest main branch](#create-a-git-tag-on-the-latest-main-branch)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Code reviewer assignments
The file is used to manage automatic code reviewer assignments.
Please see [About code owners \- GitHub Docs](https://docs.github.com/en/free-pro-team@latest/github/creating-cloning-and-archiving-repositories/about-code-owners).

* [CODEOWNERS](../../.github/CODEOWNERS)

## Add labels to PRs
The workflow is used to automatically add labels to pull requests based on file paths of changed files.

* [labeler.yml](../../.github/labeler.yml): The rules to add labels to PRs. Even if we don't pre-define labels, labeler automatically create tags defined in the file.
* `workflows/labeler.yml`: The GitHub Actions workflow

## Generate "Table of Contents" of markdown files.
The workflow is used to generate "Table of Contents" of markdown files.

* [workflows/generate-markdown-toc.yml](../../.github/workflows/generate-markdown-toc.yml)

## Create a PR to merge staging into main
The workflow is used to create a pull request to merge staging into main.

* [workflows/merge-staging-into-main-pr.yml](../../.github/workflows/merge-staging-into-main-pr.yml)

## Create a git tag on the latest main branch
The workflow is used to create a git tag on the latest main branch at the time of triggering it.

* [.github/workflows/git-tag-on-main.yml](../../.github/workflows/git-tag-on-main.yml)