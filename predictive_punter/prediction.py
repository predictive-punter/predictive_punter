import threading

import numpy
import racing_data
from sklearn import cross_validation, ensemble


class Prediction(racing_data.Entity):
    """A prediction represents the best prediction for a specified race's outcome"""

    estimator_cache = dict()
    estimator_locks = dict()

    @classmethod
    def get_estimator_lock(cls, race):
        """Get the lock for the estimator associated with the specified race's similar races hash"""

        if race.similar_races_hash not in cls.estimator_locks:
            cls.estimator_locks[race.similar_races_hash] = threading.RLock()
        return cls.estimator_locks[race.similar_races_hash]

    @classmethod
    def generate_estimator(cls, race):
        """Generate an estimator based on prior races similar to the specified race"""

        with cls.get_estimator_lock(race):

            if race.similar_races_hash not in cls.estimator_cache:
                
                best_estimator = None

                train_races, test_races = cross_validation.train_test_split(race.similar_races)
                if len(train_races) > 0 and len(test_races) > 0:

                    train_X = list()
                    train_y_classification = list()
                    train_y_regression = list()
                    train_weights = list()
                    for race in train_races:
                        for runner in race.active_runners:
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
                    for race in test_races:
                        for runner in race.active_runners:
                            if runner.result is not None:
                                test_X.append(runner.sample.normalized_query_data)
                                test_y_classification.append(runner.sample['classification_result'])
                                test_y_regression.append(runner.sample['regression_result'])
                                test_weights.append(runner.sample['weight'])
                    test_X = numpy.array(test_X)
                    test_y_classification = numpy.array(test_y_classification)
                    test_y_regression = numpy.array(test_y_regression)
                    test_weights = numpy.array(test_weights)

                    for use_sample_weights in (False,):

#                       for estimator_type in (
#                           ensemble.AdaBoostClassifier,
#                           ensemble.BaggingClassifier,
#                           ensemble.ExtraTreesClassifier,
#                           ensemble.GradientBoostingClassifier,
#                           ensemble.RandomForestClassifier
#                           ):
#
#                           try:
#                               estimator = estimator_type()
#                               score = None
#                               if use_sample_weights:
#                                   estimator.fit(train_X, train_y_classification, train_weights)
#                                   score = estimator.score(test_X, test_y_classification, test_weights)
#                               else:
#                                   estimator.fit(train_X, train_y_classification)
#                                   score = estimator.score(test_X, test_y_classification)
#                               if best_estimator is None or score > best_estimator[3]:
#                                   best_estimator = estimator, True, use_sample_weights, score, len(train_X), len(test_X)
#                           except BaseException:
#                               pass

                        for estimator_type in (
                            ensemble.AdaBoostRegressor,
                            ensemble.BaggingRegressor,
                            ensemble.ExtraTreesRegressor,
                            ensemble.GradientBoostingRegressor,
                            ensemble.RandomForestRegressor
                            ):

                            try:
                                estimator = estimator_type()
                                score = None
                                if use_sample_weights:
                                    estimator.fit(train_X, train_y_regression, train_weights)
                                    score = estimator.score(test_X, test_y_regression, test_weights)
                                else:
                                    estimator.fit(train_X, train_y_regression)
                                    score = estimator.score(test_X, test_y_regression)
                                if best_estimator is None or score > best_estimator[3]:
                                    best_estimator = estimator, False, use_sample_weights, score, len(train_X), len(test_X)
                            except BaseException:
                                pass

                cls.estimator_cache[race.similar_races_hash] = best_estimator

            return cls.estimator_cache[race.similar_races_hash]
    
    @classmethod
    def generate_prediction(cls, race):
        """Generate a prediction for the specified race"""

        prediction = {
            'estimator_type':       None,
            'picks':                list(),
            'score':                0.0,
            'train_samples':        0,
            'test_samples':         0,
            'use_sample_weights':   None
        }
        for place in range(4):
            prediction['picks'].append(list())

        estimator = cls.generate_estimator(race)
        if estimator is not None:

            estimator, is_classifier, use_sample_weights, score, train_samples, test_samples = estimator

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

        return prediction
