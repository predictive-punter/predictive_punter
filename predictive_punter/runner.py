import numpy
import racing_data

from . import Predictor


def calculate_expected_times(self, performance_list_name):
    """Return a tuple containing the minimum, maximum and average expected times based on the specified performance list's momentums"""

    def calculate_expected_time(momentum):
        if momentum is not None:
            return self.actual_distance / (momentum / self.actual_weight)

    return tuple([calculate_expected_time(momentum) for momentum in getattr(self, performance_list_name).momentums]) if self.actual_distance is not None else tuple([None, None, None])

racing_data.Runner.calculate_expected_times = calculate_expected_times


@property
def races_per_year(self):
    """Return total number of career starts for the horse divded by the horse's age as at the race date"""

    if self.age is not None and self.age > 0:
        return self.career.starts / self.age

racing_data.Runner.races_per_year = races_per_year


@property
def sample(self):
    """Return the sample for this runner"""

    return self.get_cached_property('sample', self.provider.get_sample_by_runner, self)

racing_data.Runner.sample = sample


@property
def prediction(self):
    """Return a prediction for this runner"""

    predictions = dict()
    train_samples = 0
    test_samples = 0

    for estimator, score, train_size, test_size in Predictor.get_predictors(self.race):
        try:
            prediction = estimator.predict(numpy.array(self.sample.normalized_query_data).reshape(1, -1))[0]
            if prediction not in predictions:
                predictions[prediction] = 0.0
            predictions[prediction] += score
            if train_size > train_samples:
                train_samples = train_size
            if test_size > test_samples:
                test_samples = test_size
        except BaseException:
            pass

    if len(predictions) > 0:
        return sum([key * predictions[key] for key in predictions]) / sum([predictions[key] for key in predictions]), train_samples, test_samples

racing_data.Runner.prediction = prediction
