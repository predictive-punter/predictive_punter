def test_active_runners(race):
    """The active_runners property should return a list containing all non-scratched runners in the race"""

    assert race.active_runners == [runner for runner in race.runners if runner['is_scratched'] is False]
