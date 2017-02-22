import unittest

from mock import Mock, PropertyMock, patch

from random import Random

from theatre_ag import Actor, SynchronizingClock

import pydysofu

from fuzzi_moss.socio_technical_fuzzers import *

from example_workflow import ExampleWorkflow


class SocioTechnicalFuzzersTestCase(unittest.TestCase):

    def setUp(self):
        self.environment = list()
        self.example_workflow = ExampleWorkflow(self.environment)
        self.example_workflow.actor = Mock(spec=Actor)
        self.example_workflow.actor.logical_name = 'Alice'

    def test_truncated_workflow(self):
        with patch('theatre_ag.SynchronizingClock.current_tick', new_callable=PropertyMock) as current_tick_mock:
            current_tick_mock.side_effect = [1]

            mock_random = Mock(spec=Random)
            mock_random.uniform = Mock(side_effect=[.6])

            patched_clock = SynchronizingClock(1)
            self.example_workflow.actor.clock = patched_clock

            test_advice = {
                ExampleWorkflow.method_for_fuzzing:
                    incomplete_procedure(mock_random, default_incomplete_procedure_pmf())
            }
            pydysofu.fuzz_clazz(ExampleWorkflow, test_advice)

            self.example_workflow.method_for_fuzzing()
            self.assertEquals([1, 2], self.environment)

    def test_missed_target(self):

        with \
                patch('theatre_ag.SynchronizingClock.current_tick', new_callable=PropertyMock) as current_tick_mock:

            current_tick_mock.side_effect = [1, 1, 2, 3, 4, 5, 6]

            patched_clock = SynchronizingClock()
            self.example_workflow.actor.clock = patched_clock

            mock_random = Mock(spec=Random)
            mock_random.uniform = Mock(side_effect=[0.0, 0.0, 0.0, 1.0])

            test_advice = {
                ExampleWorkflow.method_that_targets_a_goal:
                    apply_fuzzing_when_workflow_actors_name_is(
                        [('Alice', missed_target(mock_random, default_distracted_pmf(2)))]
                    )
            }

            pydysofu.fuzz_clazz(ExampleWorkflow, test_advice)

            self.example_workflow.method_that_targets_a_goal()

            self.assertEquals(3, len(self.environment))

if __name__ == '__main__':
    unittest.main()
