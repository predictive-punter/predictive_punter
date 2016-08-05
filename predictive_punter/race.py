import racing_data

from . import Prediction
from .combination_utils import get_combinations


@property
def active_runners(self):
    """Return a list of non-scratched runners in the race"""

    def generate_active_runners():
        return [runner for runner in self.runners if runner['is_scratched'] is False]

    return self.get_cached_property('active_runners', generate_active_runners)

racing_data.Race.active_runners = active_runners


def get_winning_combinations(self, places):
    """Return a list of tuples of Runners representing all winning combinations for the specified number of places"""

    if len(self.runners) >= places:

        results = []
        for count in range(places):
            results.append([])

        for runner in self.active_runners:
            if runner.result is not None and runner.result <= len(results):
                results[runner.result - 1].append(runner)

        for index in range(len(results) - 1):
            if len(results[index + 1]) < 1:
                results[index + 1] = list(results[index])

        return [tuple(combination) for combination in get_combinations(results)]

racing_data.Race.get_winning_combinations = get_winning_combinations


def calculate_value(self, places):
    """Return the value of the winning combinations with the specified number of places for the race"""

    value = 0.00

    combinations = self.get_winning_combinations(places)
    if combinations is not None:
        for combination in combinations:
            combination_value = 1.00
            for index in range(len(combination)):
                if combination[index].starting_price is not None:
                    combination_value *= max(combination[index].starting_price * (places - index) / places, 2.0 if index > 0 else 1.0)
            value += combination_value

    return value

racing_data.Race.calculate_value = calculate_value


@property
def win_value(self):
    """Return the sum of the starting prices of all winning runners less the number of winning runners"""
    
    return self.calculate_value(1)

racing_data.Race.win_value = win_value


@property
def exacta_value(self):
    """Return the sum of the products of the starting prices of first and second placed runners in all winning combinations, less the number of winning combinations"""
    
    return self.calculate_value(2)

racing_data.Race.exacta_value = exacta_value


@property
def trifecta_value(self):
    """Return the sum of the products of the starting prices of first, second and third placed runners in all winning combinations, less the number of winning combinations"""
    
    return self.calculate_value(3)

racing_data.Race.trifecta_value = trifecta_value


@property
def first_four_value(self):
    """Return the sum of the products of the starting prices of the first, second, third and fourth placed runners in all winning combinations, less the number of winning combinations"""
    
    return self.calculate_value(4)

racing_data.Race.first_four_value = first_four_value


@property
def total_value(self):
    """Return the sum of the win, exacta, trifecta and first four values for this race"""
    
    total_value = 0.0
    for value in (self.win_value, self.exacta_value, self.trifecta_value, self.first_four_value):
        if value is not None:
            total_value += value
    return total_value

racing_data.Race.total_value = total_value


@property
def predictions(self):
    """Return all predictions for this race"""

    return self.get_cached_property('predictions', self.provider.get_predictions_by_race, self)

racing_data.Race.predictions = predictions


@property
def similar_races_hash(self):
    """Return a hash of the race values relevant to finding similar races"""

    return hash(tuple(self['entry_conditions'] + [self['group'], self['track_condition']]))

racing_data.Race.similar_races_hash = similar_races_hash


@property
def best_predictions(self):
    """Return a dictionary of the best predictions for this race by bet type"""

    def generate_best_predictions():

        best_predictions = dict()
        for key in Prediction.BET_TYPES:
            best_predictions[key] = None
        best_predictions['multi'] = set()

        for prediction in self.predictions:
            similar_predictions = prediction.provider.find(Prediction, {'predictor_id': prediction['predictor_id'], 'start_time': {'$lt': self.meet['date']}}, None)

            for bet_type in Prediction.BET_TYPES:

                has_bet = True
                for place in range(Prediction.BET_TYPES[bet_type]):
                    if len(prediction['picks'][place]) < 1:
                        has_bet = False
                        break
                if has_bet:

                    all_values = [similar_prediction[bet_type + '_value'] for similar_prediction in similar_predictions if similar_prediction[bet_type + '_value'] != 0]
                    if len(all_values) > 0:
                        total_value = sum(all_values)
                        if total_value > 0:

                            if bet_type == 'win':
                                for number in prediction['picks'][0]:
                                    best_predictions['multi'].add(number)

                            win_values = [value for value in all_values if value > 0]
                            if len(win_values) > 0:

                                strike_rate = len(win_values) / len(all_values)
                                minimum_dividend = 1.0 / strike_rate

                                if best_predictions[bet_type] is None or minimum_dividend < best_predictions[bet_type][1]:

                                    roi = total_value / len(all_values)

                                    best_predictions[bet_type] = prediction, minimum_dividend, roi

        return best_predictions

    return self.get_cached_property('best_predictions', generate_best_predictions)

racing_data.Race.best_predictions = best_predictions
