# _ChRIS_ Dynamic Pipeline 

<!--
[![Version](https://img.shields.io/docker/v/fnndsc/pl-dypi?sort=semver)](https://hub.docker.com/r/fnndsc/pl-dypi)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-dypi)](https://github.com/FNNDSC/pl-dypi/blob/main/LICENSE)
[![Build](https://github.com/FNNDSC/pl-dypi/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-dypi/actions)
-->

## Abstract

``pl-dypi`` or **DY**namic **PI**peline is an experiment in exploring the utility of using ChRIS DS plugins to self-adapt the toplogical structure of a workflow to data _as it is being computed_. While it can be argued that the use case being demonstrated here _could_ be created without this plugin, it is not too difficult to imagine cases where this is simply not possible.

## Musings

### The problem of self-adaptive compute toplogies

In the majority of data analytic cases, a set of operations to apply on data can be fully described _a priori_. In a multistage workflow, where one stage "feeds" into another downstream component, the stages to use are usually fixed. Such a "pipeline" is a static structure, and usually the only variable is the data entering the "pipeline" at its origin.

On the other hand, certain problems can be best modeled by a _dynamic_ class of operations - conditionals, loops, etc, where the actual step to apply at any given stage in a workflow depends on some detail of upstream results. This could be _splitting_ downstream processing into multiple parallel explicit branches, deciding which inputs are worthy of further processing, choosing different compute directions depending on data as it is analyzed, etc.

Clearly, creating trees of compute that are a function of some emergent characteristic of the data being computed can be hard to create _a priori_ but could be extremely useful in automating many workflows.

### What might that look like in ChRIS?

Examples of this problem in the context of ChRIS include cases where some (usually) input node contains a collection of objects (files, directories, etc) and some object-specific compute is required for each object (or some subset of objects) to be performed in parallel by pre-existing plugins or _pipelines_ of plugins.

Consider a trivial case of an input collection that contains data on many subjects -- say brain MRI data on subjects of varying age. Suppose we wish to run a specific set of analysis on each subject, and moreover each analysis itself is contigent upon some characteristic of each subject data (for example, imagine the subject age needs to be parameterized in the subsequent analysis to perform but this parameter is only available at run time) or even imagine if some data, based on its type, requires type-specific preprocessing before performing some common analysis.

While it _is_ possible in the current baseline ChRIS to roll out all the above requirements into separate actual Feeds, it can be tedious. Consider the case where some input data set contains mixed formats (DICOM and NIfTI) and some downstream processing requires NIfTI input only -- this would require additional (reasonable) preprocessing by the user to first separate out all the DICOMs and convert to NIfTI and _then_ reconstitute a new homogenous input set. If it were possible to have even that be handled in the context of a single analysis, automation becomes simpler, portable, and trackable, and all contained neatly in a ChRIS Analysis Feed.

Currently, _within ChRIS_ a user would have to create separate uploaded analyses for one set of inputs, perform prepocessing, and then collect together the results of that preprocessing together with non-preprocessed inputs into a new Analysis/Feed. In the cases of requiring many parallel branches of plugin compute off some core data, a user could in theory create a separate Feed manually for _each_ branch. While _possible_ this would certainly be tedious and certainly not scalable. There is a strong use case for having a single analysis explicitly automate _all_ operations on some input set.

### External clients have the source!

One approach to address such trees is to codify the structure _programmatically_ and handle the tree construction at run time according to the nature of the problem to solve. In the ChRIS context, this could mean a completely client-side or external program that is coded to idiomatically and adaptively builds a specific set of workflows, say a shell script that POSTs data, runs a plugin, pulls results, and makes decisions on what plugin to use next based on this analysis. Examples of such workflow scripts have been developed [here](https://github.com/FNNDSC/CHRIS_docs/tree/master/workflows).

While this provides a powerful mechanism to execute advanced compute workflows in ChRIS, there are some undesirable side effects -- mostly the very fact of requiring external agents to be run and managed _by users themselves_ can be an issue in some use cases, usually in terms of portability and usability. A client python or shell script that builds a workflow is powerful, but what if a user doesn't have the correct python environment? Or python at all? What if the user is on a platform that offers no compatible shell? What is the user is simply not comfortable working in a terminal? In such cases these adaptive solutions are simply not indicated.

### Express the logic of the workflow itself programmatically without implementing it in a script

One solution to the dynamic workflow problem that does not require some external agent to execute is to describe the workflow somehow abstractly. ChRIS currently provides support for static sub-sets of a compute tree of linked plugins -- called ``pipelines`` or ``workflows``. These can be described as JSON files that explicitly describe the interconnectedness and relationship between a set of plugins, together with the parameter values for each plugin.

Unfortunately, at time of writing, these descriptions are completely _static_. While possible to create some ``pipeline`` language that contains the logic, this language, syntax, support and behavior would need to be created. Existing solutions do exist, such as the Workflow Description Language [WDL](https://github.com/openwdl/wdl) and others - and perhaps providing WDL or some subset thereof support to ChRIS could be attempted. Still this could be a complex engineering endeavor and unlikely to an immediate / simple short term solution.

### Enter containers

Given thus the current reality, another logical solution to the deployment problem is "Build the client into a container". This greatly simplifies the portability problem and reduces the space of requirements to one: use some containerization technology such as ``docker`` (and by implication a shell command line interface). Nonetheless, even this reduction might be prove onerous. Many users will find the requirement to setup and use ``docker`` on their systems too complex.

Interestingly, ChRIS itself is a platform that orchestrates container-based applications, called _plugins_. If distributing an agent that can construct trees of compute in a container is an option, then it is a small logical leap to consider, why not containerize this agent as a ChRIS plugin? In such a case, the portability and usability problem is even more simplified as the container itself becomes something the _ChRIS platform_ and not the _user_ manages.

This does blur the line somewhat spiritually as to the relationship between ChRIS plugins and the ChRIS platform. Should a plugin _know_ about talking to the actual platform that is scheduling its existence? This could be an interesting academic debate. 

### Enter ``pl-dypi``

Based on this insight, an initial solution is demonstrated by this thought-experiment plugin: ``pl-dypi`` demonstrates a solution to building complex trees _using ChRIS technologies_. The plugin, when _run_ attempts to speak to the platform and direct its subsequent scheduling based on the plugin's analysis of the data on which it is initialized.

## What this plugin demonstrates

``pl-dypi`` demonstrates splitting an input parent node into many parallel children, and applying a user specified ``workflow`` (i.e. tree of ChRIS plugin containers) to the contents of each child.

To keep things simple, ``pl-dypi`` operates with two core parameters:

* A regex that when applied over its input space can filter objects (for ex. a file blob like `*.mgz`)
* A string that specifies a _pipeline_ on the ChRIS/CUBE instance on which this plugin is being executed.
* An optional "parent" node to which to attach -- ``pl-dypi`` will by default attempt to self discover its parent.

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
docker build -t local/pl-dypi .
```

### Get JSON Representation

```shell
docker run --rm local/pl-dypi chris_plugin_info > MyProgram.json
```

### Local Test Run

Run latest versions of code without rebuilding the docker image:

```shell
docker run --rm -it --userns=host -u $(id -u):$(id -g) \
           -v  $PWD/app.py:/usr/local/lib/python3.10/site-packages/app.py:ro \
           -v $PWD/control:/usr/local/lib/python3.10/site-packages/control:ro \
           -v   $PWD/logic:/usr/local/lib/python3.10/site-packages/logic:ro \
           -v   $PWD/state:/usr/local/lib/python3.10/site-packages/state:ro \
           -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
           local//pl-dypi dypi /incoming /outgoing
```

Run latest versions of code without rebuilding the docker image suitable for debugging (running as non-root causes issues with `pudb`): 

```shell
 docker run --rm -it --userns=host  \
           -v  $PWD/app.py:/usr/local/lib/python3.10/site-packages/app.py:ro \
           -v $PWD/control:/usr/local/lib/python3.10/site-packages/control:ro \
           -v   $PWD/logic:/usr/local/lib/python3.10/site-packages/logic:ro \
           -v   $PWD/state:/usr/local/lib/python3.10/site-packages/state:ro \
           -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
           local/pl-dypi dypi /incoming /outgoing
```

_-30-_