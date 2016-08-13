import concurrent.futures
import logging
import threading

import numpy
from sklearn import cross_validation, grid_search, svm

from .profiling_utils import log_time


class Predictor:

    predictor_cache = dict()
    predictor_locks = dict()

    @classmethod
    def get_predictor_lock(cls, race):
        """Get a lock for the predictors for the specified race"""

        if race.similar_races_hash not in cls.predictor_locks:
            cls.predictor_locks[race.similar_races_hash] = threading.RLock()
        return cls.predictor_locks[race.similar_races_hash]

    @classmethod
    def get_predictor(cls, race):
        """Get a predictor for the specified race"""

        with cls.get_predictor_lock(race):

            if race.similar_races_hash not in cls.predictor_cache:
                cls.predictor_cache[race.similar_races_hash] = None

                similar_races = race.similar_races
                if len(similar_races) > 0:
                    similar_races = similar_races[:min(100, len(similar_races))]

                    train_races, test_races = cross_validation.train_test_split(race.similar_races, random_state=1)
                    if len(train_races) > 0 and len(test_races) > 0:

                        train_X = list()
                        train_y = list()
                        for train_race in train_races:
                            for runner in train_race.active_runners:
                                if runner.result is not None:
                                    train_X.append(runner.sample.normalized_query_data)
                                    train_y.append(runner.sample['regression_result'])
                        if len(train_X) > 0:
                            train_X = numpy.array(train_X)
                            train_y = numpy.array(train_y)

                            test_X = list()
                            test_y = list()
                            for test_race in test_races:
                                for runner in test_race.active_runners:
                                    if runner.result is not None:
                                        test_X.append(runner.sample.normalized_query_data)
                                        test_y.append(runner.sample['regression_result'])
                            if len(test_X) > 0:
                                test_X = numpy.array(test_X)
                                test_y = numpy.array(test_y)

                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    futures = list()

                                    param_grid = {
                                        'C':            [0.5, 1.0, 2.0],
                                        'nu':           [0.25, 0.50, 0.75],
                                        'shrinking':    [True, False],
                                        'tol':          [0.01, 0.001, 0.0001]
                                    }
                                    params_list = list(grid_search.ParameterGrid(param_grid))
                                    count = 0
                                    for params in params_list:
                                        count += 1
                                        message = 'generating estimator {count}/{total} with params {params}'.format(count=count, total=len(params_list), params=params)
                                        futures.append(executor.submit(log_time, message, cls.generate_predictor, params, train_X, train_y, test_X, test_y))

                                    for future in concurrent.futures.as_completed(futures):
                                        predictor = future.result()
                                        if predictor is not None:
                                            if cls.predictor_cache[race.similar_races_hash] is None or (predictor[1] > cls.predictor_cache[race.similar_races_hash][1]):
                                                cls.predictor_cache[race.similar_races_hash] = predictor

            return cls.predictor_cache[race.similar_races_hash]

    @classmethod
    def generate_predictor(cls, estimator_params, train_X, train_y, test_X, test_y):
        """Generate a single predictor with the specified params and fitted with the supplied training data"""

        try:
            estimator = svm.NuSVR(**estimator_params)
            estimator.fit(train_X, train_y)
            return estimator, estimator.score(test_X, test_y), len(train_X), len(test_X)
        except BaseException:
            return None
