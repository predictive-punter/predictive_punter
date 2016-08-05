import numpy
import racing_data

from . import __version__, Predictor
from .combination_utils import get_combinations


class Prediction(racing_data.Entity):
    """A prediction represents a single predictor's estimate of a race's result"""

    BET_TYPES = {
        'win':          1,
        'exacta':       2,
        'trifecta':     3,
        'first_four':   4
    }
    
    @classmethod
    def generate_predictions(cls, race):
        """Generate predictions for the specified race"""

        predictions = list()

        for predictor in Predictor.get_predictors(race):
            predictions.append(cls.generate_prediction(race, predictor))

        return predictions

    @classmethod
    def generate_prediction(cls, race, predictor):
        """Generate a prediction for the specified race using the provided predictor"""

        prediction = {
            'picks':                list(),
            'predictor_id':         predictor['_id'],
            'predictor_version':    __version__,
            'start_time':           race['start_time']
        }

        estimations = dict()
        for active_runner in race.active_runners:
            try:
                estimation = predictor.estimator.predict(numpy.array(active_runner.sample.normalized_query_data).reshape(1, -1))[0]
            except BaseException:
                pass
            else:
                if estimation not in estimations:
                    estimations[estimation] = list()
                estimations[estimation].append(active_runner['number'])

        if predictor['is_classifier']:
            for place in range(4):
                prediction['picks'].append(list())
            for place in range(1, 5):
                if place in estimations:
                    prediction['picks'][place - 1].extend(estimations[place])
        else:
            new_picks = list()
            for key in sorted(estimations.keys()):
                next_pick = list(estimations[key])
                for count in range(len(next_pick)):
                    if len(new_picks) < 4:
                        new_picks.append(next_pick)
            if len(new_picks) < 4:
                for place in range(4 - len(new_picks)):
                    new_picks.append(list())
            prediction['picks'] = new_picks

        for bet_type in cls.BET_TYPES:

            value = 0.00

            prediction_combinations = [tuple(combination) for combination in get_combinations(prediction['picks'][:cls.BET_TYPES[bet_type]])]
            if prediction_combinations is not None and len(prediction_combinations) > 0:
                
                winning_combinations = race.get_winning_combinations(cls.BET_TYPES[bet_type])
                if winning_combinations is not None:
                    for winning_combination in winning_combinations:
                        numeric_combination = tuple([runner['number'] for runner in winning_combination])
                        if numeric_combination in prediction_combinations:
                            combination_value = 1.00
                            for index in range(len(winning_combination)):
                                if winning_combination[index].starting_price is not None:
                                    combination_value *= max(winning_combination[index].starting_price * (cls.BET_TYPES[bet_type] - index) / cls.BET_TYPES[bet_type], 2.0)
                            value += combination_value

                if cls.BET_TYPES[bet_type] > 1:
                    value /= len(prediction_combinations)
                    value -= 1.0
                else:
                    value -= len(prediction_combinations)

            prediction[bet_type + '_value'] = value

        return prediction

    @property
    def has_expired(self):
        """Expire predictions that were last updated prior to the associated race"""

        return self['updated_at'] < self.race['updated_at'] or self['predictor_version'].split('.')[0] != __version__.split('.')[0]

    @property
    def race(self):
        """Return the race associated with this prediction"""

        return self.get_cached_property('race', self.provider.get_race_by_prediction, self)

    def is_equivalent_to(self, other_prediction):
        """This prediction is equivalent to other_prediction if both have the same predictor and race IDs"""

        return self['predictor_id'] == other_prediction['predictor_id'] and self['race_id'] == other_prediction['race_id']
