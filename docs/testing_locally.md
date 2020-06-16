# Testing locally

You may want to run the Treebeard build and run client locally, for example to troubleshoot a failing build.

To do so, there are two flags for the `treebeard` CLI for this purpose: `` and `--dockerless`.

`treebeard run --dockerless` will run your project locally without [docker](https://www.docker.com/) using your local kernel

`treebeard run` expects a **docker** instance to be running on your machine, and builds an image based on your project requirements files using **repo2docker**.
