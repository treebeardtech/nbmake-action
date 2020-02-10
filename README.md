# Hello Treebeard!

Treebeard allows very simple cloud deployment of jupyter notebooks from the command line. It expects a single notebook (for now) called `main.ipynb` and a requirements file. It sends your notebook to a cloud server, builds an image for it, and runs on a schedule you define. Tagged outputs (artifacts) from the notebook are made available for download.

Everything is immutable. Every notebook run, build log and notebook output is stored and made accessible.

## Getting started

1. Clone this repository and install requirements into your python environment, for example using pip or pipenv:

```
git clone https://github.com/treebeardtech/hello_treebeard.git && cd hello_treebeard
pip install -r requirements.txt
```

3. _Optionally_ - run and edit the example notebook

```
jupyter notebook
```

4. Set up treebeard ([contact us for an API key](mailto:laurence@treebeard.io?subject=I%20would%20like%20an%20API%20key))

```
treebeard configure
```

5. Schedule your notebook run

```
treebeard run --daily
```

6. Outputs will shortly appear on the admin page at the link given by the CLI

### Outputs

Notebooks are rendered as HTML, they are not interactive.  
Output notebooks are available at `https://treebeard.io/admin/<project_id>/<notebook>/<run_id>/`  
Notebook artifacts are available from links under Saved Items on the admin page.  
The artifact URL pattern is`https://URL/<project_id>/<notebook>/<run_id>/artifacts/filename`
