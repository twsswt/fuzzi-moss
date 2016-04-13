"""
@author probablytom
@author tws
"""
import ast
import inspect
from workflow_transformer import WorkflowTransformer


class mutate(object):

    mutation_cache = {}

    def __init__(self, mutation_provider):
        self.mutation_provider = mutation_provider

    def __call__(self, func):
        def wrap(*args, **kwargs):

            mutation_operator = self.mutation_provider

            func_source_lines = inspect.getsourcelines(func)[0]

            while func_source_lines[0][0:4] == '    ':
                for i in range(0, len(func_source_lines)):
                    func_source_lines[i] = func_source_lines[i][4:]

            func_source = ''.join(func_source_lines)

            # Mutate using the visitor class.
            mutation_visitor = WorkflowTransformer(mutation_operator)
            abstract_syntax_tree = ast.parse(func_source)
            mutated_func_uncompiled = mutation_visitor.visit(abstract_syntax_tree)

            # Compile the newly mutated function into a module and then extract the mutated function definition.
            compiled_module = compile(mutated_func_uncompiled, inspect.getsourcefile(func), 'exec')

            mutated_func = func
            mutated_func.func_code = compiled_module.co_consts[0]
            mutate.mutation_cache[(func, mutation_operator)] = mutated_func

            # Execute the mutated function.
            return mutated_func(*args, **kwargs)

        return wrap


    @staticmethod
    def reset():
        mutate.mutation_cache = {}
