import racing_data


@property
def active_runners(self):
    """Return a list of non-scratched runners in the race"""

    def generate_active_runners():
        return [runner for runner in self.runners if runner['is_scratched'] is False]

    return self.get_cached_property('active_runners', generate_active_runners)

racing_data.Race.active_runners = active_runners
