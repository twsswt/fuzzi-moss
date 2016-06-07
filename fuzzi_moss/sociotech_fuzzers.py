"""
Socio-technical fuzzers describe high level causes of variance in socio-technical fuzzers that can be built from the
core fuzzers library.
@author twsswt
"""

from core_fuzzers import remove_last_steps
import fuzzi_moss.core_fuzzers

def become_distracted(distribution=lambda p: 1):
    """
    Creates a fuzzer that removes a random number of lines of code from the end of the fuzzed workflow.  The number
    of lines removed is determined by the supplied distribution function.

    :param distribution:  A function that accepts a probability (0.0 <= p <= 1.0) and returns an integer number of
    lines to be removed.
    :return: the underlying fuzzer.
    """

    def _become_distracted(steps):
        p = fuzzi_moss.core_fuzzers.fuzzi_moss_random.random()
        fuzzer = remove_last_steps(distribution(p))
        return fuzzer(steps)

    return _become_distracted


def decision_mistake(p=0.0):
    pass


def become_muddled():
    pass