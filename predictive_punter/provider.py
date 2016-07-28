import racing_data

from . import Sample


class Provider(racing_data.Provider):
    """Extend the racing_data Provider class with additional functionality specific to predictive analytics"""

    @property
    def database_indexes(self):
        """Return a dictionary of required database indexes for each entity type"""

        database_indexes = super().database_indexes
        database_indexes[Sample] = [
            [('runner_id', 1)]
        ]

        return database_indexes

    def get_runner_by_sample(self, sample):
        """Get the runner associated with the specified sample"""

        return self.find_one(racing_data.Runner, {'_id': sample['runner_id']}, {'sample': sample})

    def get_sample_by_runner(self, runner):
        """Get the sample for the specified runner"""

        return self.find_or_create_one(Sample, {'runner_id': runner['_id']}, {'runner': runner}, runner['updated_at'], Sample.generate_sample, runner)
