FROM python:3.7

RUN apt-get update && apt-get install -y docker.io
RUN mkdir /treebeard-lib
COPY . /treebeard-lib

RUN pip install -e /treebeard-lib