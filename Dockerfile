# Python version can be changed, e.g.
# FROM python:3.8
# FROM docker.io/fnndsc/conda:python3.10.2-cuda11.6.0
FROM docker.io/python:3.10.2-slim-buster

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="pl-dypi" \
      org.opencontainers.image.description="A ChRIS ds plugin that can build reactive tree structures"

WORKDIR /usr/local/src/app

RUN apt update &&                   \
    apt install -y vim &&           \
    apt install -y iputils-ping &&  \
    apt install -y net-tools

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["dypi", "--help"]
