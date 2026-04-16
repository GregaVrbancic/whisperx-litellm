# whisperx-litellm-wrapper

A standalone `uv`-based project that builds a Docker image exposing WhisperX through an OpenAI-compatible transcription API, so it can be plugged into LiteLLM like another backend model service.

## What this project provides

- `GET /health`
- `GET /v1/models`
- `POST /transcribe`
- `POST /v1/audio/transcriptions`
- optional bearer auth with `WHISPERX_API_KEY`
- local diarization via WhisperX + Hugging Face token

This project is designed to be deployed as a **separate service** and then registered in LiteLLM using `model_info.mode: audio_transcription`, which LiteLLM documents for its `/v1/audio/transcriptions` endpoint.

## Why this shape

The upstream WhisperX project documents Python/CLI installation and diarization support, but not an official OpenAI-compatible API server. WhisperX uses faster-whisper and supports speaker diarization when you pass a Hugging Face token and accept the diarization model terms.

This wrapper adds the missing HTTP layer so your LiteLLM proxy can treat it like another backend service.

## Requirements

- NVIDIA GPU with working Docker GPU runtime
- Hugging Face token in `HF_TOKEN` if `diarize=true`
- accepted access terms for the pyannote diarization models

## Quick Links

- **[Installation & Setup](./DEVELOPMENT.md)** - Local development and deployment
- **[API Documentation](./API.md)** - Endpoint reference and examples
- **[Versioning Guide](./VERSIONING.md)** - Managing WhisperX versions
- **[Contributing](./CONTRIBUTING.md)** - Contributing guidelines

## LiteLLM integration

Use the included `litellm_config.example.yaml` snippet. LiteLLM documents audio transcription models by setting `model_info.mode: audio_transcription`, and the proxy endpoint is `/v1/audio/transcriptions`.

Example request through LiteLLM:

```bash
curl -X POST http://localhost:4000/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_LITELLM_MASTER_KEY" \
  -F file=@/path/to/meeting.mp4 \
  -F model=whisperx-local \
  -F language=sl \
  -F diarize=true \
  -F response_format=verbose_json
```

## Notes

- `response_format=json` returns `{ "text": ... }` for compatibility with common transcription clients.
- `response_format=verbose_json` returns segments and any diarization information produced by WhisperX.
- `response_format=text` returns plain text.
- `prompt` and `temperature` are accepted on the OpenAI-compatible endpoint for compatibility, but are not used by WhisperX.
- This is an API wrapper, not a transcript editing UI.
