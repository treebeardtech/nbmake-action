FROM python:3.7

RUN apt-get update && apt-get install -y docker.io

COPY . .

RUN pip install -e ./treebeard-lib