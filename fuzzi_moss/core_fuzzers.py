"""
Provides a library of standard fuzz operators for work flows that can be assembled into domain specific fuzz operators.
@author probablytom
@author twsswt
"""

import ast
from ast import If, While
import inspect

from random import Random


fuzzi_moss_random = Random()


def in_sequence(sequence=[]):
    """
    A composite fuzz operator that applies the supplied list of fuzz operators in sequence.
    :param sequence: the sequence of fuzz operators to apply.
    :return : a fuzz operator that applies each of the supplied fuzz operators in sequence.
    """

    def _in_sequence(steps):
        for fuzzer in sequence:
            steps = fuzzer(steps)

        return steps

    return _in_sequence


def choose_from(distribution=[(1.0, lambda x: x)]):
    """
    A composite fuzz operator that selects a fuzz operator from the supplied probability distribution.
    :param distribution: the probability distribution from which to select a fuzz operator, represented as a sequence of
    (scalar weight, fuzzing operator) tuples.
    :returns : a fuzz operator selected at random from the supplied probability distribution.
    """

    def _choose_from(steps):
        total_weight = sum(map(lambda t: t[0], distribution))

        p = fuzzi_moss_random.uniform(0.0, total_weight)

        up_to = 0.0
        for weight, fuzzer in distribution:
            up_to += weight
            if up_to >= p:
                return fuzzer(steps)

    return _choose_from


def on_condition_that(condition, fuzzer):
    """
    A composite fuzz operator that applies a fuzz operator if the specified condition holds.
    :param  condition:  Can either be a boolean value or a 0-ary function that returns a boolean value.
    :returns: a fuzz operator that applies the underlying fuzz operator if the specified condition is satisfied.
    """

    def _on_condition_that(steps):
        if hasattr(condition, '__call__'):
            if condition():
                return fuzzer(steps)
            else:
                return steps
        elif condition:
            return fuzzer(steps)
        else:
            return steps

    return _on_condition_that


def identity(steps):
    return steps


def remove_random_step(steps):
    if len(steps) > 1:
        index = fuzzi_moss_random.randint(0, len(steps) - 1)
        del steps[index]
    else:
        last_step = steps[0]
        steps = [ast.Pass(lineno=last_step.lineno, col_offset=last_step.lineno)]
    return steps


def remove_last_step(steps):
    if len(steps) > 1:
        steps.pop()
    else:
        last_step = steps[0]
        steps = [ast.Pass(lineno=last_step.lineno, col_offset=last_step.lineno)]
    return steps


def shuffle_steps(steps):
    return fuzzi_moss_random.shuffle(steps)


def swap_if_blocks(steps):
    for step in steps:
        if type(step) is If:
            temp = step.body
            step.body = step.orelse
            step.orelse = temp

    return steps


def replace_condition_with(condition):
    if type(condition) is str:
        parsed_ast = ast.parse('if %s: pass\nelse: False' % condition)
        replacement = parsed_ast.body[0].test
    elif hasattr(condition,'__call__'):
        replacement = ast.Call(
            func=ast.Name(
                id=condition.func_name,
                lineno=1,
                col_offset=1,
                ctx=ast.Load()),
            col_offset=1,
            lineno=1,args=list(),
            keywords=list())

    def _replace_condition(steps):
        for step in steps:
            if type(step) is If or type(step) is While:
                step.test = replacement
        return steps

    return _replace_condition


def recurse_into_nested_steps(fuzzer=identity):
    def _recurse_into_nested_steps(steps):

        for step in steps:
            if  type(step) in {ast.For, ast.TryExcept, ast.While}:
                _recurse_into_nested_steps(step.body)

        fuzzer(steps)

        return steps

    return _recurse_into_nested_steps

