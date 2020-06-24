<p align="center"><a href="https://treebeard.io"><img width=50% alt="Treebeard - continuous integration for data science" src="https://github.com/treebeardtech/treebeard/blob/master/docs/img/treebeard.jpg?raw=true"></a></p>
<h2 align="center">Devops for data science</h2>

<p align="center">
<a href="https://badge.fury.io/py/treebeard"><img src="https://badge.fury.io/py/treebeard.svg" alt="PyPI version"></a>
<a href="https://treebeard.readthedocs.io/"><img src="https://readthedocs.org/projects/treebeard/badge/?version=latest" alt="Docs"> </a>
<img src="https://github.com/treebeardtech/treebeard/workflows/E2E%20Test/badge.svg" alt="E2E Test">
<img src="https://github.com/treebeardtech/treebeard/workflows/Integration%20Test/badge.svg" alt="Integration Test">
<a href="https://gitter.im/treebeardtech/community?utm_source=badge&amp;utm_medium=badge&amp;utm_campaign=pr-badge&amp;utm_content=badge"><img src="https://badges.gitter.im/Join%20Chat.svg" alt="Join the Gitter Chat"></a></p>

**Note: This GitHub Action is in Pre-release. Drop us an issue or email [Alex](mailto:alex@treebeard.io) before using.**

## What is Treebeard?

A continuous integration framework for data science teams using Jupyter Notebooks.

Works either through our pypi package or GitHub Actions.

```
# .github/workflows/test.yml
on:
  push:
  schedule:
    - cron: "0 0 * * 0" # weekly
jobs:
  run:
    runs-on: ubuntu-latest
    name: Run treebeard
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - uses: treebeardtech/treebeard@master
```

```
🟩🟩🟩🟩🟩🟩🟩🟩🟩✅ module/GUI/Initialise project.ipynb
  ran 11 of 11 cells

🟩🟩🟩🟩🟩🟩🟩🟩🟩✅ module/GUI/Map.ipynb
  ran 27 of 27 cells

🟩🟩💥⬜⬜⬜⬜⬜⬜⬜ module/GUI/Settings management.ipynb
  ran 6 of 29 cells
  💥 FileNotFoundError: [Errno 2] No such file or directory: '../validation_schema.json'

🟩🟩🟩🟩🟩🟩🟩🟩🟩✅ module/GUI/Wind Farm Layout Optimisation.ipynb
  ran 39 of 39 cells

❗📦 You *may* be missing project requirements, the following modules are imported from your notebooks but can't be imported from your project root directory
  - bs4
  - folium
  - geopandas
  - ipypb
  - matplotlib

Notebooks: 11 of 22 passed (50%)
Cells: 291 of 587 passed (49%)
```

### Functionality:

- Automatically installs dependencies for binder-ready repos using repo2docker (which can use conda, pip, or pipenv)
- Runs notebooks in the repo (using papermill)
- On failure, flags all imports which cannot be resolved


### Treebeard Teams

We are a startup and are building a separate product which the library integrates with. Our goal with Teams is to improve the observability of testing/deployment to speed up debugging. Let [laurence](mailto:laurence@treebeard.io) know if you want to try it out.

<p align="center"><img src="https://storage.googleapis.com/treebeard_image_dump_public/github.png" width="550px" style="margin:'auto'"/></p>

## More Information

- [GitHub App](https://github.com/marketplace/treebeard-build)
- [Docs](https://treebeard.readthedocs.io/en/latest/)
- [Website](https://treebeard.io)
