from typing import Any
from tests.actions_helper import ActionsFileHelper
import unittest
from drivee_client import ChargingSession
from drivee_client.dtos.charging_session_dto import ChargingSessionDTO


class TestChargingSession(unittest.TestCase):
    def setUp(self):
        self.raw_data: dict[str, Any] = ActionsFileHelper.get_json("charging_session.json")

    def test_charging_session_model(self):
        # Assume the JSON root is a dict with a 'session' key containing the DTO
        self.assertIn("session", self.raw_data)
        dto_data = self.raw_data["session"]
        dto = ChargingSessionDTO(**dto_data)
        model = ChargingSession(dto)
        self.assertTrue(model.id)
        self.assertTrue(model.evse_id)
        self.assertTrue(model.started_at)

if __name__ == "__main__":
    unittest.main()
