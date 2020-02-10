# Hello Treebeard!

Treebeard allows simple cloud deployment for jupyter notebooks.
Treebeard deploys your notebook to a cloud server, builds an image and runs on a schedule you define. Tagged outputs (artifacts) from the notebook are made available for download via an API. Every notebook run, build log and notebook output is stored and made accessible.

## Why?

The main benefits are:

1. **Automatic containerisation** -- just provide a notebook and requirements.txt/pipfile/environment.yml
2. **Simple scheduling and logging** -- every time the notebook runs you can view the output notebook as html
3. **Output artifact management** -- saved files are stored and served via an API to simplify consumption in a web front end or other applications

## Getting started

The treebeard command line interface expects a single notebook (for now) called `main.ipynb` and a requirements file.

1. Clone this repository and install requirements into your python environment, for example using pip or pipenv:

```
git clone https://github.com/treebeardtech/hello_treebeard.git && cd hello_treebeard
pip install -r requirements.txt
```

3. _Optionally_ - run and edit the example notebook

4) Set up treebeard ([contact us for an API key](mailto:laurence@treebeard.io?subject=I%20would%20like%20an%20API%20key))

```
treebeard configure
```

5. Deploy your notebook to our cloud and run on a schedule

```
treebeard run --daily
```

6. Outputs will shortly appear on the admin page at the link given by the CLI

### Outputs

Notebooks are rendered as HTML, they are not interactive.  
Output notebooks are available at `https://treebeard.io/admin/<project_id>/<notebook>/<run_id>/`  
Notebook artifacts are available from links under Saved Items on the admin page.  
The artifact URL pattern is`https://URL/<project_id>/<notebook>/<run_id>/artifacts/filename`
