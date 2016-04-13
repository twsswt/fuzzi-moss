"""
@author probablytom, tws
"""

import unittest

from mock import Mock

from fuzzi_moss.core_mutators import *
import fuzzi_moss.core_mutators
from fuzzi_moss.mutate_decorator import mutate

from random import Random


class RemoveRandomStepTarget(object):

    environment = list()

    @mutate(remove_random_step)
    def mangled_function(self):
        RemoveRandomStepTarget.environment.append(1)
        RemoveRandomStepTarget.environment.append(2)
        RemoveRandomStepTarget.environment.append(3)


class RemoveLastStepTarget(object):

    environment = list()

    @mutate(remove_last_step)
    def mangled_function(self):
        RemoveLastStepTarget.environment.append(1)
        RemoveLastStepTarget.environment.append(2)
        RemoveLastStepTarget.environment.append(3)


class ChooseFromTarget(object):

    environment = list()

    @mutate(choose_from([(0.5, identity), (0.5, remove_last_step)]))
    def mangled_function(self):
        ChooseFromTarget.environment.append(1)
        ChooseFromTarget.environment.append(2)
        ChooseFromTarget.environment.append(3)


class InSequenceTarget(object):

    environment = list()

    @mutate(in_sequence([remove_last_step, remove_last_step]))
    def mangled_function(self):
        InSequenceTarget.environment.append(1)
        InSequenceTarget.environment.append(2)
        InSequenceTarget.environment.append(3)


class FuzziMossTest(unittest.TestCase):

    def test_remove__random_step(self):

        fuzzi_moss.core_mutators.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_mutators.fuzzi_moss_random.randint = Mock(side_effect=[1])

        target_a = RemoveRandomStepTarget()
        target_a.mangled_function()
        self.assertEqual([1,3], RemoveRandomStepTarget.environment)

    def test_remove_last_step(self):

        target_b = RemoveLastStepTarget()
        target_b.mangled_function()
        self.assertEqual([1, 2], RemoveLastStepTarget.environment)

    def test_choose_from(self):

        fuzzi_moss.core_mutators.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_mutators.fuzzi_moss_random.uniform = Mock(side_effect=[0.75])

        target_c = ChooseFromTarget()
        target_c.mangled_function()
        self.assertEqual([1, 2], ChooseFromTarget.environment)


    def test_sequence(self):
        target_d = InSequenceTarget()
        target_d.mangled_function()
        self.assertEqual([1], InSequenceTarget.environment)


if __name__ == '__main__':
    unittest.main()