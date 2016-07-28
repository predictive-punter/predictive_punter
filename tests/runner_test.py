def test_calculate_expected_times(runner):
    """The calculate_expected_times method should return a tuple containing the minimum, maximum and average expected times for the specified performance list"""

    expected_values = tuple([runner.actual_distance / (momentum / runner.actual_weight) for momentum in runner.career.momentums])

    assert runner.calculate_expected_times('career') == expected_values
