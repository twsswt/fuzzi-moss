"""
@author probablytom
@author tws
"""
import ast
import inspect
from workflow_transformer import WorkflowTransformer


class mutate(object):
    """
    The general purpose decorator for applying mutations to functions containing workflow steps.

    Attributes:
        enable_mutations is be default set to True, but can be set to false to globablly disable mutations.
    """

    _mutation_cache = {}

    enable_mutations = True


    def __init__(self, mutation_provider):
        self.mutation_provider = mutation_provider

    def __call__(self, func):
        def wrap(*args, **kwargs):

            if not mutate.enable_mutations:
                return func(*args, **kwargs)

            mutation_operator = self.mutation_provider

            func_source_lines = inspect.getsourcelines(func)[0]

            while func_source_lines[0][0:4] == '    ':
                for i in range(0, len(func_source_lines)):
                    func_source_lines[i] = func_source_lines[i][4:]

            func_source = ''.join(func_source_lines)

            # Mutate using the visitor class.
            original_syntax_tree = ast.parse(func_source)
            mutation_visitor = WorkflowTransformer(mutation_operator)
            mutated_syntax_tree = mutation_visitor.visit(original_syntax_tree)

            # Compile the newly mutated function into a module and then extract the mutated function definition.
            compiled_module = compile(mutated_syntax_tree, inspect.getsourcefile(func), 'exec')

            mutated_func = func
            mutated_func.func_code = compiled_module.co_consts[0]
            mutate._mutation_cache[(func, mutation_operator)] = mutated_func

            # Execute the mutated function.
            return mutated_func(*args, **kwargs)

        return wrap


    @staticmethod
    def reset():
        mutate._mutation_cache = {}
