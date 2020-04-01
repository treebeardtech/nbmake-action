import setuptools  # type: ignore

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
    "jupyter-client>=6.1.0",  # fix Step #0: ERROR: nbclient 0.2.0 has requirement jupyter-client>=6.1.0, but you'll have jupyter-client 5.3.4 which is incompatible.
]

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("treebeard/version.txt", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="treebeard",
    version=version,
    author="Treebeard Technologies",
    author_email="alex@treebeard.io",
    description="Tools for notebook hosting",
    long_description=long_description,
    long_description_content_type="text/markdown",  # type: ignore
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_data={"treebeard": ["version.txt"]},
    entry_points={
        "console_scripts": [
            "treebeard = treebeard:cli",
            "treebeard-spaceship = treebeard.version:cli",
        ]
    },
    install_requires=install_requires,
)
