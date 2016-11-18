"""
Socio-technical fuzzers describe high level causes of variance in socio-technical fuzzers that can be built from the
core fuzzers library.
@author twsswt
"""

from pydysofu.core_fuzzers import *


simulation_clock_trackers = list()


def _register_clock_tracker(tracker):
    simulation_clock_trackers.append(tracker)
    return len(simulation_clock_trackers) - 1


class _DurationTracker(object):

    def __init__(self, clock, random, p_distribution):
        self.clock = clock
        self.random = random
        self.p_distribution = p_distribution

        self.start_tick = clock.current_tick

    def test_condition(self):
        duration = self.clock.current_tick - self.start_tick

        probability = self.random.uniform(0.0, 1.0)

        return self.p_distribution(probability, duration)


def incomplete_procedure(truncation_pd=lambda steps: 0):
    """
    Creates a fuzzer that causes a workflow to be truncated.  The provided discrete probability distribution defines
    the number of steps to be removed. By default, the distribution removes no steps.
    :param truncation_pd:  A function that accepts a maximum number of steps and returns an
    integer number of steps to be removed.
    :return: the underlying fuzzer.
    """

    insertion = 'import fuzzi_moss.socio_technical_fuzzers\n'

    def _incomplete_procedure(steps):
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
        return fuzzer(steps)

    return _incomplete_procedure


def missed_target(clock, random, distraction_pd=lambda p, d: p < 1.0 / (d + 1) ** 0.5):
    """
    Creates a fuzzer that causes a workflow containing a while loop to be prematurely terminated before the condition
    in the reference function is satisfied.  The binary probability distribution for continuing work is a function of
    the duration of the workflow, as measured by the supplied turn based clock.  By default, the probability of
    continuing work is defined by the formula:

        probability = 1 / (duration + 1) ^ 0.5

    :param clock: the simulation clock.
    :param random: a Random instance used as a source of uniform distribution values in the range 0.0 to 1.0.
    :param distraction_pd: a function that accepts a duration and returns a probability threshold for an actor to be
    distracted from a target.
    :return: the insufficient effort fuzz function.
    """

    index = _register_clock_tracker(_DurationTracker(clock, random, distraction_pd))

    insertion = 'import fuzzi_moss.socio_technical_fuzzers\n'

    condition_text = \
        'fuzzi_moss.socio_technical_fuzzers.simulation_clock_trackers[%d].test_condition()' % index

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
