import numpy
import predictive_punter
import sklearn.preprocessing


def test_expected_values(runner):
    """The generate_sample method should return a dictionary containing all expected values"""

    all_results = [runner.result] + [other_runner.result for other_runner in runner.race.active_runners if other_runner['_id'] != runner['_id']]

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

    expected_values = {
        'raw_query_data':           raw_query_data,
        'fixed_query_data':         None,
        'regression_result':        sklearn.preprocessing.normalize(numpy.array(all_results).reshape(1, -1))[0, 0],
        'classification_result':    runner.result if runner.result is not None and 1 <= runner.result <= 4 else 5,
        'weight':                   runner.race.total_value,
        'predictor_version':        predictive_punter.__version__
    }

    generated_values = predictive_punter.Sample.generate_sample(runner)

    for key in expected_values:
        assert generated_values[key] == expected_values[key]
