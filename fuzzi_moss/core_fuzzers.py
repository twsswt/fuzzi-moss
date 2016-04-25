"""
Provides a library of standard fuzz operators for work flows that can be assembled into domain specific fuzz operators.
@author probablytom
@author twsswt
"""

import ast
import _ast
from ast import If, While

import copy

from random import Random

fuzzi_moss_random = Random()


# Template fuzzers and associated default identity functions.


def identity(steps):
    return steps


def filter_steps(filter=lambda steps: range(0, len(steps)), fuzzer=identity):
    """
    A composite fuzzer that applies the supplied fuzzer to a list of steps produced by applying the specified filter
    to the target sequence of steps.
    :param filter: a pointer to a function that returns a list of step indices, referencing the target steps to be
     fuzzed.  By default, an identity filter is applied, returning a list containing an index for each step in the
     target steps.
    :param fuzzer: the fuzzer to apply to the filtered steps.
    """
    def _filter_steps(steps):
        regions = filter(steps)

        for region in regions:
            start = region[0]
            end = region[1]

            filtered_steps = steps[start:end]
            steps[start:end]=fuzzer(filtered_steps)

        return steps

    return _filter_steps


# Step Filtering functions.


def choose_identity(steps):
    return (0, len(steps))


def choose_random_steps(n):

    def _choose_random_steps(steps):
        if len(steps) <= n:
            return [(0, len(steps)-1)]
        else:
            sample_indices = fuzzi_moss_random.sample(range(0, len(steps)-1), n)
            return [(i, i+1) for i in sample_indices]

    return _choose_random_steps


def choose_last_step(steps):
    candidate = len(steps)-1
    step = steps[candidate]
    while candidate > 0 and type(step) is ast.Pass:
        candidate-=1
        step = steps[candidate]
    return [(candidate, candidate+1)]


def exclude_control_structures(target={ast.For, ast.If, ast.TryExcept, ast.While, ast.Return}):
    def _exclude_control_structures(steps):
        result = list()

        for i in range(0,len(steps)):
            if type(steps[i]) not in {ast.For, ast.If, ast.TryExcept, ast.While, ast.Return} & target:
                result.append((i, i+1))

        return result

    return _exclude_control_structures


# Atomic Fuzzers.


def _replace_step_with_pass(step):
    return ast.Pass(lineno=step.lineno, col_offset=step.lineno)


def replace_steps_with_passes(steps):
    return [_replace_step_with_pass(step) for step in steps]


def duplicate_steps(steps):
    return steps + copy.deepcopy(steps)


def remove_last_step(steps):
    fuzzer = filter_steps(choose_last_step, replace_steps_with_passes)
    return fuzzer(steps)


def remove_random_step(steps):
    fuzzer = filter_steps(choose_random_steps(1), replace_steps_with_passes)
    return fuzzer(steps)


def duplicate_last_step(steps):
    fuzzer = filter_steps(choose_last_step, duplicate_steps)
    return fuzzer(steps)


def shuffle_steps(steps):
    return fuzzi_moss_random.shuffle(steps)


def swap_if_blocks(steps):
    for step in steps:
        if type(step) is If:
            temp = step.body
            step.body = step.orelse
            step.orelse = temp

    return steps


# Composite Fuzzers


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
    def build_replacement(step):

        if type(condition) is str:
            parsed_ast = ast.parse('if %s: pass\nelse: False' % condition)
            return parsed_ast.body[0].test

        elif hasattr(condition, '__call__'):
            return ast.Call(
                func=ast.Name(
                    id=condition.func_name,
                    lineno=step.lineno,
                    col_offset=step.col_offset,
                    ctx=ast.Load()
                ),
                col_offset=step.col_offset,
                lineno=step.lineno,
                args=list(),
                keywords=list()
            )

        elif type(condition) is bool:
            return _ast.Name(
                id=str(condition),
                lineno=step.lineno,
                col_offset=step.col_offset,
                ctx=ast.Load()
            )

    def _replace_condition(steps):
        for step in steps:
            if type(step) is If or type(step) is While:
                step.test = build_replacement(step)
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

                elif callable(replacement):
                    pass

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
            if type(step) in {ast.For, ast.While} & target_structures:
                step.body = _recurse_into_nested_steps(step.body)
            elif type(step) in {ast.If} & target_structures:
                step.body = _recurse_into_nested_steps(step.body)
                step.orelse = _recurse_into_nested_steps(step.orelse)
            elif type(step) in {ast.TryExcept} & target_structures:
                step.body = _recurse_into_nested_steps(step.body)
                for handler in step.handlers:
                    _recurse_into_nested_steps(handler.body)
        return fuzzer(steps)

    return _recurse_into_nested_steps
