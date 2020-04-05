# treebeard

A CLI tool that creates cloud runs for projects containing jupyter notebooks.

Treebeard creates a docker container from the project directory, builds and runs the project on commit, on a schedule, or at will, and serves rendered notebooks and tagged outputs via an API visible at an admin page.

A user account is needed to use the service at present.

## Development

To run against local services

`export TREEBEARD_ENVIRONMENT=development`

To run against prod services but with Sentry suppressed

`export TREEBEARD_ENVIRONMENT=staging`

## Code Quality Checks

Clone typeshed into the **repo root**

```
git clone https://github.com/python/typeshed.git
```

```
pyright && python3.7 -m black --check .
```
