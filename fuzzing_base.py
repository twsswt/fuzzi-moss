import environment, random, ast, inspect

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

    def __init__(self, mutation_type):
        self.mutation_type = mutation_type

    def __call__(self, func):
        def wrap(*args, **kwargs):

            if environment.resources["mutating"] is True:

                # Load function source from mutate.cache if available
                if func.func_name in mutate.cache.keys():
                    func_source = mutate.cache[func.func_name]
                else:
                    func_source = inspect.getsource(func)
                    mutate.cache[func.func_name] = func_source
                # Create function source
                func_source = ''.join(func_source) + '\n' + func.func_name + '_mod' + '()'
                # Mutate using the new mutator class
                mutator = Mutator(self.mutation_type)
                abstract_syntax_tree = ast.parse(func_source)
                mutated_func_uncompiled = mutator.visit(abstract_syntax_tree)
                mutated_func = func
                mutated_func.func_code = compile(mutated_func_uncompiled, inspect.getsourcefile(func), 'exec')
                mutate.cache[(func, self.mutation_type)] = mutated_func
                mutated_func(*args, **kwargs)
            else:
                func(*args, **kwargs)
        return wrap

    @staticmethod
    def reset():
        mutate.cache = {}