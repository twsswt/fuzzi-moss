import random
import unittest
from fuzzing_base import mutate
from env import env
import example_model
import copy

class StandardLibraryTests(unittest.TestCase):

    def test_fuzzing_is_functional(self):
        example_model.add_unmutated()
        result1 = copy.copy(env)
        example_model.add_mutated()
        result2 = copy.copy(env)
        print "\nresult1: " + str(result1['result']) + "\tresult2: " + str(result2['result'])
        self.assertNotEqual(result1, result2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
