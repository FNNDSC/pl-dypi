# _ChRIS_ Dynamic Pipeline 

<!--
[![Version](https://img.shields.io/docker/v/fnndsc/pl-dypi?sort=semver)](https://hub.docker.com/r/fnndsc/pl-dypi)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-dypi)](https://github.com/FNNDSC/pl-dypi/blob/main/LICENSE)
[![Build](https://github.com/FNNDSC/pl-dypi/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-dypi/actions)
-->

## Abstract

Creating trees of compute that are conditional to some characteristic of the data being computed can be hard to create _a priori_ and are often more easily/efficiently handled on a case-by-case basis. In some ways, this problem relates to strategies of static and dynamic structure in design patterning. While some behavior can be determined from a static analysis of the larger compute logic, this can result in complex overgeneralization as all possible compute paths might need to be considered -- imagine a tree that enumerates all possible branches from all possible data components. Even the apparently simpler problem of expressing logic such as "at this node generate _N_ parallel branches conditional to this _paramater_" and then explicitly compiling/generating the resultant _explicit_ static tree can become complex -- this requires developing a syntax for describing tree logic and then coding a compiler that can understand this syntax.

Based on this insight, perhaps a simpler approach is just to develop a program (or a class of programs) that can analyze the input space and at run/execute time determine the resulting branching structure. In other words, perhaps easiest to resolve the tree _dynamically_ in a programmatic fashion. Codify the logic itself as a program. 

Examples of this problem in the context of ChRIS include cases where some (usually) input node contains a collection of objects (files, directories, etc) and some object-specific compute is required for each object (or some subset of objects) to be performed in parallel by pre-existing plugins or _pipelines_ of plugins.

Consider a trivial case of an input collection that contains data on many subjects -- say brain MRI data on subjects of varying age. Suppose we wish to run a specific set of analysis on each subject, and moreover each analysis itself is contigent upon some characteristic of each subject data (for example, imagine the subject age is parameter itself for the subsequent analysis to perform) or even imagine if some data, based on its type, requires type-specific preprocessing before performing some common analysis.

One mechanism to determine what logic to perform on a per-object case is directly in the context of the object space itself. In the ChRIS ecosystem, this could mean a plugin that loops over input objects and performs some _system level_ response. By _system level_ is meant that the plugin's _operation_ is not to perform some computation, but rather to schedule some pre-exsiting analysis with ChRIS on each subset of the input.

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