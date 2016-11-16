import unittest

from mock import Mock

import pydysofu
from fuzzi_moss.sociotech_fuzzers import become_distracted

from example_workflow import ExampleWorkflow


class FuzziMossWeaverTest(unittest.TestCase):

    def setUp(self):
        self.environment = list()
        self.target = ExampleWorkflow(self.environment)

    def test_become_distracted(self):
        pydysofu.pydysofu_random.random = Mock(side_effect=[0.75])

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: become_distracted(lambda p: 1 if p < 0.5 else 2)
        }
        pydysofu.fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEquals(self.environment, [1])

if __name__ == '__main__':
    unittest.main()
