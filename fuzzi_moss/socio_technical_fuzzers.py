"""
Socio-technical fuzzers describe high level causes of variance in socio-technical fuzzers that can be built from the
core fuzzers library.
@author twsswt
"""

from pydysofu.core_fuzzers import *

from .probability_distributions import default_distracted_probability_mass_function


def workflow_actors_name_is(logical_name):

    def _workflow_actors_name_is(workflow):

        return False if workflow.actor is None else workflow.actor.logical_name == logical_name

    return _workflow_actors_name_is


class IsDistracted(object):

    def __init__(self, clock, random, probability_mass_function):
        self.clock = clock
        self.random = random
        self.probability_mass_function = probability_mass_function

        self.start_tick = self.clock.current_tick

    def __call__(self, *args, **kwargs):
        duration = self.clock.current_tick - self.start_tick
        return self.probability_mass_function(duration, self.random.uniform(0.0, 1.0))


def missed_target(random, probability_mass_function=default_distracted_probability_mass_function(2)):
    """
    Creates a fuzzer that causes a workflow containing a while loop to be prematurely terminated before the condition
    in the reference function is satisfied.  The binary probability distribution for continuing work is a function of
    the duration of the workflow, as measured by the supplied turn based clock.
    :param random: a random value source.
    :param probability_mass_function: a function that accepts a duration and returns a probability threshold for an
    actor to be distracted from a target.
    :return: the insufficient effort fuzz function.
    """

    def _insufficient_effort(steps, context):

        break_insertion = \
            'if not self.is_distracted() : break'

        context.is_distracted = IsDistracted(context.actor.clock, random, probability_mass_function)

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


def incomplete_procedure(truncation_pd=lambda max_steps: 0):
    """
    Creates a fuzzer that causes a workflow to be truncated.  The provided discrete probability distribution defines
    the number of steps to be removed. By default, the distribution removes no steps.
    :param truncation_pd:  A function that accepts a maximum number of steps and returns an
    integer number of steps to be removed.
    :return: the underlying fuzzer.
    """

    insertion = 'import fuzzi_moss.socio_technical_fuzzers\n'

    def _incomplete_procedure(steps, context):
        n = truncation_pd(len(steps))

        fuzzer = in_sequence(
            [
                insert_steps(0, insertion),
                recurse_into_nested_steps(
                    target_structures={ast.For, ast.TryExcept},
                    fuzzer=filter_steps(
                        exclude_control_structures(),
                        remove_last_steps(n)
                    )
                )
            ]
        )
        return fuzzer(steps, context)

    return _incomplete_procedure


def decision_mistake():
    # TODO
    pass


def become_muddled():
    # TODO
    pass
