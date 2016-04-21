"""
Provides a library of standard fuzz operators for work flows that can be assembled into domain specific fuzz operators.
@author probablytom
@author twsswt
"""

import ast
from ast import If, While

from random import Random

fuzzi_moss_random = Random()


def identity(steps):
    return steps


def replace_steps_with_pass(steps):
    if len(steps) > 0:
        last_step = steps[-1]
        return [ast.Pass(lineno=last_step.lineno, col_offset=last_step.lineno)]
    else:
        return [ast.Pass(lineno=1, col_offset=1)]


def remove_last_step(steps):
    if len(steps) > 1:
        steps.pop()
    else:
        steps = replace_steps_with_pass(steps)
    return steps


def remove_random_step(steps):
    if len(steps) > 1:
        index = fuzzi_moss_random.randint(0, len(steps) - 1)
        del steps[index]
    else:
        steps = replace_steps_with_pass(steps)
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


def replace_condition_with(condition=False):
    """
    A composite fuzzer that replaces conditions with the supplied condition.  The supplied condition may be a boolean
    """
    if type(condition) is str:
        parsed_ast = ast.parse('if %s: pass\nelse: False' % condition)
        replacement = parsed_ast.body[0].test
    elif hasattr(condition, '__call__'):
        replacement = ast.Call(
            func=ast.Name(
                id=condition.func_name,
                lineno=1,
                col_offset=1,
                ctx=ast.Load()),
            col_offset=1,
            lineno=1, args=list(),
            keywords=list())

    def _replace_condition(steps):
        for step in steps:
            if type(step) is If or type(step) is While:
                step.test = replacement
        return steps

    return _replace_condition


def replace_for_iterator_with(replacement=[]):
    """
    A composite fuzzer that replaces iterable expressions with the supplied iterable.  The function currently only
    supports lists of numbers and string literals.
    """
    def _replace_iterator_with(steps):
        for step in steps:
            if type(step) is ast.For:

                if type(replacement) is list:
                    elements = []
                    for i in replacement:
                        if type(i) in {int, long, float, complex}:
                            elements.append(ast.Num(lineno=step.iter.lineno, col_offset=step.iter.col_offset, n=i))
                        elif type(i) is str:
                            elements.append(ast.Str(lineno=step.iter.lineno, col_offset=step.iter.col_offset, s=i))

                    replacement_ast = ast.List(
                        lineno=step.iter.lineno,
                        col_offset=step.iter.col_offset,
                        elts=elements,
                        ctx=step.iter.ctx)

                step.iter = replacement_ast
        return steps

    return _replace_iterator_with


def recurse_into_nested_steps(fuzzer=identity, target_structures={ast.For, ast.TryExcept, ast.While, ast.If}):
    """
    A composite fuzzer that applies the supplied fuzzer recursively to bodies of control statements (For, While,
    TryExcept and If).  Recursion is applied at the head, i.e. the fuzzer supplied is applied to the parent block last.
    """

    def _recurse_into_nested_steps(steps):
        for step in steps:
            if type(step) in {ast.For, ast.TryExcept, ast.While} & target_structures:
                _recurse_into_nested_steps(step.body)
            elif type(step) in {ast.If} & target_structures:
                _recurse_into_nested_steps(step.body)
                _recurse_into_nested_steps(step.ifelse)
        fuzzer(steps)

        return steps

    return _recurse_into_nested_steps
