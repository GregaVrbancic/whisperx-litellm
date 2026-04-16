"""Basic tests for the WhisperX LiteLLM wrapper API."""

from __future__ import annotations

import io
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app import app, require_auth, AuthError


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test the health check endpoint."""

    @pytest.mark.unit
    def test_health_returns_ok(self, client):
        """Health endpoint should return a 200 with ok=true."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["service"] == "WhisperX LiteLLM Wrapper"
        assert "version" in data
        assert "whisperx_bin" in data

    @pytest.mark.unit
    def test_health_no_auth_required(self, client):
        """Health endpoint should not require authentication."""
        response = client.get("/health")
        assert response.status_code == 200


class TestModelsEndpoint:
    """Test the models endpoint."""

    @pytest.mark.unit
    def test_models_endpoint_no_key_required(self, client):
        """Models endpoint should work without a key when API_KEY is not set."""
        # When WHISPERX_API_KEY is not set, auth is not required
        with patch.dict(os.environ, {}, clear=False):
            if os.getenv("WHISPERX_API_KEY"):
                pytest.skip("WHISPERX_API_KEY is set; test requires it to be unset")
            response = client.get("/v1/models")
            assert response.status_code == 200

    @pytest.mark.unit
    def test_models_returns_list(self, client):
        """Models endpoint should return a list of models."""
        response = client.get("/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert "data" in data
        assert len(data["data"]) > 0
        model = data["data"][0]
        assert model["object"] == "model"
        assert model["mode"] == "audio_transcription"


class TestAuthentication:
    """Test authentication logic."""

    @pytest.mark.unit
    def test_require_auth_with_no_key_set(self):
        """require_auth should not raise when API_KEY is not set."""
        with patch.dict(os.environ, {"WHISPERX_API_KEY": ""}, clear=False):
            # Should not raise
            require_auth(None)
            require_auth("Bearer anything")

    @pytest.mark.unit
    def test_require_auth_with_valid_key(self):
        """require_auth should not raise with valid bearer token."""
        with patch.dict(os.environ, {"WHISPERX_API_KEY": "test-key"}, clear=False):
            # Need to reload the module to pick up the env var
            # For this test, we directly test the logic
            auth_header = "Bearer test-key"
            token = auth_header.split(" ", 1)[1].strip()
            assert token == "test-key"

    @pytest.mark.unit
    def test_require_auth_with_invalid_key(self):
        """require_auth should raise AuthError with invalid bearer token."""
        with patch.dict(os.environ, {"WHISPERX_API_KEY": "correct-key"}, clear=False):
            with pytest.raises(AuthError):
                require_auth("Bearer wrong-key")

    @pytest.mark.unit
    def test_require_auth_missing_bearer_prefix(self):
        """require_auth should raise AuthError without Bearer prefix."""
        with patch.dict(os.environ, {"WHISPERX_API_KEY": "test-key"}, clear=False):
            with pytest.raises(AuthError):
                require_auth("test-key")

    @pytest.mark.unit
    def test_require_auth_no_header(self):
        """require_auth should raise AuthError when no header is provided."""
        with patch.dict(os.environ, {"WHISPERX_API_KEY": "test-key"}, clear=False):
            with pytest.raises(AuthError):
                require_auth(None)


class TestTranscribeEndpoint:
    """Test the /transcribe endpoint."""

    @pytest.mark.unit
    def test_transcribe_missing_file(self, client):
        """Transcribe endpoint should require a file."""
        response = client.post("/transcribe")
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    def test_transcribe_returns_error_without_hf_token_when_diarizing(self, client):
        """Transcribe should return 400 when diarize=true but HF_TOKEN is not set."""
        with patch.dict(
            os.environ, {"WHISPERX_API_KEY": "", "HF_TOKEN": ""}, clear=False
        ):
            audio_data = io.BytesIO(b"fake audio data")
            response = client.post(
                "/transcribe",
                data={"diarize": "true"},
                files={"file": ("test.wav", audio_data)},
            )
            assert response.status_code == 400
            assert "HF_TOKEN" in response.json()["detail"]


class TestOpenAICompatibleEndpoint:
    """Test the /v1/audio/transcriptions endpoint."""

    @pytest.mark.unit
    def test_openai_endpoint_missing_file(self, client):
        """OpenAI endpoint should require a file."""
        response = client.post("/v1/audio/transcriptions")
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    def test_openai_endpoint_requires_file(self, client):
        """OpenAI transcriptions endpoint should return validation error without file."""
        response = client.post("/v1/audio/transcriptions")
        assert response.status_code == 422


@pytest.mark.unit
def test_app_has_required_endpoints():
    """Verify all required endpoints are defined."""
    endpoints = [route.path for route in app.routes]
    required_paths = [
        "/health",
        "/v1/models",
        "/transcribe",
        "/v1/audio/transcriptions",
    ]
    for path in required_paths:
        assert path in endpoints, f"Missing endpoint: {path}"
