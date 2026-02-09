from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def mock_humanizer():
    """Create a mock HumanizerService and attach it to app.state."""
    service = MagicMock()
    service.is_loaded = True
    service.humanize.return_value = "This is humanized text."
    app.state.humanizer = service
    yield service


@pytest.fixture
def client(mock_humanizer):
    return TestClient(app, raise_server_exceptions=False)


class TestHumanizeEndpoint:
    def test_humanize_success(self, client, mock_humanizer):
        response = client.post(
            "/api/humanize",
            json={"text": "Some AI generated text to humanize."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["humanized_text"] == "This is humanized text."
        assert data["input_length"] == len("Some AI generated text to humanize.")
        assert data["output_length"] == len("This is humanized text.")
        assert "processing_time_ms" in data
        mock_humanizer.humanize.assert_called_once()

    def test_humanize_with_custom_options(self, client, mock_humanizer):
        response = client.post(
            "/api/humanize",
            json={
                "text": "Test text.",
                "options": {"temperature": 1.2, "max_tokens": 512},
            },
        )
        assert response.status_code == 200
        mock_humanizer.humanize.assert_called_once_with(
            text="Test text.",
            temperature=1.2,
            max_tokens=512,
        )

    def test_humanize_empty_text(self, client):
        response = client.post("/api/humanize", json={"text": ""})
        assert response.status_code == 422

    def test_humanize_text_too_long(self, client):
        response = client.post("/api/humanize", json={"text": "a" * 10001})
        assert response.status_code == 422

    def test_humanize_model_not_loaded(self, client, mock_humanizer):
        mock_humanizer.is_loaded = False
        response = client.post(
            "/api/humanize", json={"text": "Test text."}
        )
        assert response.status_code == 503
        assert "not available" in response.json()["detail"]

    def test_humanize_model_inference_error(self, client, mock_humanizer):
        mock_humanizer.humanize.side_effect = RuntimeError("CUDA out of memory")
        response = client.post(
            "/api/humanize", json={"text": "Test text."}
        )
        assert response.status_code == 503
        assert "inference failed" in response.json()["detail"]

    @patch("app.api.humanize.get_session", side_effect=Exception("DB down"))
    def test_humanize_db_failure_doesnt_block(
        self, mock_session, client, mock_humanizer
    ):
        response = client.post(
            "/api/humanize", json={"text": "Test text."}
        )
        # Response still succeeds even though DB logging failed
        assert response.status_code == 200
        assert response.json()["humanized_text"] == "This is humanized text."

    def test_humanize_missing_body(self, client):
        response = client.post("/api/humanize")
        assert response.status_code == 422

    def test_humanize_invalid_temperature(self, client):
        response = client.post(
            "/api/humanize",
            json={"text": "Test.", "options": {"temperature": 5.0}},
        )
        assert response.status_code == 422

    def test_humanize_invalid_max_tokens(self, client):
        response = client.post(
            "/api/humanize",
            json={"text": "Test.", "options": {"max_tokens": 0}},
        )
        assert response.status_code == 422
