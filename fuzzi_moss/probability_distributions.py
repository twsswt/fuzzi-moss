
def steps_to_remove_distribution(clock, random):

    def _probability_distribution(max_steps):

        probability = random.uniform(0.0, 1.0)

        remaining_time = clock.max_ticks - clock.current_tick

        n = 1

        def threshold():
            return (1.0 - 1.0 / (n + 1)) ** (1.0 / (remaining_time + 1))

        while probability > threshold() and n <= max_steps:
            n += 1

        return n - 1

    return _probability_distribution


def default_distracted_probability_mass_function(conscientiousness=1):
    """
    Realises a 2-point PMF (True, False) that takes a duration and probability as parameters.
    """
    def _default_distracted_probability_mass_function(duration, probability):
        threshold = 1.0 / (duration + 1) ** (1.0 / conscientiousness)
        return probability < threshold

    return _default_distracted_probability_mass_function



