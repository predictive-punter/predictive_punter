import threading

import numpy
import racing_data
from sklearn import cross_validation, ensemble, linear_model, metrics, svm, tree

from . import __version__
from .profiling_utils import log_time


class Prediction(racing_data.Entity):
    """A prediction represents the best prediction for a specified race's outcome"""

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

    predictor_cache = dict()
    predictor_locks = dict()

    @classmethod
    def get_predictor_lock(cls, race):
        """Get the lock for the estimator associated with the specified race's similar races hash"""

        if race.similar_races_hash not in cls.predictor_locks:
            cls.predictor_locks[race.similar_races_hash] = threading.RLock()
        return cls.predictor_locks[race.similar_races_hash]

    @classmethod
    def generate_predictor(cls, race):
        """Find the best estimator based on prior races similar to the specified race"""

        with cls.get_predictor_lock(race):

            if race.similar_races_hash not in cls.predictor_cache:

                cls.predictor_cache[race.similar_races_hash] = None

                train_races, test_races = cross_validation.train_test_split(race.similar_races)
                if len(train_races) > 0 and len(test_races) > 0:

                    train_X = list()
                    train_y = list()
                    for train_race in train_races:
                        for runner in train_race.active_runners:
                            if runner.result is not None:
                                train_X.append(runner.sample.normalized_query_data)
                                train_y.append(runner.sample['regression_result'])
                    train_X = numpy.array(train_X)
                    train_y = numpy.array(train_y)

                    test_X = list()
                    test_y = list()
                    for test_race in test_races:
                        for runner in test_race.active_runners:
                            if runner.result is not None:
                                test_X.append(runner.sample.normalized_query_data)
                                test_y.append(runner.sample['regression_result'])
                    test_X = numpy.array(test_X)
                    test_y = numpy.array(test_y)

                    for estimator_type in cls.REGRESSION_TYPES:

                        message = 'training {estimator_type} for {race}'.format(estimator_type=estimator_type.__name__, race=race)
                        estimator = log_time(message, cls.generate_estimator, estimator_type, train_X, train_y, test_X, test_y)
                        if estimator is not None and (cls.predictor_cache[race.similar_races_hash] is None or estimator[1] < cls.predictor_cache[race.similar_races_hash][1]):
                            cls.predictor_cache[race.similar_races_hash] = estimator

            return cls.predictor_cache[race.similar_races_hash]

    @classmethod
    def generate_estimator(cls, estimator_type, train_X, train_y, test_X, test_y):
        """Create and train an estimator of the specified type using the specified training/testing data"""

        try:
            estimator = estimator_type()
            estimator.fit(train_X, train_y)
            score = metrics.mean_squared_error(test_y, estimator.predict(test_X))
            return estimator, score
        except BaseException:
            return None
    
    @classmethod
    def generate_prediction(cls, race):
        """Generate a prediction for the specified race"""

        prediction = {
            'estimator_type':       None,
            'picks':                list(),
            'score':                0.0,
            'predictor_version':    __version__
        }
        for place in range(4):
            prediction['picks'].append(list())

        predictor = cls.generate_predictor(race)
        if predictor is not None:

            estimator, prediction['score'] = predictor
            prediction['estimator_type'] = estimator.__class__.__name__

            estimations = dict()
            for runner in race.active_runners:
                estimation = estimator.predict(numpy.array(runner.sample.normalized_query_data).reshape(1, -1))[0]
                if estimation not in estimations:
                    estimations[estimation] = list()
                estimations[estimation].append(runner)

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

        return prediction

    @property
    def has_expired(self):
        """Expire predictions that were last updated prior to the race with which they are associated"""

        return self['updated_at'] < self.race['updated_at'] or self['predictor_version'].split('.')[0] != __version__.split('.')[0]

    @property
    def race(self):
        """Return the race associated with this prediction"""

        return self.get_cached_property('race', self.provider.get_race_by_prediction, self)
