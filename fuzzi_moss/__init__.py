"""
Front end API for the fuzzi_moss library.
Attributes:
    enable_fuzzings is by default set to True, but can be set to false to globally disable fuzzing.
"""

from fuzzi_moss.core_fuzzers import *
import fuzzi_moss.core_fuzzers
from fuzzi_moss.fuzz_decorator import fuzz
from fuzzi_moss.fuzz_weaver import fuzz_clazz

enable_fuzzings = False
