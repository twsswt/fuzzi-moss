"""
@author probablytom
@author tws
"""
import ast
import copy
import inspect
import fuzzi_moss
from workflow_transformer import WorkflowTransformer


# noinspection PyPep8Naming
class fuzz(object):
    """
    The general purpose decorator for applying fuzzings to functions containing workflow steps.
    """

    def __init__(self, fuzzer=lambda steps : steps):
        self.fuzz_operator = fuzzer
        self._original_syntax_tree = None

    def __call__(self, func):

        def wrap(*args, **kwargs):

            if not fuzzi_moss.enable_fuzzings:
                return func(*args, **kwargs)

            self.initialise_reference_syntax_tree(func)

            # Mutate using the visitor class.
            fuzzed_syntax_tree = copy.deepcopy(self._original_syntax_tree)
            workflow_transformer = WorkflowTransformer(self.fuzz_operator)
            workflow_transformer.visit(fuzzed_syntax_tree)

            # Compile the newly mutated function into a module and then extract the mutated function definition.
            compiled_module = compile(fuzzed_syntax_tree, inspect.getsourcefile(func), 'exec')

            fuzzed_function = func
            fuzzed_function.func_code = compiled_module.co_consts[0]

            # Execute the mutated function.
            return fuzzed_function(*args, **kwargs)

        return wrap

    def initialise_reference_syntax_tree (self, func):
        if self._original_syntax_tree is None:
            func_source_lines = inspect.getsourcelines(func)[0]

            global_indentation = len(func_source_lines[0]) - len(func_source_lines[0].strip())
            for i in range(len(func_source_lines)):
                func_source_lines[i] = func_source_lines[i][global_indentation-1:]
            
            func_source = ''.join(func_source_lines)
            self._original_syntax_tree = ast.parse(func_source)
