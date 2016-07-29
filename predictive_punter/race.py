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

    if len(self.runners) >= places:

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

                dupes = []
                for index in range(len(combinations)):
                    for item in combinations[index]:
                        if len([combo_item for combo_item in combinations[index] if combo_item == item]) > 1:
                            dupes.append(index)
                            break
                for index in sorted(dupes, reverse=True):
                    del combinations[index]

                return combinations

        results = []
        for count in range(places):
            results.append([])

        for runner in self.active_runners:
            if runner.result is not None and runner.result <= len(results):
                results[runner.result - 1].append(runner)

        for index in range(len(results) - 1):
            if len(results[index + 1]) < 1:
                results[index + 1] = list(results[index])

        return [tuple(combination) for combination in get_combinations(results)]

racing_data.Race.get_winning_combinations = get_winning_combinations


def calculate_value(self, places):
    """Return the value of the winning combinations with the specified number of places for the race"""

    value = 0.00

    combinations = self.get_winning_combinations(places)
    if combinations is not None:
        for combination in combinations:
            combination_value = 1.00
            for runner in combination:
                if runner.starting_price is not None:
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


@property
def first_four_value(self):
    """Return the sum of the products of the starting prices of the first, second, third and fourth placed runners in all winning combinations, less the number of winning combinations"""
    
    return self.calculate_value(4)

racing_data.Race.first_four_value = first_four_value


@property
def total_value(self):
    """Return the sum of the win, exacta, trifecta and first four values for this race"""
    
    total_value = 0.0
    for value in (self.win_value, self.exacta_value, self.trifecta_value, self.first_four_value):
        if value is not None:
            total_value += value
    return total_value

racing_data.Race.total_value = total_value
