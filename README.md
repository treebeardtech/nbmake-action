# Welcome to Treebeard 🌲

[![PyPI version](https://badge.fury.io/py/treebeard.svg)](https://badge.fury.io/py/treebeard)
[![Docs](https://readthedocs.org/projects/treebeard/badge/?version=latest)](https://treebeard.readthedocs.io/)
[![Treebeard build](https://api.treebeard.io/63db2b28e1/treebeard/latest/buildbadge)](https://treebeard.io/admin/63db2b28e1/treebeard/latest "Latest notebook run")
![E2E Test](https://github.com/treebeardtech/treebeard/workflows/E2E%20Test/badge.svg)
![Integration Test](https://github.com/treebeardtech/treebeard/workflows/Integration%20Test/badge.svg)
[![Join the Gitter Chat](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/treebeardtech/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## What is Treebeard?

A solution for setting up continuous integration on data science projects requiring minimal configuration.

<span style="display:block;text-align:center">
<img src="https://storage.googleapis.com/treebeard_image_dump_public/github.gif" width="550px" style="margin:'auto'"/></span>

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
