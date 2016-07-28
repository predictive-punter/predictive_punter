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


def calculate_value(self, places):
    """Return the value of the winning combinations with the specified number of places for the race"""

    value = 0.00
    for combination in self.get_winning_combinations(places):
        combination_value = 1.00
        for runner in combination:
            combination_value *= runner.starting_price
        value += combination_value - 1.00
    return value

racing_data.Race.calculate_value = calculate_value


@property
def win_value(self):
    """Return the sum of the starting prices of all winning runners less the number of winning runners"""
    
    return self.calculate_value(1)

racing_data.Race.win_value = win_value


@property
def exacta_value(self):
    """Return the sum of the products of the starting prices of first and second placed runners in all winning combinations, less the number of winning combinations"""
    
    return self.calculate_value(2)

racing_data.Race.exacta_value = exacta_value


@property
def trifecta_value(self):
    """Return the sum of the products of the starting prices of first, second and third placed runners in all winning combinations, less the number of winning combinations"""
    
    return self.calculate_value(3)

racing_data.Race.trifecta_value = trifecta_value
