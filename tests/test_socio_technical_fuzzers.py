import unittest

from mock import Mock, PropertyMock, patch

from theatre_ag import Actor, SynchronizingClock

import pydysofu
from fuzzi_moss.socio_technical_fuzzers import *

from example_workflow import ExampleWorkflow


class FuzziMossWeaverTest(unittest.TestCase):

    def setUp(self):
        self.environment = list()
        self.target = ExampleWorkflow(self.environment)

    def test_truncated_workflow(self):
        pydysofu.pydysofu_random.random = Mock(side_effect=[0.75])

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: incomplete_procedure(lambda p: 1 if p < 0.5 else 2)
        }
        pydysofu.fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEquals([1], self.environment)

    def test_missed_target(self):

        with patch('theatre_ag.SynchronizingClock.current_tick', new_callable=PropertyMock) as current_tick_mock:
            current_tick_mock.side_effect=[1, 1, 2, 3, 4, 5, 6]

            mock_random = Mock(spec=Random)
            mock_random.uniform = Mock(side_effect=[0.0, 0.0, 0.0, 1.0])

            patched_clock = SynchronizingClock()

            test_advice = {
                ExampleWorkflow.method_that_targets_a_goal: missed_target(patched_clock, mock_random)
            }

            pydysofu.fuzz_clazz(ExampleWorkflow, test_advice)

            self.target.method_that_targets_a_goal()

            self.assertEquals(3, len(self.environment))

if __name__ == '__main__':
    unittest.main()
