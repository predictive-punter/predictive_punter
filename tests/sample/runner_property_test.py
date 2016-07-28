def test_runner(runner, sample):
    """The runner property should return the runner associated with the sample"""

    assert sample.runner['_id'] == runner['_id']
