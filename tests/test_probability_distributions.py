import unittest

from mock import patch, Mock, PropertyMock

from nose_parameterized import parameterized

from random import Random

from theatre_ag import SynchronizingClock

from fuzzi_moss import steps_to_remove_distribution, default_distracted_pmf


def name_func(func, param_num, param):
    return "%s_%03d" % (func.__name__, param_num)


def create_test_parameters_for_steps_to_remove_distribution():
    return [
        [1, 1, 1.0, 3, 3],  # no time left, certainty of removal.
        [1, 1, 0.0, 3, 0],  # no time left, zero probability of removal.
        [1, 1, 0.7, 3, 2],  # no time left, some probability of removal.
        [1000, 1, 1.0, 3, 3],  # plenty of time left, certainty of removal
        [1000, 1, 0.0, 3, 0],  # plenty of time left, zero probability of removal.
        [1000, 1, 0.9995, 3, 1]  # plenty of time left, but high probability of removal.
    ]


class TestStepsToRemoveDistribution(unittest.TestCase):

    @parameterized.expand(create_test_parameters_for_steps_to_remove_distribution, testcase_func_name=name_func)
    def test(self, max_ticks, current_tick, probability, length_of_steps, expected_n):

        with patch('theatre_ag.SynchronizingClock.current_tick', new_callable=PropertyMock) as current_tick_mock:
            current_tick_mock.side_effect = [current_tick]

            patched_clock = SynchronizingClock(max_ticks)

            random_mock = Mock(spec=Random)
            random_mock.uniform = Mock(side_effect=[probability])

            n = steps_to_remove_distribution(patched_clock, random_mock)(length_of_steps)

            self.assertEquals(expected_n, n)


def create_test_parameters_for_missed_target():
    return [
        [0, 1.0, False, 1],  # Only just started, but still possible to terminate prematurely due to distraction.
        [0, 0.99, True, 1],  # Only just started, so probability needs to be 1 to terminate.
        [1000, 0.00099, True, 1],  # Been working a long time, so low probability of continuing.
        [10, 0.09, True, 1],  # Been working a short time, so relatively low probability of continuing.for
        [9, 0.79, True, 10],  # Conscientious workers worker longer.
        [1000, 0.95, True, 10000]  # ...really, really longer
    ]


class MissedTargetDistributionTestCase(unittest.TestCase):

    @parameterized.expand(create_test_parameters_for_missed_target, testcase_func_doc=name_func)
    def test(self, duration, probability, expected, conscientiousness):

        result = default_distracted_pmf(conscientiousness)(duration, probability)

        self.assertEquals(expected, result)


