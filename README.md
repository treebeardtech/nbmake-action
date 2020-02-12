# Hello Treebeard!

![Run on Treebeard](https://github.com/treebeardtech/hello_treebeard/workflows/Run%20on%20Treebeard/badge.svg?event=push)

Treebeard allows simple cloud deployment for jupyter notebooks.

Treebeard deploys your notebook to a cloud server, builds an image and runs on a schedule you define.  
Tagged output (artifacts) from the notebook are made available for download via an API.  
Every notebook run, build log and notebook output is stored and made accessible.

## Why?

The main benefits are:

1. **Automatic containerisation** -- just provide a notebook and requirements.txt/pipfile/environment.yml
2. **Simple scheduling and logging** -- every time the notebook runs you can view the output notebook as html
3. **Output artifact management** -- saved files are stored and served via an API to simplify consumption in a web front end or other applications

## Getting started

We recommend working in a virtual python environment - see below for steps to do this.  
Treebeard requires some kind of dependency file at the project root - `requirements.txt`, `Pipfile`, or `environment.yml` - to complete the cloud build.

### Deploying notebooks

The treebeard command line interface expects a single notebook (for now) called `main.ipynb` and a requirements file.

1. Clone this repository and install requirements into your python virtual environment, for example using pip or pipenv:

```
git clone https://github.com/treebeardtech/hello_treebeard.git && cd hello_treebeard
pip install -r requirements.txt
```

3. _Optionally_ - run and edit the example notebook. Any output that should be available on the cloud should be saved in a directory named `output`.

4) Set up treebeard ([contact us for an API key](mailto:laurence@treebeard.io?subject=I%20would%20like%20an%20API%20key))

```
treebeard configure
```

5. Deploy your notebook to our cloud and run on a schedule

```
treebeard run --daily
```

6. Outputs (anything saved in the `output` directory) will shortly appear on the admin page at the link given by the CLI

### Viewing deployments

From step 6, if the run job is accepted, `treebeard` will create a link to an admin dashboard where a html version of the notebook will be created from the cloud run.  
The current build status, build logs and any output artifacts can be found on this page.

Example admin view:
![admin view](https://storage.googleapis.com/treebeard_image_dump_public/admin_view.png "Admin view")

### Checking historical jobs

`treebeard status` will show all historical notebook runs.

### Output

Notebooks are rendered as HTML, they are not interactive.  
Output notebooks are available at `https://treebeard.io/admin/<project_id>/<notebook>/<run_id>/`  
Notebook artifacts are available from links under Saved Items on the admin page.  
The artifact URL pattern is`https://URL/<project_id>/<notebook>/<run_id>/artifacts/filename`

### Options and arguments

If you have a virtual environment folder in the directory, you should ignore it, using `--ignore <my_env_directory>`.

### Setup a virtual environment

Using a virtual environment is good practice to ensure project dependencies don't affect each other, and to avoid installing everything as modules with the system python.

We like `pipenv` for managing virtual environments. Check [this guide](https://realpython.com/pipenv-guide/#pipenv-introduction), follow these steps, or do your own thing:

```
pip install pipenv
pipenv shell
pipenv install -r requirements
```

This will create a `Pipfile` which will list the project dependencies.  
But now there is requirements.txt and a Pipfile... so go ahead and delete the requirements.txt file as it is no longer needed.

If you want to install more dependencies, you can do it on the command line in the pipenv shell, or in a notebook created from the pipenv shell. The command in a jupyter cell is `!pipenv install <my requirement>`, the `!` allows execution of shell commands.

**_As long as there is some kind of dependency file at the project root - requirements.txt, Pipfile, or environment.yml - treebeard can complete the cloud build_**
