import racing_data


@property
def average_earnings(self):
    """Return the average earnings per start in this performance list"""

    return self.calculate_percentage(self.earnings)

racing_data.PerformanceList.average_earnings = average_earnings
