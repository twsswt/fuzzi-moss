import unittest

from mock import patch, Mock, PropertyMock

from nose_parameterized import parameterized

from random import Random

from theatre_ag import SynchronizingClock

from fuzzi_moss.probability_distributions import steps_to_remove_distribution


def name_func(testcase_func, param_num, param):
    return "%s_%03d" % (testcase_func.__name__, param_num)


def create_test_parameters():
    return [
        [1, 1, 1.0, 3, 3],  # no time left, certainty of removal.
        [1, 1, 0.0, 3, 0],  # no time left, zero probability of removal.
        [1, 1, 0.7, 3, 2],  # no time left, some probability of removal.
        [1000, 1, 1.0, 3, 3],  # plenty of time left, certainty of removal
        [1000, 1, 0.0, 3, 0],  # plenty of time left, zero probability of removal.
        [1000, 1, 0.9995, 3, 1]  # plenty of time left, but high probability of removal.
    ]


class FuzziMossWeaverTest(unittest.TestCase):

    @parameterized.expand(create_test_parameters, testcase_func_name=name_func)
    def test_steps_to_remove_distribution(self, max_ticks, current_tick, probability, length_of_steps, expected_n):

        with patch('theatre_ag.SynchronizingClock.current_tick', new_callable=PropertyMock) as current_tick_mock:
            current_tick_mock.side_effect = [current_tick]

            patched_clock = SynchronizingClock(max_ticks)

            random_mock = Mock(spec=Random)
            random_mock.uniform = Mock(side_effect=[probability])

            n = steps_to_remove_distribution(patched_clock, random_mock)(length_of_steps)

            self.assertEquals(expected_n, n)




