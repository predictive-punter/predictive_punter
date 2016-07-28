import predictive_punter


def test_persistence(sample, runner, provider):
    """Subsequent identical calls to get_sample_by_runner should return the same Sample object"""

    assert provider.get_sample_by_runner(runner)['_id'] == sample['_id']


def test_provider(sample, provider):
    """All Sample objects should contain a reference to the provider instance from which they were sourced"""

    assert sample.provider == provider


def test_timestamps(sample):
    """All Sample objects should contain timezone aware created/updated at timestamps"""

    for key in ('created_at', 'updated_at'):
        assert sample[key].tzinfo is not None


def test_types(sample):
    """The get_sample_by_runner method should return a Sample object"""

    assert isinstance(sample, predictive_punter.Sample)


def test_updates(future_race, provider):
    """Subsequent identical calls to get_sample_by_runner with a future runner should return the same Sample object updated"""

    old_runner = provider.get_runners_by_race(future_race)[0]
    old_sample = provider.get_sample_by_runner(old_runner)

    new_runner = provider.get_runners_by_race(future_race)[0]
    new_sample = provider.get_sample_by_runner(new_runner)

    assert new_sample['_id'] == old_sample['_id']
    assert new_sample['updated_at'] > old_sample['updated_at']
