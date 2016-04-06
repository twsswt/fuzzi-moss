import random
from fuzzing_base import mutate
from env import env

def remove_a_line(lines):
    lines.remove(random.choice(lines))
    return lines

def remove_two_lines(lines):
    lines.remove(random.choice(lines))
    lines.remove(random.choice(lines))
    return lines


def setup_env():
    global env
    env = {}
    env["result"] = 0

def add_unmutated():
    env["result"] = 0
    env["result"] += 1
    env["result"] += 2
    env["result"] += 4
    env["result"] += 8
    env["result"] += 16

@mutate(remove_a_line)
def add_mutated():
    env["result"] = 0
    env["result"] += 1
    env["result"] += 2
    env["result"] += 4
    env["result"] += 8
    env["result"] += 16

@mutate([remove_a_line, remove_two_lines])
def add_mutated_two_types():
    env["result"] = 0
    env["result"] += 1
    env["result"] += 2
    env["result"] += 4
    env["result"] += 8
    env["result"] += 16

@mutate([(remove_a_line, 0.8), (remove_two_lines, 0.2)])
def add_mutated_two_types_with_probabilities():
    env["result"] = 0
    env["result"] += 1
    env["result"] += 2
    env["result"] += 4
    env["result"] += 8
    env["result"] += 16

@mutate([(remove_a_line, 0.5), (remove_two_lines, 0.2)])
def add_mutated_two_types_with_unbalanced_probabilities():
    env["result"] = 0
    env["result"] += 1
    env["result"] += 2
    env["result"] += 4
    env["result"] += 8
    env["result"] += 16
