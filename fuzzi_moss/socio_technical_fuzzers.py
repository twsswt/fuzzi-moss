"""
Socio-technical fuzzers describe high level causes of variance in socio-technical fuzzers that can be built from the
core fuzzers library.
@author twsswt
"""

import ast
import inspect
import sys

from threading import Lock

from pydysofu.core_fuzzers import choose_last_steps, filter_context, filter_steps, recurse_into_nested_steps, \
    replace_steps_with, in_sequence, include_control_structures, insert_steps

from pydysofu.fuzz_weaver import get_reference_syntax_tree

# Logging Machinery

_lines_removed_lock = Lock()
lines_removed_counters = dict()


def _update_lines_removed_counter(workflow, n):
    global _lines_removed_lock
    _lines_removed_lock.acquire()
    lines_removed_counters[workflow] = lines_removed_counters.get(workflow, 0) + n
    _lines_removed_lock.release()


def reset_lines_removed_counters():
    global lines_removed_counters
    lines_removed_counters = dict()


def lines_removed_count(workflow=None):
    filtered_values = \
        filter(lambda t: t[0] == workflow, lines_removed_counters.items()) if workflow is not None \
        else lines_removed_counters.items()

    return sum(map(lambda t: t[1], filtered_values))


def removable_lines_count(function):
    func = function if inspect.isfunction(function) else function.im_func

    _syntax_tree = get_reference_syntax_tree(func)

    def _recurse_count_steps_available_for_removal(steps):
        result = 0
        for step in steps:
            result += 1
            if type(step) in {ast.For, ast.While}:
                result += _recurse_count_steps_available_for_removal(step.body)
            elif type(step) in {ast.If}:
                result += _recurse_count_steps_available_for_removal(step.body)
                result += _recurse_count_steps_available_for_removal(step.orelse)
            elif type(step) in {ast.TryExcept}:
                result += _recurse_count_steps_available_for_removal(step.body)
                for handler in step.handlers:
                    result += _recurse_count_steps_available_for_removal(handler.body)
        return result
    return _recurse_count_steps_available_for_removal(_syntax_tree.body[0].body)


# Fuzzers and Filters

def apply_fuzzing_when_workflow_actors_name_is(name_fuzzer_pairings=list()):
    """
    A filtering fuzzer for applying fuzzers selectively based on workflow actor names.
    """

    def _workflow_actors_name_is(steps, context):

        fuzz_filters = [
            (lambda workflow: False if workflow.actor is None else workflow.actor.logical_name == nfp[0], nfp[1])
            for nfp in name_fuzzer_pairings
        ]

        filtering_fuzzer = filter_context(fuzz_filters)

        return filtering_fuzzer(steps, context)

    return _workflow_actors_name_is


def default_distracted_pmf(conscientiousness=1):
    """
    Realises a 2-point PMF (True, False) that takes a duration and probability as parameters.
    """
    def _default_distracted_probability_mass_function(duration, probability):
        threshold = 1.0 / (duration + 1) ** (1.0 / conscientiousness)
        return probability < threshold

    return _default_distracted_probability_mass_function


class IsDistracted(object):

    def __init__(self, clock, random, probability_mass_function):
        self.clock = clock
        self.random = random
        self.probability_mass_function = probability_mass_function

        self.start_tick = self.clock.current_tick

    def __call__(self):
        duration = self.clock.current_tick - self.start_tick
        return self.probability_mass_function(duration, self.random.uniform(0.0, 1.0))


def missed_target(random, pmf=default_distracted_pmf(2)):
    """
    Creates a fuzzer that causes a workflow containing a while loop to be prematurely terminated before the condition
    in the reference function is satisfied.  The binary probability distribution for continuing work is a function of
    the duration of the workflow, as measured by the supplied turn based clock.
    :param random: a random value source.
    :param pmf: a function that accepts a duration and returns a probability threshold for an
    actor to be distracted from a target.
    :return: the insufficient effort fuzz function.
    """

    def _insufficient_effort(steps, context):

        break_insertion = \
            'if not self.is_distracted() : break'

        context.is_distracted = IsDistracted(context.actor.clock, random, pmf)

        fuzzer = \
            recurse_into_nested_steps(
                fuzzer=filter_steps(
                    fuzz_filter=include_control_structures(target={ast.While}),
                    fuzzer=recurse_into_nested_steps(
                        target_structures={ast.While},
                        fuzzer=insert_steps(0, break_insertion),
                        min_depth=1
                    )
                ),
                min_depth=1
            )

        return fuzzer(steps, context)

    return _insufficient_effort


def default_incomplete_procedure_pmf(concentration=1.0):

    def _probability_distribution(remaining_time, probability):

        adjusted_probability = probability ** ((remaining_time + 1.0) * concentration)

        return sys.maxint if adjusted_probability == 1.0 else int(1.0 / (1.0 - adjusted_probability) - 1)

    return _probability_distribution


def incomplete_procedure(random, pmf=default_incomplete_procedure_pmf()):
    """
    Creates a fuzzer that causes a workflow to be truncated.  The provided discrete probability distribution defines
    the number of steps to be removed. By default, the distribution removes no steps.
    :param random : a random value source for generating a uniform random distribution.
    :param pmf:  A function that accepts a maximum number of steps, a remaining time and a
    probability and returns an integer number of steps to be removed.
    :return: the underlying fuzzer.
    """

    def _incomplete_procedure(steps, context):
        clock = context.actor.clock
        remaining_time = clock.max_ticks - clock.current_tick

        probability = random.uniform(0.0, 0.9999)

        n = pmf(remaining_time, probability)

        choose_last_steps_fuzzer = choose_last_steps(n, False)

        fuzzer = in_sequence(
            [
                recurse_into_nested_steps(
                    target_structures={ast.While, ast.For, ast.TryExcept},
                    fuzzer=filter_steps(
                        choose_last_steps_fuzzer,
                        replace_steps_with(replacement='self.actor.idling.idle()')
                    )
                )
            ]
        )

        result = fuzzer(steps, context)
        _update_lines_removed_counter(context.__class__, n - choose_last_steps_fuzzer.n)
        return result

    return _incomplete_procedure


def decision_mistake():
    # TODO
    pass


def become_muddled():
    # TODO
    pass
