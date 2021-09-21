**⚠️ Please use [nbmake](https://github.com/treebeardtech/nbmake) instead**

# nbmake-action

(repo renamed from 'treebeard').

**What?** A GitHub Action for testing notebooks, runs them from top-to-bottom

**Why?** To raise the quality of scientific material through better automation

**Who is this for?** Scientists/Developers who have written docs in notebooks and want to CI test them after every commit

## Functionality

Tests notebooks using [nbmake](https://github.com/treebeardtech/nbmake) via pytest.

**Note: If you have some experience setting up GitHub actions already you will probably prefer the flexibility of using the `nbmake` pip package directly.**

## Quick Start

```yaml
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - uses: "treebeardtech/nbmake-action@v0.2"
        with:
          path: "./examples"
          path-output: .
          notebooks: |
            nb1.ipynb
            'sub dir/*.ipynb'
```

See [action.yml](action.yml) for the parameters you can pass to this action, and see [unit tests](.github/workflows/action_unit_test.yml) and [integ tests](.github/workflows/action_integration_test.yml) for example invocations.

## Developing

### Install local package
```
npm install
```

### Run checks and build
```
npm run all
```

## See Also

- [nbmake](https://github.com/treebeardtech/nbmake)
- [jupyter book](https://github.com/executablebooks/jupyter-book)
- [Guide to python dependency management choices](https://towardsdatascience.com/devops-for-data-science-making-your-python-project-reproducible-f55646e110fa)
