# _ChRIS_ Dynamic Pipeline 

<!--
[![Version](https://img.shields.io/docker/v/fnndsc/pl-dypi?sort=semver)](https://hub.docker.com/r/fnndsc/pl-dypi)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-dypi)](https://github.com/FNNDSC/pl-dypi/blob/main/LICENSE)
[![Build](https://github.com/FNNDSC/pl-dypi/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-dypi/actions)
-->

## Abstract

Creating trees of compute that are conditional to some characteristic of the data being computed can be hard to create _a priori_ and are often more easily/efficiently handled on a case-by-case basis. In some ways, this problem relates to strategies of static and dynamic structure in design patterning. While some behavior can be determined from a static analysis of some data space, true responsiveness to a problem can sometimes best be done dynamically. 

Examples of this problem in the context of ChRIS include cases where some (usually) input node contains a collection of objects (files, directories, etc) and some object-specific compute is required for each object (or some subset of objects) to be performed in parallel by pre-existing pipelines of plugins.

Consider a trivial case of an input collection that contains data on many subjects -- say brain MRI data on subjects of varying age. Suppose we wish to run a specific set of analysis on each subject, and moreover each analysis itself is contigent upon some characteristic of each subject data (for example, imagine the subject age is parameter itself for the subsequent analysis to perform) or even imagine if some data, based on its type, requires type-specific preprocessing before performing some common analysis.

One mechanism to determine what logic to perform on a per-object case is directly in the context of the object space itself. In the ChRIS ecosystem, this could mean a plugin that loops over input objects and performs some _system level_ response. By _system level_ is meant that the plugins _operation_ is not to perform some computation, but rather to tell ChRIS to run some ChRIS activity within the ChRIS data space on the object.

This plugin, _pl-dypi_ is an initial exploration of this idea.

## What this plugin demonstrates

To keep things simple, the _pl-dypi_ operates with two core parameters:

* A regex that when applied over its input space can filter objects (for ex. a file blob like `*.mgz`)
* A string that specifies a _pipeline_ on the ChRIS/CUBE instance on which this plugin is being executed.

## Usage

```shell
singularity exec docker://fnndsc/pl-dypi dypi [--args values...] input/ output/
```

## Examples

```shell
mkdir incoming/ outgoing/
mv some.dat other.dat incoming/
singularity exec docker://fnndsc/pl-dypi:latest dypi [--args] incoming/ outgoing/
```

## Development

### Building

```shell
docker build -t localhost/fnndsc/pl-dypi .
```

### Get JSON Representation

```shell
docker run --rm localhost/fnndsc/pl-dypi chris_plugin_info > MyProgram.json
```

### Local Test Run

Run latest versions of code without rebuilding the docker image:

```shell
docker run --rm -it --userns=host -u $(id -u):$(id -g) \
    -v $PWD/app.py:/usr/local/lib/python3.10/site-packages/app.py:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-dypi dypi /incoming /outgoing
```

Run latest versions of code without rebuilding the docker image suitable for debugging (running as non-root causes issues with `pudb`): 

```shell
docker run --rm -it --userns=host  \
    -v $PWD/app.py:/usr/local/lib/python3.10/site-packages/app.py:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-dypi dypi /incoming /outgoing
```

_-30-_