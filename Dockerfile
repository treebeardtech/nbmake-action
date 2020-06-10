FROM python:3.7

RUN apt-get update && apt-get install -y docker.io
COPY ./treebeard-lib ./treebeard-lib
RUN pip install ./treebeard-lib

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]