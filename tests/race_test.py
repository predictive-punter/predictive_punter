def calculate_value(race, places):
    """Calculate the value of the race for the winning combination with the specified number of places"""

    value = 0.00

    combinations = race.get_winning_combinations(places)
    for combination in combinations:
        combination_value = 1.00
        for runner in combination:
            combination_value *= runner.starting_price
        value += combination_value - 1.00

    return value


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


def test_win_value(race):
    """The win_value property should return the sum of the starting prices of each winner less the number of winners"""

    assert race.win_value == calculate_value(race, 1)


def test_exacta_value(race):
    """The exacta_value property should return the sum of the products of the starting prices for the first and second placed runners in each winning combination, less the number of winning combinations"""

    assert race.exacta_value == calculate_value(race, 2)


def test_trifecta_value(race):
    """The trifecta_value property should return the sum of the products of the starting prices for the first, second and third placed runners in each winning combination, less the number of winning combinations"""

    assert race.trifecta_value == calculate_value(race, 3)


def test_first_four_value(race):
    """The first_four_value property should return the sum of the products of the starting prices for the first, second, third and fourth placed runners in each winning combination, less the number of winning combinations"""

    assert race.first_four_value == calculate_value(race, 4)
