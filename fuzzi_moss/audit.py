"""
Logging management routines for fuzzer invocations.
@author twsswt
"""

fuzzer_invocations = dict()


def reset_invocation_counters():
    global fuzzer_invocations
    fuzzer_invocations.clear()


def log_invocation(func):
    def func_wrapper(*args, **kwargs):
        fuzzer_invocations[func] = fuzzer_invocations.get(func,0) + 1
        return func(*args,**kwargs)
    return func_wrapper
