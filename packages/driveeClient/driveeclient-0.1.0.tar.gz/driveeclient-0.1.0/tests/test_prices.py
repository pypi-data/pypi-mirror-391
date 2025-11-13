from typing import Any
import unittest

from drivee_client.dtos.price_periods_dto import PricePeriodsDTO
from drivee_client.models.price_periods import PricePeriods

from tests.actions_helper import ActionsFileHelper

class TestCPricePeriods(unittest.TestCase):
    def setUp(self):
        self.raw_data: dict[str, Any] = ActionsFileHelper.get_json("prices.json")

    def test_price_periods_model(self):
        # Assume the JSON root is a dict with a 'periods' key containing the DTO
        dto_data = self.raw_data
        dto = PricePeriodsDTO(**dto_data)
        model = PricePeriods(dto)
        self.assertTrue(model.periods)

    def test_get_price_at(self):
        dto_data = self.raw_data
        dto = PricePeriodsDTO(**dto_data)
        model = PricePeriods(dto)
        index = 10
        # Pick a known datetime from the test data
        dt = model.periods[index].start_date
        period = model.get_price_at(dt)
        self.assertIsNotNone(period)
        if period:
            self.assertEqual(period.start_date, dt)
            self.assertEqual(period.price_per_kwh, model.periods[index].price_per_kwh)

if __name__ == "__main__":
    unittest.main()

