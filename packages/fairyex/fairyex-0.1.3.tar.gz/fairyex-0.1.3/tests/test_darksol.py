import unittest

from fairyex.darksol import _get_period_type


class TestDarkSolUtils(unittest.TestCase):

    def test_get_period_type(self):
        for period_type, user_period_types in {
            "Interval": ["Interval", "interval", "i"],
            "FiscalYear": ["FiscalYear", "Fiscal Year", "fiscalyear", "Year", "yearly", "y"],
        }.items():
            for user_period_type in user_period_types:
                self.assertEqual(_get_period_type(user_period_type), period_type)
