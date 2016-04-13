"""
@author probablytom, tws
"""

import random, ast, inspect
from types import *


class ResourcesExpendedException(Exception):
    pass


class FuzzVisitor(ast.NodeTransformer):

    mutants_visited = 0

    def __init__(self, mutation_operator=lambda x: x, strip_decorators=True):
        """
        :param mutation_operator: a function that takes a list of strings (lines of program code) and returns another list of
        lines.
        :param strip_decorators: removing decorators prevents re-mutation if a function decorated with a mutator is
        called recursively.
        """

        self.strip_decorators = strip_decorators
        self.mutation = mutation_operator

    def visit_FunctionDef(self, node):
        """
        Applies this visitor's mutation operator to the body of the supplied node.
        NOTE: This will work differently depending on whether the decorator takes arguments.
        """

        # Renaming is necessary so that we don't overwrite Python's object caching.
        node.name += '_mod'

        if self.strip_decorators:
            node.decorator_list = []

        node.body = self.mutation(node.body)

        # Now that we've mutated, increment the necessary counters and parse the rest of the tree we're given.
        FuzzVisitor.mutants_visited += 1
        return self.generic_visit(node)


class mutate(object):

    source_cache = {}

    mutation_cache = {}

    def __init__(self, mutation_provider):
        self.mutation_provider = mutation_provider

    def __call__(self, func):
        def wrap(*args, **kwargs):

            mutation_operator = self.mutation_provider

            func_source_lines = mutate.get_source_lines(func)

            while func_source_lines[0][0:4] == '    ':
                for i in range(0, len(func_source_lines)):
                    func_source_lines[i] = func_source_lines[i][4:]

            func_source = ''.join(func_source_lines)

            # Mutate using the visitor class.
            mutation_visitor = FuzzVisitor(mutation_operator)
            abstract_syntax_tree = ast.parse(func_source)
            mutated_func_uncompiled = mutation_visitor.visit(abstract_syntax_tree)

            # Compile the newly mutated function into a module and then extract the mutated function definition.
            compiled_module = compile(mutated_func_uncompiled, inspect.getsourcefile(func), 'exec')

            mutated_func = func
            mutated_func.func_code = compiled_module.co_consts[0]
            mutate.mutation_cache[(func, mutation_operator)] = mutated_func

            # Execute the mutated function.
            mutated_func(*args, **kwargs)

        return wrap

    @staticmethod
    def get_source_lines(func):
        """
        Will load function source from mutate.cache if available, or else attempt to retrieve from source.
        :return: a list of lines of code for the specified function.
        """
        if func.func_name not in mutate.source_cache.keys():
            func_source_lines = inspect.getsourcelines(func)[0]
            mutate.source_cache[func.func_name] = func_source_lines

        return mutate.source_cache[func.func_name]


    @staticmethod
    def reset():
        mutate.source_cache = {}
        mutate_mutation_cache = {}


def choose_from (distribution=[(1.0, lambda x: x)]):
    """
    A composite mutator provider that selects a mutation from a probability distribution, represented as (weight,
    mutator function) tuples.
    """
    def _choose_from(lines):
        total_weight = sum(map(lambda t: t[0], distribution))

        p = random.uniform(0.0, total_weight)

        upto = 0.0
        for weight, mutation_operator in distribution:
            upto += weight
            if upto >= p:
                return mutation_operator(lines)

    return _choose_from


def in_sequence(sequence=[]):
    """
    A composite mutator that applies the supplied list of mutant operators in sequence.
    """
    def _in_sequence(lines):
        for mutation_operator in sequence:
            lines = mutation_operator(lines)

        return lines

    return _in_sequence


def remove_random_step(lines):
    if len(lines) > 1:
        index = random.randint(0, len(lines)-1)
        del lines[index]
    return lines


def remove_last_step(lines):
    if len(lines) > 1:
        lines.pop()
    return lines


def shuffle_steps(steps):
    return random.shuffle(steps)


@mutate(choose_from([(0.5, in_sequence([remove_random_step, remove_random_step]))]))
def mangled_function():
    print 1
    print 2
    print 3
    print 4
    print 5


class Bob:

    def __init__(self):
        pass

    @mutate(remove_last_step)
    def testing(self):
        print 4
        print 5
        print 6
        self.test_other()
        print 7

    def test_other(self):
        print "hurrah"

if __name__ == "__main__":
    for i in range(3):
        mangled_function()
        print
    bob = Bob()
    bob.testing()
