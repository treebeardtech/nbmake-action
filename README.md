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

* **Simple:** Easy to set up a powerful testing loop, with straightforward but powerful configuration options.  

* **Jupyter integration:** Just works with your notebooks   

* **Fast feedback:** Catch errors quickly by testing your whole project, and easily create integration tests  for your entire workflow   

* **Flexible:** Use as a Github Action, or create your own workflows with the CLI tool   

* **Containers:** Creates docker images from your dependencies file for you, for reproducibility and deployment 

### Quick start (GitHub Actions)

```yml
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

## Installation
**Requirements**
Python 3.5+

### Install the CLI from pypi
<div class="termy">

```console
$ pip install treebeard
```

</div>

Treebeard makes substantial use of two great libraries:
- [repo2docker](https://github.com/jupyter/repo2docker) to create containers from dependency files, which powers [binder](http://mybinder.org/) 
- [papermill](https://github.com/nteract/papermill) to execute notebooks

### Use as a Github Action
[*What is a Github Action?*](https://github.com/features/actions)

**Simple example Action**   
Commit the following snippet in `.github/workflows/test.yaml` in your repo to enable the action.  
```yaml
# .github/workflows/simple_example.yaml        #  <- location of the yaml file in your project  
on: push                                       #  <- define when the Action will run
jobs:
  run:
    runs-on: ubuntu-latest                     #  <- can be linux, windows, macos
    name: Run treebeard                        #  <- name your job (there can be multiple)
    steps:
      - uses: actions/checkout@v2              #  <- gets your repo code
      - uses: actions/setup-python@v2          #  <- installs python
      - uses: treebeardtech/treebeard@master   #  <- runs Treebeard
```

**Complex example Action**  
See syntax for more complex triggers [here](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)  

This example makes use of Github [Secrets](https://docs.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets), which are then made available to the Action.  
*Prefix secrets with `TB_` if they are required inside the container for notebooks and scripts to use*
```yaml
# .github/workflows/complex_example.yaml
on:
  push:                                                                #  <- every time code is committed
  schedule:                                                            #  <- and
    - cron: "0 0 * * 0"                                                #  <- on any schedule you like
jobs:
  run:
    runs-on: ubuntu-latest
    name: Run treebeard
    steps:
      - uses: GoogleCloudPlatform/github-actions/setup-gcloud@master   #  <- connect to Google Cloud account
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}                    #  <- set credentials in ssecrets
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          export_default_credentials: true
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - uses: treebeardtech/treebeard@master
        with:
          api-key: ${{ secrets.TREEBEARD_API_KEY }}                    #  <- connect to Treebeard Teams 
          docker-username: treebeardtech                               #  <- dockerhub username
          docker-password: "${{ secrets.DOCKER_PASSWORD }}"            #  <- so image is saved in dockerhub
          docker-image-name: "treebeardtech/example_image"             #  <- for faster builds
        env:
          TB_MY_TOKEN: "${{ secrets.MY_TOKEN }}"                       #  <- secret available inside image 
```

You can have multiple actions defined in `.yaml` files in your workflows folder.

### Actions API reference

These optional variables can be specified for the Treebeard Action using `with:` as in the examples above. The full Action specification can be seen [here](https://github.com/treebeardtech/treebeard/blob/master/action.yml)  
Automatically generated docker images can be sent to a dockerhub container registry to speed up future builds, if the `docker-` variables are set.  

| Action input                | example                          | definition                                                                                               |
|-----------------------------|----------------------------------|----------------------------------------------------------------------------------------------------------|
| `notebooks`                | `<'my_notebook_to_run.ipynb'>` | Filenames of Jupyter notebooks to run\. By default a glob pattern will be used (`**/*ipynb`)    |
| `docker-username`         | `<my_dockerhub_username>`        | Dockerhub username                                                                                       |
| `docker-password`         | `<my_dockerhub_password>`        | Dockerhub password                                                                                       |
| `docker-image-name`      | `<docker_image_name>`            | the name of the image built by treebeard                                                                 |
| `docker-registry-prefix` | `<docker_image_prefix- >`        | the prefix of your docker image name use instead of docker\-image\-name to generate a default image name |
| `use-docker`              | `true`                             | Run treebeard inside repo2docker \- disable building a docker image with this flag \- on by default      |
| `debug`                    | `false`                            | Enable debug logging                                                                                     |
| `path`                     | `<'path/to/run_from'>`            | Path of the repo to run from                                                                             |
| `api-key`                 | `<my_api_key>`                   | treebeard teams api key                                                                                  |


## Treebeard Teams

For even greater observability of testing and deployment to speed up debugging, you could build out your own solution or try our Treebeard Teams platform.  

Integrating naturally with this library, the Teams platform serves all notebook outputs and artifacts from a run. This improves collaboration, debugging and deployment, especially for complex projects.
    
If you're considering implementing a new CI layer for your data science team, [get in touch](https://laurencewatson.typeform.com/to/Bgj6hp).

<p align="center"><img src="https://storage.googleapis.com/treebeard_image_dump_public/github.png" width="800px" style="margin:'auto'"/></p>

## More Information

- [Docs](https://treebeard.readthedocs.io/en/latest/)
- [Website](https://treebeard.io)
- [Guide to python dependency management choices](https://towardsdatascience.com/devops-for-data-science-making-your-python-project-reproducible-f55646e110fa)
