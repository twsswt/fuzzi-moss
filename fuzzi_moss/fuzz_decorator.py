"""
@author probablytom
@author twsswt
"""
import fuzzi_moss
from function_fuzzer import fuzz_function


# noinspection PyPep8Naming
class fuzz(object):
    """
    A general purpose decorator for applying fuzzings to functions containing workflow steps.
    """

    def __init__(self, fuzzer=lambda steps: steps):
        self.fuzzer = fuzzer
        self._original_syntax_tree = None

    def __call__(self, func):

        def wrap(*args, **kwargs):

            if not fuzzi_moss.enable_fuzzings:
                return func(*args, **kwargs)

            fuzz_function(func, self.fuzzer)

            # Execute the mutated function.
            return func(*args, **kwargs)

        return wrap
