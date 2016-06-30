"""
Front end API for the fuzzi_moss library.
"""


from .audit import fuzzer_invocations, reset_invocation_counters
from .config import fuzzi_moss_random
from .fuzz_decorator import fuzz
from .fuzz_weaver import fuzz_clazz, fuzz_module

