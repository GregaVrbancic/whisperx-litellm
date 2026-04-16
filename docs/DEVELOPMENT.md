# Development Guide

## Prerequisites

- Python 3.11+
- [uv](https://astral.sh/uv/) package manager
- NVIDIA GPU with Docker GPU runtime (for full testing)
- Hugging Face token (for diarization features)

## Local Development with uv

### Setup

```bash
# Clone and install dependencies
git clone https://github.com/yourusername/whisperx-litellm-wrapper.git
cd whisperx-litellm-wrapper
uv sync --all-extras
```

### Running the Development Server

```bash
# Set environment variables
export HF_TOKEN=your_token
export WHISPERX_API_KEY=your_api_key

# Start the server
HF_TOKEN=your_token uv run uvicorn app:app --host 0.0.0.0 --port 8010
```

The API will be available at `http://localhost:8010` with interactive docs at `http://localhost:8010/docs`.

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=html

# Run specific test class
uv run pytest tests/test_app.py::TestHealthEndpoint -v

# Run only unit tests
uv run pytest tests/ -v -m unit
```

### Code Quality

```bash
# Lint with ruff
uv run ruff check app.py tests/

# Format code
uv run ruff format app.py tests/

# Check formatting without applying
uv run ruff format --check app.py tests/
```

## Docker Development

### Build the Development Image

```bash
docker build -t whisperx-api:dev .
```

### Run with Docker

```bash
docker run --rm \
  --gpus all \
  -p 8010:8010 \
  -e HF_TOKEN=your_hf_token \
  -e WHISPERX_API_KEY=change_me \
  -e WHISPERX_DEVICE=cuda \
  -e WHISPERX_COMPUTE_TYPE=float16 \
  -v whisperx_cache:/.cache \
  whisperx-api:dev
```

### Using Docker Compose

```bash
# Edit the example file with your tokens
cp docker-compose.example.yml docker-compose.yml
# Update environment variables in docker-compose.yml

# Run the service
docker-compose up
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPERX_BIN` | `whisperx` | Path to WhisperX binary |
| `HF_TOKEN` | - | Hugging Face token for diarization |
| `WHISPERX_API_KEY` | - | Bearer token for API authentication |
| `WHISPERX_MODEL` | `large-v3` | Default WhisperX model |
| `WHISPERX_DEVICE` | `cuda` | Compute device (cuda/cpu) |
| `WHISPERX_COMPUTE_TYPE` | `float16` | Precision (float16/float32) |
| `WHISPERX_BATCH_SIZE` | `4` | Batch size for processing |
| `WHISPERX_TASK` | `transcribe` | Task (transcribe/translate) |
| `WHISPERX_OUTPUT_FORMAT` | `json` | Output format |

## Project Structure

```
├── app.py                      # Main FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_app.py            # Unit tests
├── docs/
│   ├── README.md              # Overview (this file is main README in docs/)
│   ├── DEVELOPMENT.md         # This file
│   ├── API.md                 # API documentation
│   ├── VERSIONING.md          # Version management guide
│   └── CONTRIBUTING.md        # Contribution guidelines
├── scripts/
│   └── update-whisperx-version.sh  # Version update helper
├── .github/workflows/
│   ├── tests.yml              # CI/CD tests
│   └── docker-build.yml       # Docker build and publish
├── Dockerfile                 # Docker image definition
├── pyproject.toml             # Project configuration
└── README.md                  # Quick start (links to docs/)
```

## Making Changes

1. **Create a branch** for your feature or fix
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** and test locally
   ```bash
   uv run pytest tests/ -v
   uv run ruff check app.py tests/
   ```

3. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new endpoint" -m "Detailed description of changes"
   ```

4. **Push and create a pull request**
   ```bash
   git push origin feature/my-feature
   ```

5. **Wait for CI/CD checks** to pass

## Debugging Tips

- **Check health endpoint**: `curl http://localhost:8010/health`
- **View API docs**: Open `http://localhost:8010/docs` in a browser
- **Check logs**: Watch Docker logs with `docker logs -f <container-id>`
- **Test authentication**: Add `Authorization: Bearer your-key` header
- **Inspect requests**: Use FastAPI debug mode in `app.py`

## Continuous Integration

GitHub Actions automatically:
- Runs tests on Python 3.11 and 3.12
- Checks code formatting with Ruff
- Builds and publishes Docker images on main branch
- Tags images with WhisperX version
