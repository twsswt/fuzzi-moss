"""
Core code fuzzing functionality.
@author twsswt
"""
import ast
import copy
import inspect

from core_fuzzers import identity

from workflow_transformer import WorkflowTransformer

_reference_syntax_trees = dict()


def get_reference_syntax_tree(func):
    if not _reference_syntax_trees.has_key(func):
        func_source_lines = inspect.getsourcelines(func)[0]

        global_indentation = len(func_source_lines[0]) - len(func_source_lines[0].strip())
        for i in range(len(func_source_lines)):
            func_source_lines[i] = func_source_lines[i][global_indentation - 1:]

        func_source = ''.join(func_source_lines)
        _reference_syntax_trees[func] = ast.parse(func_source)

    return _reference_syntax_trees[func]


def fuzz_function(reference_function, fuzzer=identity):
    reference_syntax_tree = get_reference_syntax_tree(reference_function)

    fuzzed_syntax_tree = copy.deepcopy(reference_syntax_tree)
    workflow_transformer = WorkflowTransformer(fuzzer)
    workflow_transformer.visit(fuzzed_syntax_tree)

    # Compile the newly mutated function into a module, extract the mutated function code object and replace the
    # reference function's code object for this call.
    compiled_module = compile(fuzzed_syntax_tree, inspect.getsourcefile(reference_function), 'exec')
    reference_function.func_code = compiled_module.co_consts[0]
