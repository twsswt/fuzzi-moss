import random

'''

    A set of formats for the structure of a project, a-la omnifocus projects.
    This can be extended using omnifocus parallel projects, if multiple tasks are assigned to the same slice of ticks.

'''

# A sequential project is one where the tasks in the project are listed in a specific order.
# Each task should be available only upon its predecessor's completion.
def sequential(lines):
    return lines

# A single action list is one where tasks in a project can be completed in any order.
# The project acts as a 'bucket' that tasks fall into, and the project is completed when all tasks are done.
# Tasks run one after the other, but in any order.
def single_action_list(lines):
    random.shuffle(lines)
    return lines

'''
def parallel(lines):
    clever concurrency stuff here
'''

