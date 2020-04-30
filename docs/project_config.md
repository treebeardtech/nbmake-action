# Configuring your project

## Specify Dependencies

[Binder-ready](https://mybinder.readthedocs.io/en/latest/introduction.html) repos can be run on treebeard without any additional configuration.

## Select Notebooks

By default all notebooks will be run (matching `'**/*.ipynb'`) although you can provide a `treebeard.yaml` to specify your own config.

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

_**kernel_name**_ (default: _['python3']_)
<br/>
The name of the ipykernel which papermill will use for running the notebooks. You can use this setting to run Julia, C++, or any [language listed here](https://github.com/jupyter/jupyter/wiki/Jupyter-kernels).

Note that you will need to install the kernel by including it in a binder-supported dependency file or build script.

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

### Specify Treebeard Version

The python process at runtime needs the [treebeard pypi package](https://pypi.org/project/treebeard/) available at runtime. By default it will be installed after your project is built, but you can install it in your requirements.txt etc. proactively if you need to resolve conflicts.
