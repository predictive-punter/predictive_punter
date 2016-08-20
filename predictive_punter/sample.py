import threading

import numpy
import racing_data
import sklearn.preprocessing

from . import __version__


class Sample(racing_data.Entity):
    """A sample represents a single row of query data for a predictor"""

    IMPUTERS = list()
    for key in ('barrier', 'number', 'weight'):
        IMPUTERS.append(max)
    for key in ('age', 'carrying', 'races_per_year', 'spell', 'up'):
        IMPUTERS.append(max)
    for key1 in ('at_distance', 'at_distance_on_track', 'at_up', 'career', 'last_10', 'last_12_months', 'on_firm', 'on_good', 'on_heavy', 'on_soft', 'on_synthetic', 'on_track', 'on_turf', 'since_rest', 'with_jockey'):
        for count in range(3):
            IMPUTERS.append(max)
        IMPUTERS.append(max)
        for key2 in ('earnings_potential', 'fourth_pct', 'result_potential', 'roi', 'second_pct', 'starts', 'third_pct', 'win_pct'):
            IMPUTERS.append(min)
        for count in range(3):
            IMPUTERS.append(max)

    normalizer_locks = dict()

    @classmethod
    def generate_sample(cls, runner):
        """Generate a new sample for the specified runner"""

        raw_query_data = []
        for key in ('barrier', 'number', 'weight'):
            raw_query_data.append(runner[key])
        for key in ('age', 'carrying', 'races_per_year', 'spell', 'up'):
            raw_query_data.append(getattr(runner, key))
        for key1 in ('at_distance', 'at_distance_on_track', 'at_up', 'career', 'last_10', 'last_12_months', 'on_firm', 'on_good', 'on_heavy', 'on_soft', 'on_synthetic', 'on_track', 'on_turf', 'since_rest', 'with_jockey'):
            raw_query_data.extend(runner.calculate_expected_times(key1))
            performance_list = getattr(runner, key1)
            for key2 in ('earnings', 'earnings_potential', 'fourth_pct', 'result_potential', 'roi', 'second_pct', 'starts', 'third_pct', 'win_pct'):
                raw_query_data.append(getattr(performance_list, key2))
            raw_query_data.extend(performance_list.starting_prices)

        regression_result = None
        if runner.result is not None:
            all_results = [runner.result] + [other_runner.result for other_runner in runner.race.active_runners if other_runner['_id'] != runner['_id'] and other_runner.result is not None]
            try:
                regression_result = sklearn.preprocessing.normalize(numpy.array(all_results).reshape(1,-1))[0,0]
            except BaseException:
                pass

        return {
            'raw_query_data':           raw_query_data,
            'imputed_query_data':       None,
            'normalized_query_data':    None,
            'regression_result':        regression_result,
            'classification_result':    runner.result if runner.result is not None and 1 <= runner.result <= 4 else 5,
            'weight':                   runner.race.total_value,
            'predictor_version':        __version__
        }

    @classmethod
    def get_normalizer_lock(cls, race):
        """Get the normalizer lock for the specified race"""

        if race['_id'] not in cls.normalizer_locks:
            cls.normalizer_locks[race['_id']] = threading.RLock()

        return cls.normalizer_locks[race['_id']]

    @property
    def imputed_query_data(self):
        """Impute the raw query data alongside the raw query data for all other active runners in the race"""

        if self['imputed_query_data'] is None:

            all_query_data = [list(self['raw_query_data'])] + [runner.sample['raw_query_data'] for runner in self.runner.race.active_runners if runner['_id'] != self.runner['_id']]

            for index in range(len(all_query_data[0])):
                if all_query_data[0][index] is None:
                    other_values = [value[index] for value in all_query_data[1:] if value[index] is not None]
                    if len(other_values) > 0:
                        all_query_data[0][index] = self.IMPUTERS[index](other_values)
                    else:
                        all_query_data[0][index] = 0.0

            self['imputed_query_data'] = all_query_data[0]
            self.provider.save(self)

        return self['imputed_query_data']

    @property
    def normalized_query_data(self):
        """Normalize the imputed query data alongside the imputed query data for all other active runners in the race"""

        with self.get_normalizer_lock(self.runner.race):

            if self['normalized_query_data'] is None:
                
                all_query_data = numpy.asarray([self.imputed_query_data] + [runner.sample.imputed_query_data for runner in self.runner.race.active_runners if runner['_id'] != self.runner['_id']])
                self['normalized_query_data'] = sklearn.preprocessing.normalize(all_query_data, axis=0).tolist()[0]
                self.provider.save(self)

            return self['normalized_query_data']

    @property
    def has_expired(self):
        """Expire samples sourced from an incompatible predictor version"""

        return self['predictor_version'].split('.')[0] != __version__.split('.')[0]

    @property
    def runner(self):
        """Return the runner associated with this sample"""

        return self.get_cached_property('runner', self.provider.get_runner_by_sample, self)
