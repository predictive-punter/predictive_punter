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
