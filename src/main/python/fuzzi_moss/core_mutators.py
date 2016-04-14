"""
Provides a library of standard mutators for workflows that can be assembled into domain specific mutators.
@author probablytom
@author twsswt
"""

from random import Random

fuzzi_moss_random = Random()


def in_sequence(sequence=[]):
    """
    A composite mutator that applies the supplied list of mutant operators in sequence.
    """

    def _in_sequence(steps):
        for mutator in sequence:
            steps = mutator(steps)

        return steps

    return _in_sequence


def choose_from(distribution=[(1.0, lambda x: x)]):
    """
    A composite mutator that selects a mutation from a probability distribution, represented as (weight, mutator
    function) tuples.
    """

    def _choose_from(steps):
        total_weight = sum(map(lambda t: t[0], distribution))

        p = fuzzi_moss_random.uniform(0.0, total_weight)

        upto = 0.0
        for weight, mutator in distribution:
            upto += weight
            if upto >= p:
                return mutator(steps)

    return _choose_from


def on_condition_that(condition, mutator):
    """
    A composite mutator that applies a mutator if the specified condition holds.
    : param : condition the condiction to test.  Can either be a boolean value or a 0-ary function
     that returns a boolean value.
    """

    def _on_condition_that(steps):
        if hasattr(condition, '__call__'):
            if condition():
                return mutator(steps)
            else:
                return steps
        elif condition:
            return mutator(steps)
        else:
            return steps

    return _on_condition_that


def identity(steps):
    return steps


def remove_random_step(steps):
    if len(steps) > 1:
        index = fuzzi_moss_random.randint(0, len(steps) - 1)
        del steps[index]
    return steps


def remove_last_step(steps):
    if len(steps) > 1:
        steps.pop()
    return steps


def shuffle_steps(steps):
    return fuzzi_moss_random.shuffle(steps)
