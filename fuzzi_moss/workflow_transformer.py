"""
@author probablytom
@author twsswt
"""
import ast


class WorkflowTransformer(ast.NodeTransformer):

    _functions_visited = 0

    def __init__(self, fuzzer=lambda x: x, strip_decorators=True):
        """
        :param fuzzer: a function that takes a list of strings (lines of program code) and returns another
        list of lines.
        :param strip_decorators: removing decorators prevents re-mutation if a function decorated with a mutator is
        called recursively.
        """

        self.strip_decorators = strip_decorators
        self.fuzzer = fuzzer

    def visit_FunctionDef(self, node):
        """
        Applies this visitor's mutation operator to the body of the supplied node.
        NOTE: This will work differently depending on whether the decorator takes arguments.
        """

        # Renaming is necessary so that we don't overwrite Python's object caching.
        node.name += '_mod'

        if self.strip_decorators:
            node.decorator_list = []

        node.body = self.fuzzer(node.body)

        # Now that we've mutated, increment the necessary counters and parse the rest of the tree we're given.
        WorkflowTransformer._functions_visited += 1
        return self.generic_visit(node)
