class ExampleWorkflow(object):
    """
    An example workflow class containing functions that can be fuzzed for unit testing.
    """

    def __init__(self, environment):
        self.environment = environment

    def method_for_fuzzing(self):
        self.environment.append(1)
        self.environment.append(2)
        self.environment.append(3)

    def method_that_targets_a_goal(self):

        while len(self.environment) < 5:
            self.environment.append(1)
