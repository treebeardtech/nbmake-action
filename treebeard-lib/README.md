# treebeard-lib

Contains functionality for interacting with the scheduler service via the CLI and running builds

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

