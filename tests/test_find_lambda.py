import unittest

import fuzzi_moss.find_lambda


class FindLambdaUnitTest(unittest.TestCase):

    def test_one_lambda(self):
        result = fuzzi_moss.find_lambda.find_lambda_ast(
            'ExampleWorkflow.method_containing_if: replace_condition_with(lambda: False)', lambda: False)
        self.assertEqual('False', result.value.body.id)

    def test_two_lambdas(self):
        result = \
            fuzzi_moss.find_lambda.find_lambda_ast(
                '...in_sequence([replace_condition_with(lambda: False), replace_condition_with(lambda: True)])',
                lambda: True
            )
        self.assertEqual('True', result.value.body.id)
