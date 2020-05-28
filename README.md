<p align="center"><a href="https://modin.readthedocs.io"><img width=77% alt="Treebeard - continuous integration for data science" src="https://github.com/treebeardtech/treebeard/blob/master/docs/img/treebeard.jpg?raw=true"></a></p>
<h2 align="center">Continuous integration for data science - test your Jupyter notebooks🌲</h2>

<p align="center">
<a href="https://badge.fury.io/py/treebeard"><img src="https://badge.fury.io/py/treebeard.svg" alt="PyPI version"></a>
<a href="https://treebeard.readthedocs.io/"><img src="https://readthedocs.org/projects/treebeard/badge/?version=latest" alt="Docs"> </a>
<img src="https://github.com/treebeardtech/treebeard/workflows/E2E%20Test/badge.svg" alt="E2E Test">
<img src="https://github.com/treebeardtech/treebeard/workflows/Integration%20Test/badge.svg" alt="Integration Test">
<a href="https://gitter.im/treebeardtech/community?utm_source=badge&amp;utm_medium=badge&amp;utm_campaign=pr-badge&amp;utm_content=badge"><img src="https://badges.gitter.im/Join%20Chat.svg" alt="Join the Gitter Chat"></a></p>

## What is Treebeard?

A solution for setting up continuous integration on data science projects requiring minimal configuration.

<p align="center"><img src="https://storage.googleapis.com/treebeard_image_dump_public/github.gif" width="550px" style="margin:'auto'"/></p>

### Functionality:

- Automatically installs dependencies for binder-ready repos (which can use conda, pip, or pipenv)
- Runs notebooks in the repo (using papermill)
- Uploads outputs, providing versioned URLs and nbcoverted output notebooks
- Integrates with repos via a [GitHub App](https://github.com/marketplace/treebeard-build)
- Slack notifications
- A secret store for integrating with existing infrastructure

## What is in this repo?

Our Apache-licensed Python SDK which contains a CLI, buildtime orchestration logic, and runtime code for testing notebooks and uploading outputs.

## More Information

- [GitHub App](https://github.com/marketplace/treebeard-build)
- [Docs](https://treebeard.readthedocs.io/en/latest/)
- [Website](https://treebeard.io)
