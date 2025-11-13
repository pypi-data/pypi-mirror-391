from tests.actions_helper import ActionsFileHelper
import unittest
from drivee_client import ChargingHistory
from drivee_client.dtos.charging_history_dto import ChargingHistoryDTO
from typing import Any

class TestChargingHistory(unittest.TestCase):
    def setUp(self):
        self.raw_data: dict[str, Any] = ActionsFileHelper.get_json("history_response.json")

    def test_charging_history_model(self):
        # Assume the JSON root is a dict with a 'session_history' key containing the DTOs
        dto_data = self.raw_data
        self.assertIn("session_history", dto_data)
        self.assertIsInstance(dto_data["session_history"], list)
        dto = ChargingHistoryDTO(**dto_data)
        model = ChargingHistory(dto)
        # Assert the count matches the JSON
        expected_count = len(dto_data["session_history"])
        self.assertEqual(len(model.sessions), expected_count)

if __name__ == "__main__":
    unittest.main()
