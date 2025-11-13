"""Unit tests for ChargePoint model transformation from raw API data."""
import unittest
from typing import Any

from drivee_client.dtos.charge_point_dto import ChargePointDTO
from drivee_client.models.charge_point import ChargePoint
from tests.actions_helper import ActionsFileHelper


class TestChargePoint(unittest.TestCase):
    """Test cases for ChargePoint model transformation from DTOs."""

    def setUp(self):
        """Set up test data."""
        self.raw_data: dict[str, Any] = ActionsFileHelper.get_json("charge_points_notcharging.json")

    def test_charge_point_model_from_api_data(self):
        """Verify ChargePoint model can be created from the sample charge-points.json data via DTOs."""
        self.assertIn("data", self.raw_data)
        self.assertIsInstance(self.raw_data["data"], list)
        self.assertGreater(len(self.raw_data["data"]), 0)

        charge_points_dto: list[ChargePointDTO] = [
            ChargePointDTO(**point_data)
            for point_data in self.raw_data["data"]
        ]

        self.assertEqual(len(charge_points_dto), len(self.raw_data["data"]))

        charge_point: ChargePoint = ChargePoint.from_dtos(charge_points_dto)
        self.assertIsInstance(charge_point, ChargePoint)


if __name__ == "__main__":
    unittest.main()