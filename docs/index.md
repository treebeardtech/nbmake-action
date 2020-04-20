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
   testing_locally
   on_prem
   faq

.. toctree::
  :caption: Support
  :maxdepth: 2
  :hidden:

  GitHub <https://github.com/treebeardtech/treebeard>

```

# 🌲 Welcome to Treebeard

Treebeard is a library which reproduces Python data science work in the cloud, natively supporting Jupyter Notebooks.

Treebeard allows you to do the following without bash scripts:

- Setup continuous integration for your Github repo, to test notebooks on each push
- Automatically build a project container image
- Fetch outputs from each cloud run using versioned URLs
- See outputs over time in an admin page

The goal is to allow data scientists to set up **continuous integration** with minimal changes to their project.

We recommend quickly getting a project hosted on Github running with the [Github App](https://github.com/marketplace/treebeard-build). Once the Github App is watching your repository, it will build any notebooks in the project (or as specified in `treebeard.yaml`) when a commit is made.

## Configuration

Treebeard expects project dependencies to be listed in a `requirements.txt`, `Pipfile`, or `environment.yml`. The `treebeard` pip package should also be added, once installed for local testing.

Treebeard then expects a `treebeard.yaml` file in the same directory:

```yaml
# example treebeard.yaml
notebooks:
  - run.ipynb
ignore:
  - venv
output_dirs:
  - output
  - plots
secrets:
  - secrets.json
```

Runs can be triggered with `treebeard run`.

We host back-end infrastructure for running your notebook in the cloud, and serving output data.

![](https://treebeard.io/static/slack_integration-ba8ff89332c2e14c928973a841842e5b.png)

## Install Treebeard

Treebeard is available via pip. Please note only Python 3.6 or higher is supported.

```bash
➜ pip --version
pip 20.0.2 from /Users/.../python3.7/site-packages/pip (python 3.7)
```

```bash
➜ pip install -e ./treebeard-lib
```

## Get started

Authenticate your CLI with our backend infrastructure using your email address.

```bash
➜ treebeard configure --email test@example.com
🔑  Config saved in /Users/project_user/.treebeard
```

You will then need to verify your email address.

Clone our git repo to try the examples

```bash
➜ git clone https://github.com/treebeardtech/treebeard.git
```

### Running your first example

```bash
➜ cd treebeard/examples/hello_treebeard
➜ jupyter notebook
...

➜ treebeard run --daily
⠙ 🌲  Compressing repo
  Including main.ipynb
  Including requirements.txt
  Including treebeard.yaml
✨  Run has been accepted! https://treebeard.io/admin/b44c784b10/treebeard_example_2/cf7a1475-6105-42b6-abeb-ba71420c6a55

# get the latest outputs

# what's my API key?
➜ cat ~/.treebeard
[credentials]
treebeard_email = laurence@treebeard.io
treebeard_project_id = xxxxxx
treebeard_api_key = xxxxxxxxx

➜ curl -o my_data.json \
https://api.treebeard.io/b44c784b10/treebeard_example_2/cli-latest/output/my_data.json?api_key=xxxxxxxxxx
{"mydata": "goes_here"}
```

The entry example shows the basic capabilities of the cloud build service.  
The notebook uses some cloud credentials to call an API, saves an image to an output directory, and calls a separate python script.

We recommend working in a python virtual environment. Ensure your python (3.6 or higher) environment has jupyter and treebeard installed, and then start jupyter in the project directory:
`jupyter notebook`

Open `main.ipynb` and check out the examples. When you're ready, return to the command line and instruct treebeard to build the project on the cloud with:
`treebeard run`

### Examples

There are several example projects in the `examples` folder.

The `reddit_tracker` example shows a notebook that calls the Reddit API using saved credentials, extracts the most commonly mentioned names from recent submissions and saves charts showing those common names. This is then run daily, and the images can then be served through a browser extension. [This blog]("https://towardsdatascience.com/how-to-track-sentiment-on-reddit-with-python-and-a-chrome-extension-a623d63e3a1d?gi=90de4fb3934a") goes into more detail.

## Join the community

Stay in touch with us via [Github](https://github.com/treebeardtech/treebeard) and our [email newsletter](https://treebeard.io/contact)

### 3 Minute Overview

<div style="width: 100%; height: 0px; position: relative; padding-bottom: 62.500%;"><iframe src="https://streamable.com/s/37o5e/lsjslt" frameborder="0" width="100%" height="100%" allowfullscreen style="width: 100%; height: 100%; position: absolute;"></iframe>
<br></br></div>
