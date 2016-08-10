import threading

import numpy
from sklearn import cross_validation, ensemble, grid_search

from .profiling_utils import log_time


class Predictor:

    CLASSIFICATION_TYPES = {
#        ensemble.AdaBoostClassifier:    {   #18
#            'algorithm':        ['SAMME', 'SAMME.R'],
#            'learning_rate':    [0.5, 1.0, 2.0],
#            'n_estimators':     [25, 50, 100],
#            'random_state':     [1]
#        },
#        ensemble.BaggingClassifier:     {   #12
#            'max_features':     [0.5, 1.0],
#            'max_samples':      [0.5, 1.0],
#            'n_estimators':     [5, 10, 20],
#            'random_state':     [1]
#        },
#        ensemble.ExtraTreesClassifier:  {   #36
#            'class_weight':     ['balanced', 'balanced_subsample'],
#            'criterion':        ['gini' ,'entropy'],
#            'max_features':     ['sqrt', 'log2', None],
#            'n_estimators':     [5, 10, 20],
#            'random_state':     [1]
#        },
#        ensemble.GradientBoostingClassifier:    {   #54
#            'learning_rate':    [0.05, 0.1, 0.2],
#            'loss':             ['deviance', 'exponential'],
#            'max_features':     ['sqrt', 'log2', None],
#            'n_estimators':     [50, 100, 200],
#            'random_state':     [1]
#        },
#        ensemble.RandomForestClassifier:        {   #36
#            'class_weight':     ['balanced', 'balanced_subsample'],
#            'criterion':        ['gini', 'entropy'],
#            'max_features':     ['sqrt', 'log2', None],
#            'n_estimators':     [5, 10, 20],
#            'random_state':     [1]
#        }
    }

    REGRESSION_TYPES = {
#        ensemble.AdaBoostRegressor:     {   #27
#            'learning_rate':    [0.5, 1.0, 2.0],
#            'loss':             ['linear', 'square', 'exponential'],
#            'n_estimators':     [25, 50, 100],
#            'random_state':     [1]
#        },
        ensemble.BaggingRegressor:      {   #12
            'max_features':     [0.5, 1.0],
            'max_samples':      [0.5, 1.0],
            'n_estimators':     [5, 10, 20],
            'random_state':     [1]
        },
        ensemble.ExtraTreesRegressor:   {   #9
            'max_features':     ['sqrt', 'log2', None],
            'n_estimators':     [5, 10, 20],
            'random_state':     [1]
        },
#        ensemble.GradientBoostingRegressor: {   #108
#            'learning_rate':    [0.05, 0.1, 0.2],
#            'loss':             ['ls', 'lad', 'huber', 'quantile'],
#            'max_features':     ['sqrt', 'log2', None],
#            'n_estimators':     [50, 100, 200],
#            'random_state':     [1]
#        },
#        ensemble.RandomForestRegressor:     {   #9
#            'max_features':     ['sqrt', 'log2', None],
#            'n_estimators':     [5, 10, 20],
#            'random_state':     [1]
#        }
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

                train_races, test_races = cross_validation.train_test_split(race.similar_races)
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

                        for use_weights in (True, False):

                            for estimator_type in cls.CLASSIFICATION_TYPES:
                                predictors = cls.generate_predictors(estimator_type, cls.CLASSIFICATION_TYPES[estimator_type], train_X, train_y_classification, train_weights if use_weights else None, test_X, test_y_classification, test_weights if use_weights else None)
                                cls.predictor_cache[race.similar_races_hash].extend(predictors)

                            for estimator_type in cls.REGRESSION_TYPES:
                                predictors = cls.generate_predictors(estimator_type, cls.REGRESSION_TYPES[estimator_type], train_X, train_y_regression, train_weights if use_weights else None, test_X, test_y_regression, test_weights if use_weights else None)
                                cls.predictor_cache[race.similar_races_hash].extend(predictors)

            return cls.predictor_cache[race.similar_races_hash]

    @classmethod
    def generate_predictors(cls, estimator_type, estimator_params, train_X, train_y, train_weights, test_X, test_y, test_weights):
        """Generate predictors of the specified type for all combinations of the specified params based on the supplied training and testing data"""

        predictors = list()

        params_list = list(grid_search.ParameterGrid(estimator_params))
        count = 1
        for params in params_list:
            message = 'generating {estimator_type} ({count}/{total}) with params {estimator_params}'.format(estimator_type=estimator_type.__name__, count=count, total=len(params_list), estimator_params=params)
            predictor = log_time(message, cls.generate_predictor, estimator_type, params, train_X, train_y, train_weights, test_X, test_y, test_weights)
            if predictor is not None:
                predictors.append(predictor)
            count += 1

        return predictors

    @classmethod
    def generate_predictor(cls, estimator_type, estimator_params, train_X, train_y, train_weights, test_X, test_y, test_weights):
        """Generate a single predictor of the specified type with the specified params based on the supplied training and testing data"""

        try:
            estimator = estimator_type(**estimator_params)
            estimator.fit(train_X, train_y, sample_weight=train_weights)
            return estimator, estimator.score(test_X, test_y, sample_weight=test_weights)
        except BaseException:
            return None
