# 🌲 Treebeard

A Notebook-First Continuous Integration Framework

![Action Integration Test](https://github.com/treebeardtech/treebeard/workflows/Action%20Integration%20Test/badge.svg) ![Teams Integration Test](https://github.com/treebeardtech/treebeard/workflows/Teams%20Integration%20Test/badge.svg) ![Pytest](https://github.com/treebeardtech/treebeard/workflows/Pytest/badge.svg) <a href="https://gitter.im/treebeardtech/community?utm_source=badge&amp;utm_medium=badge&amp;utm_campaign=pr-badge&amp;utm_content=badge"><img src="https://badges.gitter.im/Join%20Chat.svg" alt="Join the Gitter Chat"></a> [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/treebeardtech/treebeard/master?urlpath=lab/tree/tutorial/tutorial.ipynb)

## What Does Treebeard Do?

* <img width=18 src="https://github.githubassets.com/images/modules/site/features/actions-icon-actions.svg"/> Runs on GitHub Actions

* 🐳 Automatically Containerises Repos

* <img width=18 src="https://jupyter.org/favicon.ico"> Executes Notebooks

* <img width=18 src="https://www.python.org/favicon.ico"> Searches for missing imports 

## Why Notebook-First?

Notebooks have gained mass-adoption within exploratory data science due to how readable they are after execution.

This property can make them useful in more general scenarios:
* as entrypoints to larger programs
* for scheduled tasks
* as install scripts (think 'interactive READMEs').

If [Netflix](https://netflixtechblog.com/notebook-innovation-591ee3221233) runs 100K+ jobs per day using notebooks maybe it's not a bad idea :)

## How can Treebeard help me?
1. **Automate Daily reports** Create daily reports from a dataset and publish them ([Quicklooks](https://github.com/Swarm-DISC/Swarm_quicklooks/blob/master/.github/workflows/main.yml))
2. **Test Project Examples** Smoke test example directories for your tool/library ([ThinkBayes](https://github.com/Rabscuttler/ThinkBayes2/runs/869047684?check_suite_focus=true))
3. **Ensure Project Reproducibility** Validate project requirements and build docker images ([PyPSA](https://github.com/treebeardtech/PyPSA/blob/master/.github/workflows/main.yaml))

<p align="center">
  <br>
  <img width=800 src="https://storage.googleapis.com/treebeard_image_dump_public/usecases.png"/>
</p>


# <img width=23 src="https://github.githubassets.com/images/modules/site/features/actions-icon-actions.svg"/>  Getting Started via GitHub Actions
[*What is a Github Action?*](https://github.com/features/actions)

## Minimal Quickstart

**You will need**:
1. Notebook(s) in your repo
2. A requirements.txt or environment.yml containing dependencies (if required)
3. This GitHub Action workflow file:

```yml
# .github/workflows/treebeard.yml
# Run all notebooks on every push and weekly
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
      - uses: treebeardtech/treebeard@v0.1.1
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

## More Treebeard Action Examples


### Run Notebooks In EDA Directory when any branch is pushed 
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
      - uses: treebeardtech/treebeard@v0.1.1   #  <- runs Treebeard
        notebooks: "EDA/*ipynb"
```

**Additional variables**  
See syntax for more complex triggers [here](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)  

This example makes use of Github [Secrets](https://docs.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets), which are then made available to the Action.  
*Prefix secrets with `TB_` if they are required inside the container for notebooks and scripts to use*
```yaml
# .github/workflows/additional_variables.yaml
on:
  push:                                                                #  <- every time code is committed
  schedule:                                                            #  <- and
    - cron: "0 0 * * 0"                                                #  <- on any schedule you like
jobs:
  run:
    runs-on: ubuntu-latest
    name: Run treebeard
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - uses: treebeardtech/treebeard@v0.1.1
        with:
          api-key: "${{ secrets.TREEBEARD_API_KEY }}"                    #  <- connect to Treebeard Teams 
          docker-username: "treebeardtech"                               #  <- dockerhub username
          docker-password: "${{ secrets.DOCKER_PASSWORD }}"            #  <- so image is saved in dockerhub
          docker-image-name: "treebeardtech/example_image"             #  <- for faster builds
        env:
          TB_MY_TOKEN: "${{ secrets.MY_TOKEN }}"                       #  <- secret available inside image 
```

**Connecting to other services**  
In this workflow, the runtime environment connects to Google Cloud Platform. This allows notebooks and scripts to authenticate with GCP. Note that credentials would not be passed into the docker image - so it is not used - the `use-docker` flag is set to false and dependencies are installed manually.

```yaml
# .github/workflows/connect_to_services.yaml
on: push
jobs:
  run:
    runs-on: ubuntu-latest
    name: Run treebeard
    steps:
      - uses: GoogleCloudPlatform/github-actions/setup-gcloud@master
        with:
          project_id: "${{ secrets.GCP_PROJECT_ID }}"
          service_account_key: "${{ secrets.GCP_SA_KEY }}"
          export_default_credentials: true
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt # Manually install python deps as running dockerless
      - uses: treebeardtech/treebeard@v0.1.1
        with:
          api-key: "${{ secrets.TREEBEARD_API_KEY }}"
          use-docker: false
```

You can have multiple actions defined in `.yaml` files in your workflows folder.

# Treebeard Action API reference

These optional variables can be specified for the Treebeard Action using `with:` as in the examples above. The full Action specification can be seen [here](https://github.com/treebeardtech/treebeard/blob/master/action.yml)  
Automatically generated docker images can be sent to a dockerhub container registry to speed up future builds, if the `docker-` variables are set.  

| Action input                | example                          | definition                                                                                               |
|-----------------------------|------------------------------------------------------------|------------------------------------------------------------------------------------|
| `notebooks`                | `"my_notebook_to_run.ipynb"` | Filenames of Jupyter notebooks to run\. By default a glob pattern will be used (`**/*ipynb`)    |
| `docker-username`         | `"treebeardtech"`        | Dockerhub username                                                                                       |
| `docker-password`         | `"${{ secrets.DOCKER_PASSWORD }}"`        | Dockerhub password                                                                                       |
| `docker-image-name`      | `"project_docker_image"`            | the name of the image built by treebeard                                                                 |
| `docker-registry-prefix` | `"my_docker_image_prefix-"`        | the prefix of your docker image name use instead of docker\-image\-name to generate a default image name |
| `use-docker`              | `true`                             | Run treebeard inside repo2docker \- disable building a docker image with this flag \- on by default      |
| `debug`                    | `false`                            | Enable debug logging                                                                                     |
| `path`                     | `"examples/notebooks/"`            | Path of the repo to run from                                                                             |
| `api-key`                 | `"${{ secrets.TREEBEARD_API_KEY }}"`                   | treebeard teams api key                                                                                  |

# FAQ
 ## 🐳 Should I `use-docker` or not?

By default, Treebeard will use repo2docker to containerise the repo before running the notebooks inside the container.

This is great for simplicity and binder-compatibility but more advanced users may prefer to bypass containerisation because
1. You prefer to install dependencies yourself (could be as simple as `pip install -r requirements.txt`)
2. You would like to use GitHub Actions to integrate with GCP, AWS etc without having to pass credentials into a container
3. You would like to use windows. Repo2docker builds Ubuntu images.

## How do I pass secrets/variables into the runtime container?

Any variable beginning with `TB_` will be forwarded into the container at runtime.

## How do I install dependencies that don't work in an `environment.yml`?

By default, repo2docker installs your conda, pipenv, or pip requirements based on files on your repo. It also supports [several other config files]().

# 🙌  Contributing

The most valuable contribution to us is feedback and issues raised via Gitter or Issues.

If you want to hack on the internal treebeard Python package then we encourage you to jump into our interactive tutorial:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/treebeardtech/treebeard/master?urlpath=lab/tree/tutorial/tutorial.ipynb)

chat with us if you want to make changes, we are here to help!

# <img width=30 src="https://treebeard.io/static/logo-f65d0b1f4c26063572398ee1da01edd7.png"></src> Treebeard Viewer

The great thing about notebooks is they provide a readable record of what happened.

We've built a backend for viewing executed notebooks and their artifacts. It's completely free for open source usage.
    
If you are thinking of setting up a more organised CI layer for your notebooks, [let us know](https://laurencewatson.typeform.com/to/Bgj6hp).

<p align="center"><img src="https://storage.googleapis.com/treebeard_image_dump_public/ui.gif" width="600" style="margin:'auto'"/></p>

## More Information

- [Website](https://treebeard.io)
- [Guide to python dependency management choices](https://towardsdatascience.com/devops-for-data-science-making-your-python-project-reproducible-f55646e110fa)
