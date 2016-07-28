def test_active_runners(race):
    """The active_runners property should return a list containing all non-scratched runners in the race"""

    assert race.active_runners == [runner for runner in race.runners if runner['is_scratched'] is False]


def test_get_winning_combinations(race):
    """The get_winning_combinations method should return a list of tuples of Runners representing all winning combinations for the specified number of places"""

    results = [
        None,
        None,
        None,
        None
    ]
    for runner in race.active_runners:
        if runner.result <= len(results):
            results[runner.result - 1] = runner

    for places in range(1, 5):
        winning_combinations = race.get_winning_combinations(places)
        assert winning_combinations[0] == tuple([results[index] for index in range(places)])
