# whisperx-litellm-wrapper

Docker image exposing WhisperX through an OpenAI-compatible transcription API for LiteLLM.

> **[View detailed documentation →](./docs/README.md)**

## Quick Start

### Local Development

```bash
uv sync
HF_TOKEN=your_token uv run uvicorn app:app --host 0.0.0.0 --port 8010
```

### Docker

```bash
docker build -t whisperx-api:local .
docker run --rm --gpus all -p 8010:8010 \
  -e HF_TOKEN=your_hf_token \
  -e WHISPERX_API_KEY=change_me \
  whisperx-api:local
```

### Test

```bash
curl http://localhost:8010/health
```

## Documentation

- **[Overview & Setup](./docs/README.md)** - Project overview and getting started
- **[Development Guide](./docs/DEVELOPMENT.md)** - Local setup, testing, and debugging
- **[API Documentation](./docs/API.md)** - Complete endpoint reference
- **[Versioning](./docs/VERSIONING.md)** - Managing WhisperX versions
- **[Contributing](./docs/CONTRIBUTING.md)** - How to contribute

## Features

- ✅ OpenAI-compatible `/v1/audio/transcriptions` endpoint
- ✅ Direct `/transcribe` endpoint with WhisperX parameters
- ✅ Speaker diarization support
- ✅ Optional bearer token authentication
- ✅ Multiple output formats (json, text, verbose_json)
- ✅ Docker support with GPU acceleration

## Requirements

- Python 3.11+ or Docker
- NVIDIA GPU with Docker GPU runtime (optional, supports CPU)
- Hugging Face token for diarization

## License

See [LICENSE](./LICENSE) file for details.
