import racing_data


@property
def active_runners(self):
    """Return a list of non-scratched runners in the race"""

    def generate_active_runners():
        return [runner for runner in self.runners if runner['is_scratched'] is False]

    return self.get_cached_property('active_runners', generate_active_runners)

racing_data.Race.active_runners = active_runners


def get_winning_combinations(self, places):
    """Return a list of tuples of Runners representing all winning combinations for the specified number of places"""

    def get_combinations(results):

        if len(results) > 0:

            combinations = []

            next_combinations = get_combinations(results[1:])
            for item in results[0]:
                if next_combinations is None:
                    combinations.append([item])
                else:
                    for next_combination in next_combinations:
                        combinations.append([item] + next_combination)

            return combinations

    results = []
    for count in range(places):
        results.append([])

    for runner in self.active_runners:
        if runner.result is not None and runner.result <= len(results):
            results[runner.result - 1].append(runner)

    combinations = get_combinations(results)
    dupes = []
    for index in range(len(combinations)):
        for item in combinations[index]:
            if len([combo_item for combo_item in combinations[index] if combo_item == item]) > 1:
                dupes.append(index)
                break
    for index in sorted(dupes, reverse=True):
        combinations.removeAt(index)

    return [tuple(combination) for combination in combinations]

racing_data.Race.get_winning_combinations = get_winning_combinations


@property
def win_value(self):
    """Return the sum of the starting prices of all winning runners less the number of winning runners"""
    
    win_value = 0.00
    for winning_combination in self.get_winning_combinations(1):
        if winning_combination[0].starting_price is not None:
            win_value += winning_combination[0].starting_price - 1.00
    return win_value

racing_data.Race.win_value = win_value


@property
def exacta_value(self):
    """Return the sum of the products of the starting prices of first and second placed runners in all winning combinations, less the number of winning combinations"""

    exacta_value = 0.00
    for combination in self.get_winning_combinations(2):
        combination_value = 1.00
        for runner in combination:
            combination_value *= runner.starting_price
        exacta_value += combination_value - 1.00
    return exacta_value

racing_data.Race.exacta_value = exacta_value
