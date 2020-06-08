import setuptools  # type: ignore

"""
Treebeard - CLI and Github app for running notebooks
====================================================

Check out [GitHub](https://github.com/treebeardtech/treebeard) to find out more.
"""

install_requires = [
    "click",
    "halo",
    "papermill",
    "jupyter-repo2docker",
    "colorama",
    "ipykernel",
    "pathlib",
    "timeago",
    "humanfriendly",
    "sentry-sdk",
    "pyyaml",
    "pydantic",
    "docker",
    "python-magic",
    "nbstripout",
    "docker",
    "requests",
    "jupyter-client>=6.1.0",  # fix Step #0: ERROR: nbclient 0.2.0 has requirement jupyter-client>=6.1.0, but you'll have jupyter-client 5.3.4 which is incompatible.
    "jupyter-contrib-nbextensions",  # for nbconvert scriptexporter
]

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("treebeard/version.txt", "r") as fh:
    version = fh.read()

setuptools.setup(  # type: ignore
    name="treebeard",
    version=version,
    author="Treebeard Technologies",
    author_email="alex@treebeard.io",
    description="Run and schedule jupyter notebook projects in the cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",  # type: ignore
    packages=setuptools.find_namespace_packages(),  # type: ignore
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license="Apache-2.0",
    python_requires=">=3.6",
    package_data={"treebeard": ["version.txt", "example_treebeard.yaml"]},
    entry_points={
        "console_scripts": [
            "treebeard = treebeard:cli",
            "treebeard-spaceship = treebeard.version:cli",
        ]
    },
    install_requires=install_requires,
    url="https://github.com/treebeardtech/treebeard",
)
