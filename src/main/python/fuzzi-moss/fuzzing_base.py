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

                # Get an appropriate mutator function
                if type(self.mutation_instructions) == FunctionType or type(self.mutation_instructions) == LambdaType:
                    mutator_function = self.mutation_instructions
                elif isinstance(self.mutation_instructions, list):
                    # We've been given a list of mutator functions. Are they tuples of functions and probabilities? To be done here!
                    # For now, we just assume that we're given a list of mutator functions of equal probability. 
                    if isinstance(self.mutation_instructions[0], tuple):
                        # We have a series of tuples of mutator functions and the probabilities that they come up!
                        # We'll do the following.
                        '''
                            Sift each tuple out into the function and the probability. Keep a list of the probabilities and a list of the functions.
                            If the sum of the probabilities are <1, assume we're dealing with probabilities rather than parts and that the identity has been omitted. Add the identity with the remaining probability.
                            Pick a random float between 0 and sum(probabilities), f.
                            Starting from the first probability p0, pick probability pn such that pn-1 is the last probability s.t. pn-1<n. If p0>n, choose p0.
                        '''

                        # Sift through the probabilities
                        functions = []
                        probabilities = []
                        for current_tuple in self.mutation_instructions:
                            functionIndex = 0 if isinstance(current_tuple[0], FunctionType) or isinstance(current_tuple[0], LambdaType) else 1
                            probIndex = 1 - functionIndex
                            functions.append(current_tuple[functionIndex])
                            probabilities.append(current_tuple[probIndex])

                        # Add an identity mutator function if needed, smartly.
                        if sum(probabilities) < 1:  # If we're dealing with probabilities rather than parts and if the identity has been omitted:
                            probabilities.append(1-sum(probabilities))
                            functions.append(lambda x : x)

                        # Pick a random float.
                        f = random.random() * sum(probabilities)

                        # Find the probability chosen
                        choice = 0
                        while choice < len(probabilities):
                            if sum(probabilities[:choice+1]) >= f:
                                break
                            else:
                                choice += 1

                        # Decide on the choice given by the above algorithm.
                        mutator_function = functions[choice]
                    else:
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

def mutate_test_two(lines):
    return lines

@mutate([(0.5, mutate_test)])
def mutated_function():
    print 1
    print 2
    print 3
    print 4
    print 5

if __name__ == "__main__":
    for i in range(10):
        mutated_function()
        print
