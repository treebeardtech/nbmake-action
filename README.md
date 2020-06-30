<p align="center"><a href="https://treebeard.io"><img width=50% alt="Treebeard - continuous integration for data science" src="https://github.com/treebeardtech/treebeard/blob/master/docs/img/treebeard.jpg?raw=true"></a></p>
<h2 align="center">Jupyter notebook continuous integration</h2>

<p align="center">
<a href="https://badge.fury.io/py/treebeard"><img src="https://badge.fury.io/py/treebeard.svg" alt="PyPI version"></a>
<a href="https://treebeard.readthedocs.io/"><img src="https://readthedocs.org/projects/treebeard/badge/?version=latest" alt="Docs"> </a>
<img src="https://github.com/treebeardtech/treebeard/workflows/E2E%20Test/badge.svg" alt="E2E Test">
<img src="https://github.com/treebeardtech/treebeard/workflows/Integration%20Test/badge.svg" alt="Integration Test">
<a href="https://gitter.im/treebeardtech/community?utm_source=badge&amp;utm_medium=badge&amp;utm_campaign=pr-badge&amp;utm_content=badge"><img src="https://badges.gitter.im/Join%20Chat.svg" alt="Join the Gitter Chat"></a></p>

**Note: This GitHub Action is in Pre-release. Drop us an issue or message Alex on [gitter](https://gitter.im/treebeardtech/community) before using as docs are patchy**

## What is Treebeard?

A low-config continuous integration framework for data science teams using Jupyter Notebooks.

Works either through our pypi package or GitHub Actions.

### GitHub Actions Example

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
        env:
          TB_MY_TOKEN: "${{ secrets.MY_TOKEN }}" # 'TB_' prefixed variable are passed to notebook runtime
```

### Output Example
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

## Functionality

- Automatically installs dependencies for binder-ready repos using repo2docker (which can use conda, pip, or pipenv)
- Runs notebooks in the repo (using papermill)
- On failure, flags all imports which cannot be resolved
- Supports notebook build scripts. `treebeard/post_install.ipynb` can manually install dependencies and `treebeard/container_setup.ipynb` can install credential files. 

## Why use this?

This framework is made for teams with lots of data science ability but constrained in terms of devops.

**Testing**: If you are frequently blocked by bugs in Jupyter Notebooks or Python scripts, then setting up treebeard via GitHub actions will provide automated testing to resolve issues faster.

**Automation**: Scheduling notebooks to run is trivial once you have a working dependency file.

## Why not use this?

Experienced Docker users: This project containerises Python repos using repo2docker. It is simple to setup, but is slower to build and results in large images.

## Design Philosophy

**Promote devops culture** We believe good teams have a devops champion, but the best teams have a devops culture. As a result we want to make team infrastructure as similar as possible to team code.

For data science this means treating Jupyter Notebooks as first class citizens. You do not need to write any bash scripts with boilerplate here.

**Help with integration** Tools are most powerful when combined. We aim to strike a balance between being purely open source and readily linking with platforms such as GitHub and Slack.

We are keen to know what you would like treebeard to work with.

## Treebeard Teams

We are a startup and are building a separate product which the library integrates with. Our goal with Teams is to improve the observability of testing/deployment to speed up debugging. Let [laurence](mailto:laurence@treebeard.io) know if you want to try it out.

<p align="center"><img src="https://storage.googleapis.com/treebeard_image_dump_public/github.png" width="550px" style="margin:'auto'"/></p>

## More Information

- [Docs](https://treebeard.readthedocs.io/en/latest/)
- [Website](https://treebeard.io)
- [Medium blog on dependency management](https://towardsdatascience.com/devops-for-data-science-making-your-python-project-reproducible-f55646e110fa)
