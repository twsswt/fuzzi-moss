"""
@author probablytom
@author twsswt
"""
import ast
from fuzz_formats import sequential


class WorkflowTransformer(ast.NodeTransformer):

    def __init__(self, fuzzer=lambda x: x, strip_decorators=True, format=sequential):
        """
        :param fuzzer: a function that takes a list of strings (lines of program code) and returns another
        list of lines.
        :param strip_decorators: removing decorators prevents re-mutation if a function decorated with a mutator is
        called recursively.
        """

        self.strip_decorators = strip_decorators
        self.fuzzer = fuzzer
        self.format = format

    def visit_FunctionDef(self, node):
        """
        Applies this visitor's mutation operator to the body of the supplied node.
        """

        # Renaming is necessary so that we don't overwrite Python's object caching.
        node.name += '_mod'

        if self.strip_decorators:
            node.decorator_list = []

        node.body = self.format(node.body)  # Should this happen before or after the fuzzing?
        node.body = self.fuzzer(node.body)

        # Now that we've mutated, visit the rest of the tree we're given.
        return self.generic_visit(node)
