import racing_data

from . import Prediction, Predictor, Sample


class Provider(racing_data.Provider):
    """Extend the racing_data Provider class with additional functionality specific to predictive analytics"""

    @property
    def database_indexes(self):
        """Return a dictionary of required database indexes for each entity type"""

        database_indexes = super().database_indexes
        database_indexes[Prediction] = [
            [('race_id', 1)]
        ]
        database_indexes[Predictor] = [
            [('similar_races_hash', 1)]
        ]
        database_indexes[Sample] = [
            [('runner_id', 1)]
        ]
        database_indexes[racing_data.Race].append(
            [('entry_conditions', 1), ('group', 1), ('start_time', 1), ('track_condition', 1)]
            )

        return database_indexes

    def get_predictions_by_race(self, race):
        """Get a list of predictions for the specified race"""

        return self.find_or_create(Prediction, {'race_id': race['_id']}, {'race': race}, Prediction.generate_predictions, race)

    def get_race_by_prediction(self, prediction):
        """Get the race associated with the specified prediction"""

        return self.find_one(racing_data.Race, {'_id': prediction['race_id']}, None)

    def get_runner_by_sample(self, sample):
        """Get the runner associated with the specified sample"""

        return self.find_one(racing_data.Runner, {'_id': sample['runner_id']}, {'sample': sample})

    def get_sample_by_runner(self, runner):
        """Get the sample for the specified runner"""

        return self.find_or_create_one(Sample, {'runner_id': runner['_id']}, {'runner': runner}, runner['updated_at'], Sample.generate_sample, runner)
