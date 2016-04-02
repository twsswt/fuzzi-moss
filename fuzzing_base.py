import environment, random, ast, inspect
from types import *

class ResourcesExpendedException(Exception):
    pass


class Mutator(ast.NodeTransformer):

    mutants_visited = 0

    # The mutation argument is a function that takes a list of lines and returns another list of lines.
    def __init__(self, mutation=lambda x: x, strip_decorators = True):
        self.strip_decorators = strip_decorators
        self.mutation = mutation

    #NOTE: This will work differently depending on whether the decorator takes arguments.
    def visit_FunctionDef(self, node):

        # Fix the randomisation to the environment
        random.seed(environment.resources["seed"])

        # Mutation algorithm!
        node.name += '_mod'   # so we don't overwrite Python's object caching
        # Remove decorators if we need to So we don't re-decorate when we run the mutated function, mutating recursively
        if self.strip_decorators:
            node.decorator_list = []
        # Mutate! self.mutation is a function that takes a list of line objects and returns a list of line objects.
        node.body = self.mutation(node.body)

        # Now that we've mutated, increment the necessary counters and parse the rest of the tree we're given
        Mutator.mutants_visited += 1
        environment.resources["seed"] += 1
        return self.generic_visit(node)


class mutate(object):

    cache = {}

    def __init__(self, mutation_instructions):
        self.mutation_instructions = mutation_instructions

    def __call__(self, func):
        def wrap(*args, **kwargs):

            if environment.resources["mutating"] is True:

                # Initialise the mutator function into something harmless.
                mutator_function = lambda x: x

                print type(self.mutation_instructions)

                # Get an appropriate mutator function
                if type(self.mutation_instructions) == FunctionType or type(self.mutation_instructions) == LambdaType:
                    mutator_function = self.mutation_instructions
                elif isinstance(self.mutation_instructions, list):
                    # We've been given a list of mutator functions. Are they tuples of functions and probabilities? To be done here!
                    # For now, we just assume that we're given a list of mutator functions of equal probability. 
                    mutator_function = random.choice(self.mutation_instructions)
                else:
                    print "None of the above!"

                # Load function source from mutate.cache if available
                if func.func_name in mutate.cache.keys():
                    func_source = mutate.cache[func.func_name]
                else:
                    func_source = inspect.getsource(func)
                    mutate.cache[func.func_name] = func_source
                # Create function source
                func_source = ''.join(func_source) + '\n' + func.func_name + '_mod' + '()'
                # Mutate using the new mutator class
                mutator = Mutator(mutator_function)
                abstract_syntax_tree = ast.parse(func_source)
                mutated_func_uncompiled = mutator.visit(abstract_syntax_tree)
                mutated_func = func
                mutated_func.func_code = compile(mutated_func_uncompiled, inspect.getsourcefile(func), 'exec')
                mutate.cache[(func, mutator_function)] = mutated_func
                mutated_func(*args, **kwargs)
            else:
                func(*args, **kwargs)
        return wrap

    @staticmethod
    def reset():
        mutate.cache = {}


def mutate_test(lines):
    if len(lines) > 1 :#and random.choice([True, False]):
        lines.remove(random.choice(lines))
    return lines
@mutate([mutate_test])
def mutated_function():
    print 1
    print 2
    print 3
    print 4
    print 5
if __name__ == "__main__":
    mutated_function()
