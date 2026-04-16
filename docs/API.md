# API Documentation

The WhisperX LiteLLM Wrapper provides two sets of endpoints: a direct transcription API and an OpenAI-compatible audio transcriptions endpoint.

## Base URL

- Development: `http://localhost:8010`
- Docker: `http://localhost:8010` (if exposed)
- Production: `https://your-deployment-domain`

## Authentication

All endpoints except `/health` require optional bearer token authentication when `WHISPERX_API_KEY` is set.

### Bearer Token

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8010/v1/models
```

If `WHISPERX_API_KEY` is not set in the environment, authentication is not required.

## Endpoints

### Health Check

Check service status and configuration.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "ok": true,
  "service": "WhisperX LiteLLM Wrapper",
  "version": "3.1.0",
  "whisperx_bin": "whisperx",
  "default_model": "large-v3",
  "hf_token_configured": true
}
```

### List Models

Get available transcription models.

**Request:**
```http
GET /v1/models
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "large-v3",
      "object": "model",
      "owned_by": "local",
      "mode": "audio_transcription"
    }
  ]
}
```

### Direct Transcription

Transcribe audio directly with WhisperX parameters.

**Request:**
```http
POST /transcribe
Authorization: Bearer YOUR_API_KEY
Content-Type: multipart/form-data
```

**Form Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | file | required | Audio file to transcribe |
| `model` | string | `large-v3` | WhisperX model size |
| `language` | string | auto | Language code (e.g., `en`, `sl`) |
| `task` | string | `transcribe` | Task: `transcribe` or `translate` |
| `diarize` | boolean | `true` | Enable speaker diarization |
| `batch_size` | integer | `4` | Processing batch size |
| `compute_type` | string | `float16` | Precision: `float16` or `float32` |
| `device` | string | `cuda` | Device: `cuda` or `cpu` |
| `output_format` | string | `json` | Internal format: `json`, `txt`, `srt`, etc. |
| `min_speakers` | integer | - | Minimum speakers for diarization |
| `max_speakers` | integer | - | Maximum speakers for diarization |
| `response_format` | string | `json` | Response format (see below) |

**Example:**
```bash
curl -X POST http://localhost:8010/transcribe \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@meeting.mp4 \
  -F model=large-v3 \
  -F language=en \
  -F diarize=true \
  -F response_format=verbose_json
```

**Response Formats:**

- `json`: Simple format `{"text": "..."}` (OpenAI compatible)
- `text`: Plain text only
- `verbose_json`: Full details with segments and diarization

**Example Response (`json`):**
```json
{
  "text": "Hello, this is a test transcription."
}
```

**Example Response (`verbose_json`):**
```json
{
  "task": "transcribe",
  "language": "en",
  "duration": 42.5,
  "text": "Hello, this is a test transcription.",
  "segments": [
    {
      "id": 0,
      "seek": 0,
      "start": 0.0,
      "end": 5.2,
      "text": " Hello, this is a test transcription.",
      "tokens": [50364, 2425],
      "temperature": 0.0,
      "avg_logprob": -0.25,
      "compression_ratio": 1.2,
      "no_speech_prob": 0.001,
      "speaker": "SPEAKER_00"
    }
  ],
  "words": [
    {"word": "Hello", "start": 0.2, "end": 0.8, "speaker": "SPEAKER_00"},
    {"word": "this", "start": 1.0, "end": 1.3, "speaker": "SPEAKER_00"}
  ],
  "x_diarization_enabled": true,
  "x_request_id": "abc123def456",
  "x_whisperx_model": "large-v3"
}
```

### OpenAI-Compatible Audio Transcription

OpenAI-compatible endpoint for use with LiteLLM and other platforms.

**Request:**
```http
POST /v1/audio/transcriptions
Authorization: Bearer YOUR_API_KEY
Content-Type: multipart/form-data
```

**Form Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | file | required | Audio file to transcribe |
| `model` | string | `large-v3` | Model identifier |
| `language` | string | auto | Language code |
| `response_format` | string | `json` | Response format |
| `prompt` | string | - | Prompt (accepted but ignored by WhisperX) |
| `temperature` | number | - | Temperature (accepted but ignored by WhisperX) |
| `diarize` | boolean | `true` | Enable speaker diarization |
| `min_speakers` | integer | - | Minimum speakers |
| `max_speakers` | integer | - | Maximum speakers |

**Example:**
```bash
curl -X POST http://localhost:8010/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@meeting.mp4 \
  -F model=large-v3 \
  -F language=en \
  -F response_format=verbose_json
```

**Response:**

Same as Direct Transcription endpoint, depending on `response_format`.

## Using with LiteLLM

Configure in LiteLLM's `config.yaml`:

```yaml
model_list:
  - model_name: whisperx-local
    litellm_params:
      model: whisperx-local
      api_base: http://localhost:8010
      mode: audio_transcription
    model_info:
      mode: audio_transcription
```

Then call through LiteLLM proxy:

```bash
curl -X POST http://localhost:4000/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_LITELLM_KEY" \
  -F file=@meeting.mp4 \
  -F model=whisperx-local \
  -F language=en \
  -F response_format=verbose_json
```

## Error Responses

### 400 Bad Request
Missing required `HF_TOKEN` when diarization is enabled:
```json
{
  "detail": "HF_TOKEN is required when diarize=true"
}
```

### 401 Unauthorized
Invalid or missing bearer token:
```json
{
  "detail": "Invalid or missing bearer token"
}
```

### 500 Internal Server Error
WhisperX execution failed:
```json
{
  "detail": {
    "message": "WhisperX execution failed",
    "stderr": "error message from whisperx",
    "stdout": "output from whisperx",
    "command": ["whisperx", "..."]
  }
}
```

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Successful transcription |
| 400 | Bad request (missing parameters, validation error) |
| 401 | Unauthorized (invalid API key) |
| 422 | Unprocessable entity (validation error) |
| 500 | Internal server error (WhisperX execution failed) |

## Rate Limiting

Currently not implemented. Each transcription processes sequentially based on system resources.

## Supported Audio Formats

WhisperX supports all formats supported by ffmpeg:
- MP3
- WAV
- M4A
- FLAC
- OGG
- MP4 (video)
- WebM
- etc.

## Performance Notes

- Processing time depends on audio duration and model size
- GPU is highly recommended for acceptable performance
- Diarization adds significant processing time
- Larger models (large-v3) are more accurate but slower
- Batch processing is handled internally based on `batch_size` parameter
