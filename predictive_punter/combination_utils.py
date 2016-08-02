def get_combinations(picks):
    """Recursively get non-repeating combinations from picks"""

    if len(picks) > 0:

        combinations = []

        next_combinations = get_combinations(picks[1:])
        for item in picks[0]:
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
