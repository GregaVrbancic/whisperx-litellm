# Version Management

This project follows the WhisperX version it wraps. When a new WhisperX version is released, update this project's version to match.

## Tracking WhisperX Version

- **`.whisperx-version`**: Contains the pinned WhisperX version
- **`pyproject.toml`**: Project version matches WhisperX version
- **`Dockerfile`**: Uses `ARG WHISPERX_VERSION` to pin the base image

## Updating to a New WhisperX Version

Use the automated script:

```bash
./scripts/update-whisperx-version.sh 3.1.1
```

This updates:
- `.whisperx-version`
- `pyproject.toml` version field

Then commit and push:

```bash
git add .whisperx-version pyproject.toml
git commit -m "chore: update to WhisperX 3.1.1"
git tag v3.1.1
git push --tags
```

## Docker Image Tagging

When pushed to main, the Docker image is automatically tagged with:
- `latest` (main branch only)
- `whisperx-3.1.0` (main branch only)
- Git commit SHA
- Git ref/branch
- Semantic version tags (if pushed as a tag)

Docker images are published to: `ghcr.io/<owner>/whisperx_litellm`

## Version at Runtime

The service version is dynamically read from `pyproject.toml` at startup and reported in:
- `GET /health` endpoint
- OpenAI API responses

The environment variable `WHISPERX_VERSION` is also available inside the Docker container.
