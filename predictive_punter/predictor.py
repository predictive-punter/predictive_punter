import concurrent.futures
import logging
import threading

import numpy
from sklearn import cross_validation, ensemble, grid_search, linear_model, svm

from .profiling_utils import log_time


class Predictor:

    CLASSIFICATION_TYPES = {
    }

    REGRESSION_TYPES = {
#        svm.SVR:    {   #36
#            'C':            [0.5, 1.0, 2.0],
#            'epsilon':      [0.05, 0.10, 0.20],
#            'shrinking':    [True, False],
#            'tol':          [0.01, 0.001, 0.0001]
#        },
        svm.NuSVR:  {   #36
            'C':            [0.5, 1.0, 2.0],
            'nu':           [0.25, 0.50, 0.75],
            'shrinking':    [True, False],
            'tol':          [0.01, 0.001, 0.0001]
        }
    }

    predictor_cache = dict()
    predictor_locks = dict()

    @classmethod
    def get_predictor_lock(cls, race):
        """Get a lock for the predictors for the specified race"""

        if race.similar_races_hash not in cls.predictor_locks:
            cls.predictor_locks[race.similar_races_hash] = threading.RLock()
        return cls.predictor_locks[race.similar_races_hash]

    @classmethod
    def get_predictors(cls, race):
        """Get a list of predictors for the specified race"""

        with cls.get_predictor_lock(race):

            if race.similar_races_hash not in cls.predictor_cache:
                cls.predictor_cache[race.similar_races_hash] = list()

                train_races, test_races = cross_validation.train_test_split(race.similar_races, random_state=1)
                if len(train_races) > 0 and len(test_races) > 0:

                    train_X = list()
                    train_y_classification = list()
                    train_y_regression = list()
                    train_weights = list()
                    for train_race in train_races:
                        for runner in train_race.active_runners:
                            if runner.result is not None:
                                train_X.append(runner.sample.normalized_query_data)
                                train_y_classification.append(runner.sample['classification_result'])
                                train_y_regression.append(runner.sample['regression_result'])
                                train_weights.append(runner.sample['weight'])
                    if len(train_X) > 0 and (len(train_X) >= len(train_X[0])):

                        train_X = numpy.array(train_X)
                        train_y_classification = numpy.array(train_y_classification)
                        train_y_regression = numpy.array(train_y_regression)
                        train_weights = numpy.array(train_weights)

                        test_X = list()
                        test_y_classification = list()
                        test_y_regression = list()
                        test_weights = list()
                        for test_race in test_races:
                            for runner in test_race.active_runners:
                                if runner.result is not None:
                                    test_X.append(runner.sample.normalized_query_data)
                                    test_y_classification.append(runner.sample['classification_result'])
                                    test_y_regression.append(runner.sample['regression_result'])
                                    test_weights.append(runner.sample['weight'])
                        test_X = numpy.array(test_X)
                        test_y_classification = numpy.array(test_y_classification)
                        test_y_regression = numpy.array(test_y_regression)
                        test_weights = numpy.array(test_weights)

                        for estimator_type in cls.CLASSIFICATION_TYPES:
                            predictors = cls.generate_predictors(estimator_type, cls.CLASSIFICATION_TYPES[estimator_type], train_X, train_y_classification, train_weights, test_X, test_y_classification, test_weights)
                            cls.predictor_cache[race.similar_races_hash].extend(predictors)

                        for estimator_type in cls.REGRESSION_TYPES:
                            predictors = cls.generate_predictors(estimator_type, cls.REGRESSION_TYPES[estimator_type], train_X, train_y_regression, train_weights, test_X, test_y_regression, test_weights)
                            cls.predictor_cache[race.similar_races_hash].extend(predictors)

            return cls.predictor_cache[race.similar_races_hash]

    @classmethod
    def generate_predictors(cls, estimator_type, estimator_params, train_X, train_y, train_weights, test_X, test_y, test_weights):
        """Generate predictors of the specified type for all combinations of the specified params based on the supplied training and testing data"""

        predictors = list()

        params_list = list(grid_search.ParameterGrid(estimator_params))
        count = 1

        for use_weights in (False,):    # removed True

            best_predictor = None

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = list()

                for params in params_list:
                    message = 'generating {estimator_type} {use_weights} ({count}/{total}) with params {estimator_params}'.format(estimator_type=estimator_type.__name__, use_weights='with weights' if use_weights else 'without weights', count=count, total=len(params_list), estimator_params=params)
                    futures.append(executor.submit(log_time, message, cls.generate_predictor, estimator_type, params, train_X, train_y, train_weights if use_weights else None, test_X, test_y, test_weights if use_weights else None))
                    count += 1

                for future in concurrent.futures.as_completed(futures):
                    predictor = future.result()
                    if predictor is not None and (best_predictor is None or predictor[1] > best_predictor[1]):
                        best_predictor = predictor

            if best_predictor is not None:
                logging.debug('Using {estimator_type} with {estimator_params} ({estimator_score})'.format(estimator_type=best_predictor[0].__class__.__name__, estimator_params=best_predictor[0].get_params(), estimator_score=best_predictor[1]))
                predictors.append(best_predictor)

        return predictors

    @classmethod
    def generate_predictor(cls, estimator_type, estimator_params, train_X, train_y, train_weights, test_X, test_y, test_weights):
        """Generate a single predictor of the specified type with the specified params based on the supplied training and testing data"""

        try:
            estimator = estimator_type(**estimator_params)
            estimator.fit(train_X, train_y, sample_weight=train_weights)
            return estimator, estimator.score(test_X, test_y, sample_weight=test_weights), len(train_X), len(test_X)
        except BaseException:
            return None
