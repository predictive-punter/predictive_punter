import racing_data


def calculate_expected_times(self, performance_list_name):
    """Return a tuple containing the minimum, maximum and average expected times based on the specified performance list's momentums"""
    
    return tuple([self.actual_distance / (momentum / self.actual_weight) for momentum in getattr(self, performance_list_name).momentums])

racing_data.Runner.calculate_expected_times = calculate_expected_times


@property
def races_per_year(self):
    """Return total number of career starts for the horse divded by the horse's age as at the race date"""

    return self.career.starts / self.age

racing_data.Runner.races_per_year = races_per_year
