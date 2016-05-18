
"""
@author twsswt
"""
import inspect

from core_fuzzers import *

from function_fuzzer import fuzz_function


def fuzz_clazz(clazz, advice):

    def __fuzzed_getattribute__(self, item):

        attribute = object.__getattribute__(self, item)

        if not (inspect.ismethod(attribute) or inspect.isfunction(attribute)):
            return attribute

        def wrap(*args, **kwargs):

            reference_function = attribute.im_func

            # Ensure that advice key is unbound method.
            advice_key = getattr(attribute.im_class, attribute.func_name)
            fuzzer = advice[advice_key]

            fuzz_function(reference_function, fuzzer)

            # Execute the mutated function.
            return reference_function(self, *args, **kwargs)

        return wrap

    clazz.__getattribute__ = __fuzzed_getattribute__

