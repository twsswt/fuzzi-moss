# Fuzzi_Moss - Code Fuzzing for Simulating Variance in Models of Socio-technical Systems

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

Fuzzi_Moss is a library for simulating variance in models of idealised workflow of socio-technical systems. The purpose
is to evaluate the resilience of a socio-technical system when a work flow is imperfectly executed by the actors in the
system.  These variations to the idealised work flow may be caused by a variety of factors, such as excess load on
human actors, insufficient or incorrect knowledge during decision making, or the development of local 'optimisations'
that short cut desired behaviour.

The variance is implemented using code fuzzing.  A socio-technical system is represented as a collection of python
classes that capture the pertinent aspects of the problem state as instance attributes.  System work flows are
represented as a hierarchical collection of functions that manipulate the state of the system model, with a top level
function providing an entry point for the work flow.  Work flow functions can optionally be collected into a class if
desired.

Fuzzing operations are implemented in an extensible library of fuzzers.  The fuzzers can be applied to workflow
functions in in two ways:

  * By constructing an Aspect Oriented Programming like advice dictionary, mapping function pointers to fuzzers
   (recommended).

  * By decorating fuzzable operations with an <code>@fuzz</code> decorator, parameterised with the desired fuzzer.

The AOP approach is preferred because

Each fuzzing operator is a function that accepts the body of a work flow function (as a list of statements) and returns
a fuzzed list of statements.

## Available Fuzzers

The core library includes both atomic and composite fuzzers for building more complex behaviours:

 * Identity
 * Applying a fuzzer to a subset of function body steps using a filter.  Filters provided include:
    * Identity
    * Random selection
    * n last steps
    * Excluding control structures
    * Inverting a selection
 * Removing steps
 * Duplicating steps
 * Shuffling steps
 * Applying a sequence of fuzz operators
 * Choosing a random fuzz operator to apply from a probability distribution.
 * Applying a fuzz operator conditionally.
 * Replacing the iterable of a foreach loop
 * Replacing a condition expression
 * Recursing into composite steps
 * Swapping if blocks

A number of demonstrator fuzzers are also provided:

  * Remove last step(s)
  * Duplicate last step
  * Remove random step

Fuzzers are also under development to represent high level cognitive behaviours in a workflow (incomplete).

  * Become distracted
  * Become muddled
  * Decision mistake


## Tutorial

Consider the following Python class representing a collection of simple workflow descriptions.



A fuzzed work flow can be executed as a normal python program.

