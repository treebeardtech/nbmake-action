## Development Install

```bash
pipenv install
```

## Development against Backend

To run against local services

```bash
export TREEBEARD_ENVIRONMENT=development
```

To run against prod services but with Sentry suppressed

```bash
export TREEBEARD_ENVIRONMENT=staging
```

## Code Quality Checks

Clone typeshed into the **repo root**

```bash
git clone https://github.com/python/typeshed.git
```

```bash
pyright && python3.7 -m black --check .
```

```bash
isort -m 3 -tc -y
```
