# Configuring your project

Note: Whichever form of dependency management you use, you will need to include `treebeard` as a dependency.

Treebeard requires the directory which it is run in to contain:

1. Some type of dependencies file (requirements.txt, Pipfile, or environment.yml)
2. A treebeard.yaml file

An example of a valid project directory is shown below.

Note that it contains a `venv` which we do not want to upload to Treebeard, and a `.env` file containing credentials used by this project.

```
➜ ls -a repo
total 32
-rw-r--r--  1 project_user  staff    13B 12 Mar 15:05 .env
drwxr-xr-x  3 project_user  staff    96B 17 Mar 10:13 .ipynb_checkpoints
drwxr-xr-x  3 project_user  staff    96B 12 Mar 14:13 .vscode
-rw-r--r--  1 project_user  staff    31B 17 Mar 10:08 requirements.txt
-rw-r--r--  1 project_user  staff   1.2K 17 Mar 10:13 run.ipynb
-rw-r--r--  1 project_user  staff   135B 12 Mar 13:38 treebeard.yaml
drwxr-xr-x  6 project_user  staff   192B 12 Mar 14:06 venv
```

```yaml
# treebeard.yaml
notebooks:
  - run.ipynb
ignore:
  - venv
  - .vscode
  - .ipynb_checkpoints
  - "*pyc"
secret:
  - .env
output_dirs:
  - my_output
  - another_output
```

## treebeard.yaml fields

_**notebooks**_ (default: _main.ipynb_)
<br/>
lists patterns of `ipynb` files to be run

_**ignore**_ (default: _[]_)
<br/>
lists files which will are not to be uploaded to treebeard. They will not be available at runtime

_**secret**_ (default: _[]_)
<br/>
lists files which can be stored in Treebeard using `treebeard secrets push` and will then be available at runtime. This may be necessary for Github integration

_**output_dirs**_ (default: _['output']_)
<br/>
list directories where outputs are saved. Outputs will be served via a versioned API by Treebeard

Depending on your use case, you can use a minimal config file e.g.

```yaml
# treebeard.yaml
notebooks:
  - run.ipynb
```

## Advanced Configuration

### Repo2Docker Configuration

Treebeard is built on top of repo2docker, a great open source project which determines how to install your dependencies. If you need custom packages (usually installed via `apt-get install ...` ) then you can supply the config files such as _apt.txt_ which they accept and are listed in their [docs](https://repo2docker.readthedocs.io/en/latest/config_files.html).

### Speeding up builds with postbuild scripts

If you make changes to dependencies, this will cause a full rebuild of the container. To prevent that and obtain faster build times, repo2docker allows [postbuild scripts](https://repo2docker.readthedocs.io/en/latest/config_files.html#postbuild-run-code-after-installing-the-environment). For example by installing a local package in a postbuild script with `pip install -e .`, changes that package on commit would not cause a container rebuild.

### Package managers and build times

We have found for the fastests builds from fastest to slowest: pip (fastest) > pipenv > conda
