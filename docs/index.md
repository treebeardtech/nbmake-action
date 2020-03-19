```eval_rst
.. toctree::
   :caption: Documentation
   :maxdepth: 2
   :hidden:

   Home <https://treebeard.readthedocs.io/>
   project_config
   running
   outputs
   external_integrations
   integrate_your_infra
   cli
   on_prem
   faq

.. toctree::
  :caption: Support
  :maxdepth: 2
  :hidden:

  GitHub <https://github.com/treebeardtech/treebeard>

```

# 🌲 Welcome to Treebeard

Treebeard is an open source library which reproduces Python data science work in the cloud, natively supporting Jupyter Notebooks.

The goal is to allow data scientists to set up continuous integration with minimal changes to their project.

Treebeard works by adding the `treebeard` pip package to your `requirements.txt`, `Pipfile`, or `environment.yml`.

Then placing a `treebeard.yaml` file in the same directory like so:

```yaml
# treebeard.yaml
notebook: run.ipynb
ignore:
  - venv
```

then running `treebeard run`.

We host back-end infrastructure for running your notebook in the cloud, and serving output data.

![Treebeard Admin Page Screenshot](https://treebeard.io/static/slack_integration-ba8ff89332c2e14c928973a841842e5b.png)

## Install Treebeard

Treebeard is available via pip. Please note only Python 3 is supported.

```bash
➜ pip --version
pip 20.0.2 from /Users/.../python3.7/site-packages/pip (python 3.7)
```

```bash
➜ pip install treebeard
```

## Get started

Authenticate your CLI with our backend infrastructure using an API key. If we have not given you one, contact [alex@treebeard.io](mailto:alex@treebeard.io).

```bash
➜ treebeard configure --email test@example.com --key xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
🔑  Config saved in /Users/project_user/.treebeard
```

You will then need to verify your email address.

Clone our git repo to try the examples

```bash
➜ git clone https://github.com/treebeardtech/treebeard.git
TODO cd examples, run, admin page, pull down file
```

## Join the community

Stay in touch with us via [Github](https://github.com/treebeardtech/treebeard) and our [email newsletter](https://treebeard.io/contact)
