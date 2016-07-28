import numpy
import racing_data
import sklearn.preprocessing

from . import __version__


class Sample(racing_data.Entity):
    """A sample represents a single row of query data for a predictor"""

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
            'fixed_query_data':         None,
            'regression_result':        regression_result,
            'classification_result':    runner.result if runner.result is not None and 1 <= runner.result <= 4 else 5,
            'weight':                   runner.race.total_value,
            'predictor_version':        __version__
        }

    @property
    def fixed_query_data(self):
        """Impute and normalize the raw query data alongside the raw query data for all other active runners in the race"""

        if self['fixed_query_data'] is None:
            
            all_query_data = numpy.asarray([self['raw_query_data']] + [runner.sample['raw_query_data'] for runner in self.runner.race.active_runners if runner['_id'] != self.runner['_id']])

            imputer = sklearn.preprocessing.Imputer(missing_values='NaN', strategy='median', axis=0)
            imputed_query_data = imputer.fit_transform(all_query_data)

            self['fixed_query_data'] = sklearn.preprocessing.normalize(imputed_query_data, axis=0).tolist()[0]

            self.provider.save(self)

        return self['fixed_query_data']

    @property
    def has_expired(self):
        """Expire samples sourced from an incompatible predictor version"""

        return self['predictor_version'].split('.')[0] != __version__.split('.')[0]

    @property
    def runner(self):
        """Return the runner associated with this sample"""

        return self.get_cached_property('runner', self.provider.get_runner_by_sample, self)
