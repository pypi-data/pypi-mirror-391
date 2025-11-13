import unittest
from unittest.mock import AsyncMock, MagicMock
from drivee_client import DriveeClient, AuthenticationError
from tests.actions_helper import ActionsFileHelper
from typing import Any

class ResponseMockBuilder:
    def __init__(self):
        self._status = 200
        self._json_data: dict[str, object] | None = None
        self._text_data: str | None = None

    def with_status(self, status: int) -> "ResponseMockBuilder":
        self._status = status
        return self

    def with_json(self, json_data: dict[str, object]) -> "ResponseMockBuilder":
        self._json_data = json_data
        return self

    def with_text(self, text_data: str) -> "ResponseMockBuilder":
        self._text_data = text_data
        return self

    def build(self) -> MagicMock:
        mock_response = MagicMock()
        mock_response.status = self._status
        if self._json_data is not None:
            mock_response.json = AsyncMock(return_value=self._json_data)
        if self._text_data is not None:
            mock_response.text = AsyncMock(return_value=self._text_data)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        return mock_response

class SessionMockBuilder:
    def __init__(self):
        self._methods: dict[str, MagicMock] = {}
        self._side_effects: dict[str, Any] = {}

    def with_method(self, method: str, response: MagicMock) -> "SessionMockBuilder":
        self._methods[method] = MagicMock(return_value=response)
        return self

    def with_side_effect(self, method: str, side_effect_fn: Any) -> "SessionMockBuilder":
        self._side_effects[method] = side_effect_fn
        return self

    def build(self) -> MagicMock:
        mock_session = MagicMock()
        for method, mock in self._methods.items():
            setattr(mock_session, method, mock)
        for method, side_effect in self._side_effects.items():
            setattr(getattr(mock_session, method), "side_effect", side_effect)
        return mock_session

class TestDriveeClient(unittest.IsolatedAsyncioTestCase):
    async def test_authenticate_success(self):
        # Load response from actions/auth.json
        mock_auth_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("auth.json"))
            .build()
        )

        mock_charge_points_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("charge_points_notcharging.json"))
            .build()
        )
        mock_session = (
            SessionMockBuilder()
            .with_method("post", mock_auth_response)
            .with_method("request", mock_charge_points_response)
            .build()
        )
        client = DriveeClient("user", "pass", session=mock_session)
        await client.init()

    async def test_authenticate_failure(self):
        mock_response = (
            ResponseMockBuilder()
            .with_status(401)
            .with_text("Unauthorized")
            .build()
        )
        mock_session = (
            SessionMockBuilder()
            .with_method("post", mock_response)
            .build()
        )
        client = DriveeClient("user", "pass", session=mock_session)
        with self.assertRaises(AuthenticationError):
            await client.init()

    async def test_end_charging(self):
        auth_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("auth.json"))
            .build()
        )
        mock_end_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("end_charging.json"))
            .build()
        )
        mock_start_charge_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("start_charging.json"))
            .build()
        )
        mock_charge_points_non_charging_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("charge_points_notcharging.json"))
            .build()
        )
        mock_charge_points_charging_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("charge_points_charging.json"))
            .build()
        )
        nonCharging = [True]
        def request_side_effect(method: str, url: str, *args: Any, **kwargs: Any) -> MagicMock:
            url_str = str(url)
            if method.lower() == "post" and "start" in url_str:
                return mock_start_charge_response
            if method.lower() == "post" and "end" in url_str:
                return mock_end_response
            if method.lower() == "get" and "charge-points" in url_str and nonCharging[0]:
                nonCharging[0] = False
                return mock_charge_points_non_charging_response
            if method.lower() == "get" and "charge-points" in url_str and not nonCharging[0]:
                return mock_charge_points_charging_response
            raise Exception("Invalid request in test")
        mock_session = (
            SessionMockBuilder()
            .with_method("post", auth_response)
            .with_side_effect("request", request_side_effect)
            .build()
        )
        client = DriveeClient("user", "pass", session=mock_session)
        await client.init()
        await client.start_charging()
        response = await client.end_charging()
        self.assertEqual(response.session.id, "648418")

    async def test_start_charging(self):
        # Build response mocks
        mock_auth_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("auth.json"))
            .build()
        )
        mock_charge_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("start_charging.json"))
            .build()
        )
        mock_charge_points_response = (
            ResponseMockBuilder()
            .with_status(200)
            .with_json(ActionsFileHelper.get_json("charge_points_notcharging.json"))
            .build()
        )

        def request_side_effect(method: str, url: str, *args: Any, **kwargs: Any) -> MagicMock | None:
            url_str = str(url)
            if method.lower() == "post" and "start" in url_str:
                return mock_charge_response
            if method.lower() == "get" and "charge-points" in url_str:
                return mock_charge_points_response
            raise Exception("Invalid request in test")
        mock_session = (
            SessionMockBuilder()
            .with_method("post", mock_auth_response)
            .with_side_effect("request", request_side_effect)
            .build()
        )
        client = DriveeClient("user", "pass", session=mock_session)
        await client.init()
        response = await client.start_charging()
        self.assertEqual(response.session.id, "648418")

if __name__ == "__main__":
    unittest.main()
