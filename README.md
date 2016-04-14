#Fuzzi_Moss - Code Fuzzing for Simulating Variance in Models of Socio-technical Systems

##Contributors

  * Tom Wallis<br/>
    School of Computing Science, University of Glasgow<br/>
    GitHub ID: probablytom
    [twallisgm@googlemail.com](mailto:twallisgm@googlemail.com)

  * Tim Storer<br/>
    School of Computing Science, University of Glasgow<br/>
    GitHub ID: twsswt
    [timothy.storer@glagow.ac.uk](mailto:timothy.storer@glagow.ac.uk)

##Overview

Fuzzi_Moss is a library for simulating variance in models of idealised workflow of socio-technical systems. The purpose
is to evaluate the resilience of a socio-technical system when a work flow is imperfectly executed by the actors in the
system.  These variations to the idealised work flow may be caused by a variety of factors, such as excess load on
human actors, insufficient or incorrect knowledge during decision making, or the development of local 'optimisations'
that short cut desired behaviour.

The variance is implemented using code fuzzing.  A socio-technical system is represented as a collection of python
classes that capture the pertinent aspects of the problem state as instance attributes.  System work flows are
represented as a hierarchical collection of functions that manipulate the state of the system model, with a top level
function providing an entry point for the work flow.  Work flow functions can optionally be collected into a class if
desired.  The functions in the work flow that are considered to be subject to variance are decorated with an
<code>@fuzz</code> decorator, that can be configured using an extensible library of fuzzing operators.  Each fuzzing
operator is a function that accepts the body of a work flow function (as a list of statements) and returns a fuzzed
list of statements.

The core library includes both atomic and composite fuzzing operators:

 * Identity
 * Removing a random statement from a body.
 * Removing the last statement in a body.
 * Shuffling the statements in the body.
 * Applying a sequence of fuzz operators
 * Choosing a random fuzz operator to apply from a probability distribution.
 * Applying a fuzz operator conditionally.

A fuzzed work flow can be executed as a normal python program.

##Tutorial