import threading

import numpy
import racing_data
from sklearn import cross_validation, ensemble, linear_model, naive_bayes, svm, tree

from . import __version__
from .profiling_utils import log_time


class Prediction(racing_data.Entity):
    """A prediction represents the best prediction for a specified race's outcome"""

    CLASSIFIER_TYPES = (
        ensemble.AdaBoostClassifier,
        ensemble.BaggingClassifier,
        ensemble.ExtraTreesClassifier,
        ensemble.GradientBoostingClassifier,
        ensemble.RandomForestClassifier,
        linear_model.LogisticRegression,
        linear_model.Perceptron,
        linear_model.RidgeClassifier,
        linear_model.SGDClassifier,
        naive_bayes.GaussianNB,
        svm.SVC,
        svm.NuSVC,
        tree.DecisionTreeClassifier,
        tree.ExtraTreeClassifier
        )

    REGRESSION_TYPES = (
        ensemble.AdaBoostRegressor,
        ensemble.BaggingRegressor,
        ensemble.ExtraTreesRegressor,
        ensemble.GradientBoostingRegressor,
        ensemble.RandomForestRegressor,
        linear_model.LinearRegression,
        linear_model.Ridge,
        linear_model.SGDRegressor,
        svm.SVR,
        svm.NuSVR,
        tree.DecisionTreeRegressor,
        tree.ExtraTreeRegressor
        )

    estimator_cache = dict()
    estimator_locks = dict()

    @classmethod
    def get_estimator_lock(cls, race):
        """Get the lock for the estimator associated with the specified race's similar races hash"""

        if race.similar_races_hash not in cls.estimator_locks:
            cls.estimator_locks[race.similar_races_hash] = threading.RLock()
        return cls.estimator_locks[race.similar_races_hash]

    @classmethod
    def generate_estimators(cls, race):
        """Generate the best classification and regression estimator based on prior races similar to the specified race"""

        with cls.get_estimator_lock(race):

            if race.similar_races_hash not in cls.estimator_cache:
                
                best_classifier = None
                best_regressor = None

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

                    for use_sample_weights in (True, False):

                        for estimator_type in cls.CLASSIFIER_TYPES:

                            message = 'training {estimator_type} ({use_sample_weights}) for {race}'.format(estimator_type=estimator_type.__name__, use_sample_weights=use_sample_weights, race=race)
                            estimator = log_time(message, cls.generate_estimator, estimator_type, True, train_X, train_y_classification, train_weights if use_sample_weights else None, test_X, test_y_classification, test_weights if use_sample_weights else None)
                            if estimator is not None and (best_classifier is None or estimator[3] > best_classifier[3]):
                                best_classifier = estimator

                        for estimator_type in cls.REGRESSION_TYPES:

                            message = 'training {estimator_type} ({use_sample_weights}) for {race}'.format(estimator_type=estimator_type.__name__, use_sample_weights=use_sample_weights, race=race)
                            estimator = log_time(message, cls.generate_estimator, estimator_type, False, train_X, train_y_regression, train_weights if use_sample_weights else None, test_X, test_y_regression, test_weights if use_sample_weights else None)
                            if estimator is not None and (best_regressor is None or estimator[3] > best_regressor[3]):
                                best_regressor = estimator

                cls.estimator_cache[race.similar_races_hash] = list()
                if best_classifier is not None: cls.estimator_cache[race.similar_races_hash].append(best_classifier)
                if best_regressor is not None: cls.estimator_cache[race.similar_races_hash].append(best_regressor)

            return cls.estimator_cache[race.similar_races_hash]

    @classmethod
    def generate_estimator(cls, estimator_type, is_classifier, train_X, train_y, train_weights, test_X, test_y, test_weights):
        """Create and train an estimator of the specified type using the specified training/testing data"""

        try:
            estimator = estimator_type()
            score = None
            if train_weights is None or test_weights is None:
                estimator.fit(train_X, train_y)
                score = estimator.score(test_X, test_y)
            else:
                estimator.fit(train_X, train_y, sample_weight=train_weights)
                score = estimator.score(test_X, test_y, sample_weight=test_weights)
            return estimator, is_classifier, train_weights is not None and test_weights is not None, score, len(train_X), len(test_X)
        except BaseException:
            return None
    
    @classmethod
    def generate_predictions(cls, race):
        """Generate predictions for the specified race"""

        predictions = list()

        estimators = cls.generate_estimators(race)
        for next_estimator in estimators:

            prediction = {
                'estimator_type':       None,
                'picks':                list(),
                'score':                0.0,
                'train_samples':        0,
                'test_samples':         0,
                'use_sample_weights':   None,
                'predictor_version':    __version__
            }
            for place in range(4):
                prediction['picks'].append(list())

            estimator, is_classifier, use_sample_weights, score, train_samples, test_samples = next_estimator

            prediction['estimator_type'] = estimator.__class__.__name__

            estimations = dict()
            for runner in race.active_runners:
                estimation = estimator.predict(numpy.array(runner.sample.normalized_query_data).reshape(1, -1))[0]
                if estimation not in estimations:
                    estimations[estimation] = list()
                estimations[estimation].append(runner)

            if is_classifier:
                for place in range(1, 5):
                    if place in estimations:
                        for runner in estimations[place]:
                            prediction['picks'][place - 1].append(runner['number'])

            else:
                picks = list()
                for estimation in sorted(estimations.keys()):
                    next_place = list()
                    for runner in estimations[estimation]:
                        next_place.append(runner['number'])
                    for count in range(len(next_place)):
                        if len(picks) < 4:
                            picks.append(next_place)
                        else:
                            break
                prediction['picks'] = picks

            prediction['score'] = score

            prediction['train_samples'] = train_samples
            prediction['test_samples'] = test_samples

            prediction['use_sample_weights'] = use_sample_weights

            predictions.append(prediction)

        return predictions

    @property
    def has_expired(self):
        """Expire predictions that were last updated prior to the race with which they are associated"""

        return self['updated_at'] < self.race['updated_at'] or self['predictor_version'].split('.')[0] != __version__.split('.')[0]

    @property
    def race(self):
        """Return the race associated with this prediction"""

        return self.get_cached_property('race', self.provider.get_race_by_prediction, self)

    def is_equivalent_to(self, other_prediction):
        """This prediction is equivalent to other_prediction if both have the same race ID, estimator category value"""

        is_same_category = False
        for category in (self.CLASSIFIER_TYPES, self.REGRESSION_TYPES):
            estimator_types = [estimator_type.__name__ for estimator_type in category]
            if self['estimator_type'] in estimator_types and other_prediction['estimator_type'] in estimator_types:
                is_same_category = True
                break

        return is_same_category and self['race_id'] == other_prediction['race_id']
