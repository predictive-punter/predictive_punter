import racing_data


def calculate_expected_times(self, performance_list_name):
    """Return a tuple containing the minimum, maximum and average expected times based on the specified performance list's momentums"""
    
    return tuple([self.actual_distance / (momentum / self.actual_weight) for momentum in getattr(self, performance_list_name).momentums])

racing_data.Runner.calculate_expected_times = calculate_expected_times
