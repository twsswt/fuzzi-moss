import unittest

from mock import Mock

import fuzzi_moss

from fuzzi_moss import *

from fuzzi_moss import fuzz_clazz


class ExampleWorkflow(object):

    def __init__(self, environment):
        self.environment = environment

    def method_for_fuzzing(self):
        self.environment.append(1)
        self.environment.append(2)
        self.environment.append(3)

    def method_for_fuzzing_that_returns_4(self):
        self.environment.append(1)
        self.environment.append(2)
        self.environment.append(3)
        return 4

    def method_containing_if(self):
        if True:
            self.environment.append(1)
        else:
            self.environment.append(2)

    def make_nested_fuzzing_call(self):
        self.nested_method_call()
        self.environment.append(3)
        self.environment.append(4)

    def nested_method_call(self):
        self.environment.append(1)
        self.environment.append(2)

    def method_containing_iterator(self):
        for i in [1, 2, 3, 4]:
            self.environment.append(i)

    def method_containing_for_and_nested_try(self):
        for i in range(0, 3):
            try:
                self.environment.append(i)
                if i == 2:
                    raise Exception()
                self.environment.append("TO BE REMOVED")
            except Exception:
                self.environment.append(7)
                self.environment.append(9)
            self.environment.append("TO BE REMOVED")
        self.environment.append("TO BE REMOVED")

    def method_containing_if_followed_by_for(self):
        if True:
            self.environment.append(1)

        for i in range(1, 3):
            self.environment.append(i)


class FuzziMossWeaverTest(unittest.TestCase):

    def setUp(self):
        self.environment = list()
        self.target = ExampleWorkflow(self.environment)

    def test_identity(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: identity
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEquals([1, 2, 3], self.environment)

    def test_remove_last_step(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: remove_last_step
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([1, 2], self.environment)

    def test_remove_last_step_twice(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: remove_last_step
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.target.method_for_fuzzing()
        self.assertEqual([1, 2, 1, 2], self.environment)

    def test_duplicate_last_step(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: duplicate_last_step
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([1, 2, 3, 3], self.environment)

    def test_remove_random_step(self):
        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.sample = Mock(side_effect=[[1]])

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: remove_random_step
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([1, 3], self.environment)

    def test_remove__random_step_twice(self):
        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.sample = Mock(side_effect=[[1], [2]])

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: remove_random_step
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.target.method_for_fuzzing()
        self.assertEqual([1, 3, 1, 2], self.environment)

    def test_replace_all_steps_with_pass_in_random_sequence(self):
        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.sample = Mock(side_effect=[[0], [1], [2]])

        test_advice = {
            ExampleWorkflow.method_for_fuzzing:
                in_sequence([remove_random_step, remove_random_step, remove_random_step])
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([], self.environment)

    def test_remove_all_steps(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: in_sequence([remove_last_step, remove_last_step, remove_last_step])
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([], self.environment)

    def test_shuffle_steps(self):
        def mock_random_shuffle(iterable):
            result = list()
            result.append(iterable[2])
            result.append(iterable[0])
            result.append(iterable[1])
            return result

        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.shuffle = Mock(side_effect=mock_random_shuffle)

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: shuffle_steps
        }

        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([3, 1, 2], self.environment)

    def test_swap_if_blocks(self):

        test_advice = {
            ExampleWorkflow.method_containing_if: swap_if_blocks
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_containing_if()
        self.assertEqual([2], self.environment)

    def test_choose_from(self):
        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.uniform = Mock(side_effect=[0.75, 0.75])

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: choose_from([(0.5, identity), (0.5, remove_last_step)])
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.target.method_for_fuzzing()
        self.assertEqual([1, 2, 1, 2], self.environment)

    def test_in_sequence(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: in_sequence([remove_last_step, remove_last_step])
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([1], self.environment)

    def test_on_condition_that(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: on_condition_that(True, remove_last_step)
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([1, 2], self.environment)

    def test_on_condition_that_with_function(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: on_condition_that(lambda: False, remove_last_step)
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEqual([1, 2, 3], self.environment)

    def test_replace_condition(self):

        test_advice = {
            ExampleWorkflow.method_containing_if: replace_condition_with('1 is 2')
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_containing_if()
        self.assertEquals([2], self.environment)

    def test_replace_condition_with_function(self):

        test_advice = {
            ExampleWorkflow.method_containing_if: replace_condition_with(lambda: False)
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_containing_if()
        self.assertEquals([2], self.environment)

    def test_replace_condition_with_literal(self):

        test_advice = {
            ExampleWorkflow.method_containing_if: replace_condition_with(False)
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_containing_if()
        self.assertEquals([2], self.environment)
        pass

    def test_make_nested_fuzzing_call(self):

        test_advice = {
            ExampleWorkflow.make_nested_fuzzing_call: remove_last_step,
            ExampleWorkflow.nested_method_call: remove_last_step
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.make_nested_fuzzing_call()
        self.assertEquals([1, 3], self.environment)

    def test_replace_iterator(self):

        test_advice = {
            ExampleWorkflow.method_containing_iterator:  replace_for_iterator_with([3, 2, 1])
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_containing_iterator()
        self.assertEquals([3, 2, 1], self.environment)

    def test_apply_fuzzer_to_nested_statements(self):

        test_advice = {
            ExampleWorkflow.method_containing_for_and_nested_try:
                recurse_into_nested_steps(remove_last_step, target_structures={ast.For, ast.TryExcept})
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_containing_for_and_nested_try()
        self.assertEquals([0, 1, 2, 7], self.environment)
        pass

    def test_mangled_function_excluding_control_structures(self):

        test_advice = {
            ExampleWorkflow.method_containing_if_followed_by_for:
                filter_steps(exclude_control_structures({ast.For}), remove_last_step)
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_containing_if_followed_by_for()
        self.assertEquals([1, 2], self.environment)

    def test_mangled_function_invert_filter(self):

        test_advice = {
            ExampleWorkflow.method_for_fuzzing_that_returns_4:
                filter_steps(invert(choose_last_step), replace_steps_with_passes)
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        result = self.target.method_for_fuzzing_that_returns_4()
        self.assertEquals(4, result)
        self.assertEquals(self.environment, [])

    def test_mangled_function_invert_invert_filter(self):
        test_advice = {
            ExampleWorkflow.method_for_fuzzing_that_returns_4:
                filter_steps(invert(invert(choose_last_step)), replace_steps_with_passes)
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        result = self.target.method_for_fuzzing_that_returns_4()
        self.assertEquals(None, result)
        self.assertEquals(self.environment, [1, 2, 3])

    def test_become_distracted(self):
        fuzzi_moss.core_fuzzers.fuzzi_moss_random = Mock(spec=Random)
        fuzzi_moss.core_fuzzers.fuzzi_moss_random.random = Mock(side_effect=[0.75])

        test_advice = {
            ExampleWorkflow.method_for_fuzzing: become_distracted(lambda p: 1 if p < 0.5 else 2)
        }
        fuzz_clazz(ExampleWorkflow, test_advice)

        self.target.method_for_fuzzing()
        self.assertEquals(self.environment, [1])

if __name__ == '__main__':
    unittest.main()