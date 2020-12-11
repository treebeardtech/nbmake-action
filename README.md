# nbmake-action

GitHub Action for testing notebooks
(repo renamed from 'treebeard').

## Functionality

Tests notebooks using [nbmake](https://github.com/treebeardtech/nbmake) via pytest.

## Quick Start

```yaml
      - uses: "treebeardtech/nbmake-action@v0.2"
        with:
          path: "./examples"
          html: true
          notebooks: |
            nb1.ipynb
            'sub dir/*.ipynb'
```

See [action.yml](action.yml) for the parameters you can pass to this action, and see [unit tests](.github/workflows/action_unit_test.yml) and [integ tests](.github/workflows/action_integration_test.yml) for example invocations.

## Uploading Test Reports

Any static site hosting platform will work, e.g. S3, Firebase, Netlify.

[Docs on using netlify](https://treebeardtech.github.io/nbmake/landing-page.html#run-and-upload-report-on-github-actions-using-netlify)

### HTML Report Example

![HTML Report](docs/screen.png)

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
