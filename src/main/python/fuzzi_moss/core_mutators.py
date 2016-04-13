from random import Random

fuzzi_moss_random = Random()

def choose_from (distribution=[(1.0, lambda x: x)]):
    """
    A composite mutator provider that selects a mutation from a probability distribution, represented as (weight,
    mutator function) tuples.
    """
    def _choose_from(lines):
        total_weight = sum(map(lambda t: t[0], distribution))

        p = fuzzi_moss_random.uniform(0.0, total_weight)

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


def identity(steps):
    return steps


def remove_random_step(steps):
    if len(steps) > 1:
        index = fuzzi_moss_random.randint(0, len(steps) - 1)
        del steps[index]
    return steps


def remove_last_step(steps):
    if len(steps) > 1:
        steps.pop()
    return steps


def shuffle_steps(steps):
    return fuzzi_moss_random.shuffle(steps)
