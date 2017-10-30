# Fuzzi Moss

A code fuzzing library for simulating variance in models of socio-technical systems, based on the PyDySoFu library.

## Contributors

* Tom Wallis<br/>
  School of Computing Science, University of Glasgow<br/>
  GitHub ID: probablytom
  [twallisgm@googlemail.com](mailto:twallisgm@googlemail.com)

* Tim Storer<br/>
  School of Computing Science, University of Glasgow<br/>
  GitHub ID: twsswt
  [timothy.storer@glagow.ac.uk](mailto:timothy.storer@glagow.ac.uk)

## Overview

Fuzzi Moss is a library for simulating variance in models of idealised workflow of socio-technical systems. The purpose
is to evaluate the resilience of a socio-technical system when a work flow is imperfectly executed by the actors in the
system.  These variations to the idealised work flow may be caused by a variety of factors, such as excess load on
human actors, insufficient or incorrect knowledge during decision making, or the development of local 'optimisations'
that short cut desired behaviour.

Socio-technical workflows are implemented in the theatre_ag framework. The variance is implemented using the pydysofu
dynamic code
fuzzing.  A socio-technical system is represented as a collection of python
classes that capture the pertinent aspects of the problem state as instance attributes.  System work flows are
represented as a hierarchical collection of functions that manipulate the state of the system model, with a top level
function providing an entry point for the work flow.  Work flow functions can optionally be collected into a class if
desired.

## Available Fuzzers

Fuzzers are under development to represent high level cognitive behaviours in a workflow (incomplete).

* Become distracted
* Become muddled
* Decision mistake