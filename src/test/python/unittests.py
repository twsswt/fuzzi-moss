"""
@author probablytom
@author twsswt
"""

import unittest

from mock import Mock

from fuzzi_moss import *

from random import Random


def bool_func():
    return False


class Target(object):

    environment = list()

    @fuzz(identity)
    def mangled_function_identity(self):
        Target.environment.append(1)
        Target.environment.append(2)
        Target.environment.append(3)

    @fuzz(remove_random_step)
    def mangled_function_remove_random_step(self):
        Target.environment.append(1)
        Target.environment.append(2)
        Target.environment.append(3)

    @fuzz(remove_last_step)
    def mangled_function_remove_last_step(self):
        Target.environment.append(1)
        Target.environment.append(2)
        Target.environment.append(3)

    @fuzz(shuffle_steps)
    def mangled_function_shuffle_steps(self):
        Target.environment.append(1)
        Target.environment.append(2)
        Target.environment.append(3)

    @fuzz(choose_from([(0.5, identity), (0.5, remove_last_step)]))
    def mangled_function_choose_from(self):
        Target.environment.append(1)
        Target.environment.append(2)
        Target.environment.append(3)

    @fuzz(in_sequence([remove_last_step, remove_last_step]))
    def mangled_function_in_sequence(self):
        Target.environment.append(1)
        Target.environment.append(2)
        Target.environment.append(3)

    @fuzz(on_condition_that(True, remove_last_step))
    def mangled_function_on_condition_that(self):
        Target.environment.append(1)
        Target.environment.append(2)
        Target.environment.append(3)

    @fuzz(on_condition_that(bool_func, remove_last_step))
    def mangled_function_on_condition_that_with_function(self):
        Target.environment.append(1)
        Target.environment.append(2)
        Target.environment.append(3)

    @fuzz(swap_if_blocks)
    def mangled_function_swap_if_blocks(self):
        if True:
            Target.environment.append(1)
        else:
            Target.environment.append(2)

    @fuzz(replace_condition_with('1 is 2'))
    def mangled_function_replace_condition(self):
        if 1==1:
            Target.environment.append(1)
        else:
            Target.environment.append(2)


class FuzziMossTest(unittest.TestCase):

    def setUp(self):
        self.target = Target()
        Target.environment = list()

    def test_identity(self):
        self.target.mangled_function_identity()
        self.assertEquals([1, 2, 3], Target.environment)

    def test_remove__random_step(self):
        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.randint = Mock(side_effect=[1])

        self.target.mangled_function_remove_random_step()
        self.assertEqual([1, 3], Target.environment)

    def test_remove_last_step(self):
        self.target.mangled_function_remove_last_step()
        self.assertEqual([1, 2], Target.environment)

    def test_shuffle_steps(self):
        def mock_random_shuffle(iterable):
            result = list()
            result.append(iterable[2])
            result.append(iterable[0])
            result.append(iterable[1])
            return result

        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.shuffle = Mock(side_effect=mock_random_shuffle)

        self.target.mangled_function_shuffle_steps()
        self.assertEqual([3, 1, 2], Target.environment)

    def test_swap_if_blocks(self):
        self.target.mangled_function_swap_if_blocks()
        self.assertEqual([2], Target.environment)

    def test_choose_from(self):
        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.uniform = Mock(side_effect=[0.75])

        self.target.mangled_function_choose_from()
        self.assertEqual([1, 2], Target.environment)

    def test_in_sequence(self):
        self.target.mangled_function_in_sequence()
        self.assertEqual([1], Target.environment)

    def test_on_condition_that(self):
        self.target.mangled_function_on_condition_that()
        self.assertEqual([1, 2], Target.environment)

    def test_on_condition_that_with_function(self):
        self.target.mangled_function_on_condition_that_with_function()
        self.assertEqual([1, 2, 3], Target.environment)

    def test_replace_condition(self):
        self.target.mangled_function_replace_condition()
        self.assertEquals([2], Target.environment)


if __name__ == '__main__':
    unittest.main()
