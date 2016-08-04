from datetime import datetime
import pickle
import threading

import numpy
import racing_data
from sklearn import grid_search, linear_model


class Predictor(racing_data.Entity):
    """A predictor wraps a scikit-learn estimator in a persistence framework"""

    CLASSIFICATION_PARAMS = {
        'class_weight': ['balanced', None],
        'loss':         ['hinge', 'log', 'modified_huber', 'perceptron', 'squared_hinge'],
        'penalty':      ['elasticnet', 'l1', 'l2', 'none']
    }
    CLASSIFICATION_PARAM_GRID = list(grid_search.ParameterGrid(CLASSIFICATION_PARAMS))

    REGRESSION_PARAMS = {
        'loss':     ['epsilon_insensitive', 'huber', 'squared_epsilon_insensitive', 'squared_loss'],
        'penalty':  ['elasticnet', 'l1', 'l2', 'none']
    }
    REGRESSION_PARAM_GRID = list(grid_search.ParameterGrid(REGRESSION_PARAMS))

    predictor_cache = dict()
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

            if race.similar_races_hash not in cls.predictor_cache:

                cls.predictor_cache[race.similar_races_hash] = race.provider.find(Predictor, {'race_entry_conditions': race['entry_conditions'], 'race_group': race['group'], 'race_track_condition': race['track_condition']}, None)
                if len(cls.predictor_cache[race.similar_races_hash]) < 1:
                    cls.predictor_cache[race.similar_races_hash] = cls.generate_predictors(race)

                last_training_date = None
                for predictor in cls.predictor_cache[race.similar_races_hash]:
                    if predictor['last_training_date'] is not None and (last_training_date is None or predictor['last_training_date'] < last_training_date):
                        last_training_date = predictor['last_training_date']

                if last_training_date is None or last_training_date < race.meet['date']:

                    train_X = list()
                    train_y_classification = list()
                    train_y_regression = list()
                    train_weights = list()

                    start_time = {'$lt': race.meet['date']}
                    if last_training_date is not None:
                        start_time['$gte'] = last_training_date
                    similar_races = race.provider.find(racing_data.Race, {'entry_conditions': race['entry_conditions'], 'group': race['group'], 'start_time': start_time, 'track_condition': race['track_condition']}, None)
                    for similar_race in similar_races:
                        for active_runner in similar_race.active_runners:
                            if active_runner.result is not None:
                                train_X.append(active_runner.sample.normalized_query_data)
                                train_y_classification.append(active_runner.sample['classification_result'])
                                train_y_regression.append(active_runner.sample['regression_result'])
                                train_weights.append(active_runner.sample['weight'])

                    if len(train_X) > 0:

                        train_X = numpy.array(train_X)
                        train_y_classification = numpy.array(train_y_classification)
                        train_y_regression = numpy.array(train_y_regression)
                        train_weights = numpy.array(train_weights)

                        for predictor in cls.predictor_cache[race.similar_races_hash]:
                            try:
                                predictor.estimator.partial_fit(train_X, train_y_classification if predictor['is_classifier'] else train_y_regression, sample_weight=train_weights if predictor['uses_sample_weights'] else None)
                            except BaseException:
                                predictor.delete()
                            else:
                                predictor['last_training_date'] = race.meet['date']
                                predictor.save()

                        cls.predictor_cache[race.similar_races_hash][:] = [predictor for predictor in cls.predictor_cache[race.similar_races_hash] if '_id' in predictor and predictor['_id'] is not None]

            return cls.predictor_cache[race.similar_races_hash]

    @classmethod
    def generate_predictors(cls, race):
        """Generate predictors for the specified race"""

        predictors = list()

        for uses_sample_weights in (True, False):

            for estimator_params in cls.CLASSIFICATION_PARAM_GRID:
                try:
                    predictors.append(cls.generate_predictor(race, linear_model.SGDClassifier, estimator_params, True, uses_sample_weights))
                except BaseException:
                    pass

            for estimator_params in cls.REGRESSION_PARAM_GRID:
                try:
                    predictors.append(cls.generate_predictor(race, linear_model.SGDRegressor, estimator_params, False, uses_sample_weights))
                except BaseException:
                    pass

        return predictors

    @classmethod
    def generate_predictor(cls, race, estimator_type, estimator_params, is_classifier, uses_sample_weights):
        """Generate and train a predictor of the specified type using the provided training data"""

        predictor = Predictor(race.provider, None, is_classifier=is_classifier, last_training_date=None, race_entry_conditions=race['entry_conditions'], race_group=race['group'], race_track_condition=race['track_condition'], uses_sample_weights=uses_sample_weights)
        predictor.estimator = estimator_type(random_state=1, warm_start=True, **estimator_params)
        predictor.save()

        return predictor

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.estimator = None
        if 'estimator' in self and self['estimator'] is not None:
            self.estimator = pickle.loads(self['estimator'])

    def delete(self):
        """Remove this predictor from the database"""

        self.provider.delete(self)

    def save(self):
        """Save this predictor to the database"""

        self['estimator'] = None
        if self.estimator is not None:
            self['estimator'] = pickle.dumps(self.estimator)

        self['updated_at'] = datetime.now(self.provider.local_timezone)

        self.provider.save(self)
