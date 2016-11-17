"""
Socio-technical fuzzers describe high level causes of variance in socio-technical fuzzers that can be built from the
core fuzzers library.
@author twsswt
"""

from pydysofu.core_fuzzers import *

from pydysofu.config import pydysofu_random


def incomplete_procedure(distribution=lambda p: 1):
    """
    Creates a fuzzer that removes a random number of lines of code from the end of a workflow.  The number
    of lines removed is determined by the supplied distribution function.

    :param distribution:  A function that accepts a probability (0.0 <= p <= 1.0) and returns an integer number of
    lines to be removed.
    :return: the underlying fuzzer.
    """
    def _incomplete_procedure(steps):
        p = pydysofu_random.random()
        fuzzer = remove_last_steps(distribution(p))
        return fuzzer(steps)

    return _incomplete_procedure


def _default_distraction_pd(duration):
    return 1.0 / (duration + 1) ** 0.5


simulation_clock_trackers = list()


class _InsufficientEffortTracker(object):

    def __init__(self, clock, random, p_distribution):
        self.clock = clock
        self.start_tick = clock.current_tick
        self.p_distribution = p_distribution

        self.random = random

    def distraction_check(self):
        duration = self.clock.current_tick - self.start_tick

        threshold = self.p_distribution(duration)
        probability = self.random.uniform(0.0, 1.0)

        return probability < threshold


def missed_target(clock, random, distraction_pd=_default_distraction_pd):
    """
    Creates a fuzzer that causes a workflow containing a while loop to be prematurely terminated before the condition
    in the reference function is reached.  The probability distribution for continuing work is a function of the
    duration of the workflow, as measured by the supplied turn based clock.  By default, the probability distribution
    is defined by the formula:

        probability = 1 / (duration + 1) ^ 0.5

    :param clock: the simulation clock.
    :param random: a Random instance used as a source of uniform distribution values in the range 0.0 to 1.0.
    :param distraction_pd: a function that accepts a duration and returns a probability threshold for an actor to be
    distracted from a target.
    :return: the insufficient effort fuzz function.
    """

    simulation_clock_trackers.append(_InsufficientEffortTracker(clock, random, distraction_pd))

    insertion = 'import fuzzi_moss.socio_technical_fuzzers\n'

    index = len(simulation_clock_trackers) - 1

    condition_text = \
        'fuzzi_moss.socio_technical_fuzzers.simulation_clock_trackers[%d].distraction_check()' % index

    def _insufficient_effort(steps):
        fuzzer = in_sequence(
            [
                insert_steps(0, insertion),
                recurse_into_nested_steps(
                    target_structures={ast.For, ast.TryExcept},
                    fuzzer=filter_steps(
                        exclude_control_structures(target={ast.If}),
                        replace_condition_with(condition_text)
                    )
                )
            ]
        )

        return fuzzer(steps)

    return _insufficient_effort


def decision_mistake():
    # TODO
    pass


def become_muddled():
    # TODO
    pass

