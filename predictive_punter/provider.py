import racing_data

from . import Sample


class Provider(racing_data.Provider):
    """Extend the racing_data Provider class with additional functionality specific to predictive analytics"""

    def get_sample_by_runner(self, runner):
        """Get the sample for the specified runner"""

        return self.find_or_create_one(Sample, {'runner_id': runner['_id']}, {'runner': runner}, runner['updated_at'], Sample.generate_sample, runner)
