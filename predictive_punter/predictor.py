from datetime import datetime
import pickle
import threading

import numpy
import racing_data
from sklearn import linear_model


class Predictor(racing_data.Entity):
    """A predictor wraps a scikit-learn estimator in a persistence framework"""

    CLASSIFICATION_TYPES = (
        linear_model.SGDClassifier,
        )

    REGRESSION_TYPES = (
        linear_model.SGDRegressor,
        )

    predictor_locks = dict()

    @classmethod
    def get_predictor_lock(cls, race):
        """Get a lock for the predictors for races similar to the specified race"""

        if race.similar_races_hash not in cls.predictor_locks:
            cls.predictor_locks[race.similar_races_hash] = threading.RLock()
        return cls.predictor_locks[race.similar_races_hash]
    
    @classmethod
    def get_predictors(cls, race):
        """Get a list of appropriate predictors for the specified race"""

        with cls.get_predictor_lock(race):

            predictors = race.provider.find(Predictor, {'similar_races_hash': race.similar_races_hash}, None)
            if len(predictors) < 1:
                predictors = cls.generate_predictors(race)

            for predictor in predictors:
                if predictor['last_training_date'] is None or predictor['last_training_date'] < race.meet['date']:

                    train_X = list()
                    train_y = list()
                    train_weights = list()

                    start_time = {'$lt': race.meet['date']}
                    if predictor['last_training_date'] is not None:
                        start_time['$gte'] = predictor['last_training_date']
                    similar_races = predictor.provider.find(racing_data.Race, {'entry_conditions': race['entry_conditions'], 'group': race['group'], 'start_time': start_time, 'track_condition': race['track_condition']}, None)
                    for similar_race in similar_races:
                        for active_runner in similar_race.active_runners:
                            if active_runner.result is not None:
                                train_X.append(active_runner.sample.normalized_query_data)
                                if predictor['is_classifier']:
                                    train_y.append(active_runner.sample['classification_result'])
                                else:
                                    train_y.append(active_runner.sample['regression_result'])
                                train_weights.append(active_runner.sample['weight'])

                    if len(train_X) > 0:

                        train_X = numpy.array(train_X)
                        train_y = numpy.array(train_y)
                        train_weights = numpy.array(train_weights)

                        try:
                            predictor.estimator.fit(train_X, train_y, sample_weight=train_weights if predictor['uses_sample_weights'] else None)
                        except BaseException:
                            pass
                        else:
                            predictor['last_training_date'] = race.meet['date']
                            predictor.save()

            return predictors

    @classmethod
    def generate_predictors(cls, race):
        """Generate predictors for the specified race"""

        predictors = list()

        for uses_sample_weights in (True, False):

            for estimator_type in cls.CLASSIFICATION_TYPES:
                predictors.append(cls.generate_predictor(race, estimator_type, True, uses_sample_weights))

            for estimator_type in cls.REGRESSION_TYPES:
                predictors.append(cls.generate_predictor(race, estimator_type, False, uses_sample_weights))

        return predictors

    @classmethod
    def generate_predictor(cls, race, estimator_type, is_classifier, uses_sample_weights):
        """Generate and train a predictor of the specified type using the provided training data"""

        predictor = Predictor(race.provider, None, is_classifier=is_classifier, last_training_date=None, similar_races_hash=race.similar_races_hash, uses_sample_weights=uses_sample_weights)
        predictor.estimator = estimator_type(warm_start=True)
        predictor.save()

        return predictor

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.estimator = None
        if 'estimator' in self and self['estimator'] is not None:
            self.estimator = pickle.loads(self['estimator'])

    def save(self):
        """Save this predictor to the database"""

        self['estimator'] = None
        if self.estimator is not None:
            self['estimator'] = pickle.dumps(self.estimator)

        self['updated_at'] = datetime.now(self.provider.local_timezone)

        self.provider.save(self)
