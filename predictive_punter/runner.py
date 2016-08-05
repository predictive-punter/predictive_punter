from datetime import timedelta

import racing_data
from racing_data.constants import ALTERNATIVE_TRACK_NAMES


def calculate_expected_times(self, performance_list_name):
    """Return a tuple containing the minimum, maximum and average expected times based on the specified performance list's momentums"""

    def calculate_expected_time(momentum):
        if momentum is not None:
            return self.actual_distance / (momentum / self.actual_weight)
    
    return tuple([calculate_expected_time(momentum) for momentum in getattr(self, performance_list_name).momentums]) if self.actual_distance is not None else tuple([None, None, None])

racing_data.Runner.calculate_expected_times = calculate_expected_times


@property
def races_per_year(self):
    """Return total number of career starts for the horse divded by the horse's age as at the race date"""

    if self.age is not None and self.age > 0:
        return self.career.starts / self.age

racing_data.Runner.races_per_year = races_per_year


@property
def sample(self):
    """Return the sample for this runner"""

    return self.get_cached_property('sample', self.provider.get_sample_by_runner, self)

racing_data.Runner.sample = sample


@property
def jockey_at_distance(self):
    """Return a PerformanceList containing all prior performances for the jockey within 100m of the current race distance"""

    def generate_jockey_at_distance():
        return racing_data.PerformanceList([performance for performance in self.jockey_career if self.race['distance'] is not None and performance['distance'] is not None and self.race['distance'] - 100 < performance['distance'] < self.race['distance'] + 100])

    return self.get_cached_property('jockey_at_distance', generate_jockey_at_distance)

racing_data.Runner.jockey_at_distance = jockey_at_distance


@property
def jockey_at_distance_on_track(self):
    """Return a PerformanceList containing all prior performances for the jockey within 100m of the current race distance and on the same track"""

    def generate_jockey_at_distance_on_track():
        return racing_data.PerformanceList([performance for performance in self.jockey_at_distance if performance in self.jockey_on_track])

    return self.get_cached_property('jockey_at_distance_on_track', generate_jockey_at_distance_on_track)

racing_data.Runner.jockey_at_distance_on_track = jockey_at_distance_on_track


@property
def jockey_career(self):
    """Return a PerformanceList containing all performances for the jockey prior to the current race date"""

    def generate_jockey_career():
        return racing_data.PerformanceList([performance for performance in self.jockey.performances if performance['date'] < self.race.meet['date']] if self.jockey is not None else list())

    return self.get_cached_property('jockey_career', generate_jockey_career)

racing_data.Runner.jockey_career = jockey_career


@property
def jockey_last_12_months(self):
    """Return a PerformanceList containing all prior performances for the jockey in the last 12 months"""

    def generate_jockey_last_12_months():
        return racing_data.PerformanceList([performance for performance in self.jockey_career if performance['date'] >= self.race.meet['date'] - timedelta(days=365)])

    return self.get_cached_property('jockey_last_12_months', generate_jockey_last_12_months)

racing_data.Runner.jockey_last_12_months = jockey_last_12_months


@property
def jockey_on_firm(self):
    """Return a PerformanceList containing all prior performances for the jockey on FIRM tracks"""

    return self.get_cached_property('jockey_on_firm', self.get_performance_list_jockey_on_track_condition, 'FIRM')

racing_data.Runner.jockey_on_firm = jockey_on_firm


@property
def jockey_on_good(self):
    """Return a PerformanceList containing all prior performances for the jockey on GOOD tracks"""

    return self.get_cached_property('jockey_on_good', self.get_performance_list_jockey_on_track_condition, 'GOOD')

racing_data.Runner.jockey_on_good = jockey_on_good


@property
def jockey_on_heavy(self):
    """Return a PerformanceList containing all prior performances for the jockey on HEAVY tracks"""

    return self.get_cached_property('jockey_on_heavy', self.get_performance_list_jockey_on_track_condition, 'HEAVY')

racing_data.Runner.jockey_on_heavy = jockey_on_heavy


@property
def jockey_on_soft(self):
    """Return a PerformanceList containing all prior performances for the jockey on SOFT tracks"""

    return self.get_cached_property('jockey_on_soft', self.get_performance_list_jockey_on_track_condition, 'SOFT')

racing_data.Runner.jockey_on_soft = jockey_on_soft


@property
def jockey_on_synthetic(self):
    """Return a PerformanceList containing all prior performances for the jockey on SYNTHETIC tracks"""

    return self.get_cached_property('jockey_on_synthetic', self.get_performance_list_jockey_on_track_condition, 'SYNTHETIC')

racing_data.Runner.jockey_on_synthetic = jockey_on_synthetic


@property
def jockey_on_track(self):
    """Return a PerformanceList containing all prior performances for the jockey on the current track"""

    def get_track_names():
        for track_names in ALTERNATIVE_TRACK_NAMES:
            if self.race.meet['track'] in track_names:
                return track_names
        return [self.race.meet['track']]

    def generate_jockey_on_track():
        return racing_data.PerformanceList([performance for performance in self.jockey_career if performance['track'] in get_track_names()])

    return self.get_cached_property('jockey_on_track', generate_jockey_on_track)

racing_data.Runner.jockey_on_track = jockey_on_track


@property
def jockey_on_turf(self):
    """Return a PerformanceList containing all prior performances for the jockey on turf tracks"""

    def generate_jockey_on_turf():
        return racing_data.PerformanceList([performance for performance in self.jockey_career if performance['track_condition'] is not None and 'SYNTHETIC' not in performance['track_condition'].upper()])

    return self.get_cached_property('jockey_on_turf', generate_jockey_on_turf)

racing_data.Runner.jockey_on_turf = jockey_on_turf


def get_performance_list_jockey_on_track_condition(self, track_condition):
    """Return a PerformanceList containing all prior past performances for the jockey on the specified track condition"""

    return racing_data.PerformanceList([performance for performance in self.jockey_career if performance['track_condition'] is not None and track_condition.upper() in performance['track_condition'].upper()])

racing_data.Runner.get_performance_list_jockey_on_track_condition = get_performance_list_jockey_on_track_condition
