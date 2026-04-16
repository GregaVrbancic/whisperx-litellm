from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse

APP_NAME = "WhisperX LiteLLM Wrapper"


def get_app_version() -> str:
    """Read version from pyproject.toml."""
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        for line in content.split("\n"):
            if line.startswith('version = "'):
                return line.split('"')[1]
    return "unknown"


APP_VERSION = get_app_version()

WHISPERX_BIN = os.getenv("WHISPERX_BIN", "whisperx")
HF_TOKEN = os.getenv("HF_TOKEN")
API_KEY = os.getenv("WHISPERX_API_KEY")
DEFAULT_MODEL = os.getenv("WHISPERX_MODEL", "large-v3")
DEFAULT_COMPUTE_TYPE = os.getenv("WHISPERX_COMPUTE_TYPE", "float16")
DEFAULT_DEVICE = os.getenv("WHISPERX_DEVICE", "cuda")
DEFAULT_BATCH_SIZE = os.getenv("WHISPERX_BATCH_SIZE", "4")
DEFAULT_OUTPUT_FORMAT = os.getenv("WHISPERX_OUTPUT_FORMAT", "json")
DEFAULT_TASK = os.getenv("WHISPERX_TASK", "transcribe")

app = FastAPI(title=APP_NAME, version=APP_VERSION)


class AuthError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Invalid or missing bearer token")


def require_auth(authorization: str | None) -> None:
    if not API_KEY:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthError()
    token = authorization.split(" ", 1)[1].strip()
    if token != API_KEY:
        raise AuthError()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": APP_NAME,
        "version": APP_VERSION,
        "whisperx_bin": WHISPERX_BIN,
        "default_model": DEFAULT_MODEL,
        "hf_token_configured": bool(HF_TOKEN),
    }


@app.get("/v1/models")
def list_models(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    require_auth(authorization)
    return {
        "object": "list",
        "data": [
            {
                "id": DEFAULT_MODEL,
                "object": "model",
                "owned_by": "local",
                "mode": "audio_transcription",
            }
        ],
    }


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    authorization: str | None = Header(default=None),
    model: str = Form(default=DEFAULT_MODEL),
    language: str | None = Form(default=None),
    task: Literal["transcribe", "translate"] = Form(default=DEFAULT_TASK),
    diarize: bool = Form(default=True),
    batch_size: int = Form(default=int(DEFAULT_BATCH_SIZE)),
    compute_type: str = Form(default=DEFAULT_COMPUTE_TYPE),
    device: str = Form(default=DEFAULT_DEVICE),
    output_format: Literal["json", "txt", "srt", "tsv", "vtt"] = Form(
        default=DEFAULT_OUTPUT_FORMAT
    ),
    min_speakers: int | None = Form(default=None),
    max_speakers: int | None = Form(default=None),
    response_format: Literal["json", "text", "verbose_json"] = Form(default="json"),
) -> JSONResponse | PlainTextResponse:
    require_auth(authorization)
    return await _run_whisperx(
        file=file,
        model=model,
        language=language,
        task=task,
        diarize=diarize,
        batch_size=batch_size,
        compute_type=compute_type,
        device=device,
        output_format=output_format,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
        response_format=response_format,
    )


@app.post("/v1/audio/transcriptions")
async def openai_audio_transcriptions(
    file: UploadFile = File(...),
    authorization: str | None = Header(default=None),
    model: str = Form(default=DEFAULT_MODEL),
    language: str | None = Form(default=None),
    prompt: str | None = Form(default=None),
    response_format: Literal["json", "text", "verbose_json"] = Form(default="json"),
    temperature: float | None = Form(default=None),
    diarize: bool = Form(default=True),
    min_speakers: int | None = Form(default=None),
    max_speakers: int | None = Form(default=None),
) -> JSONResponse | PlainTextResponse:
    require_auth(authorization)
    _ = prompt, temperature
    return await _run_whisperx(
        file=file,
        model=model,
        language=language,
        task="transcribe",
        diarize=diarize,
        batch_size=int(DEFAULT_BATCH_SIZE),
        compute_type=DEFAULT_COMPUTE_TYPE,
        device=DEFAULT_DEVICE,
        output_format="json",
        min_speakers=min_speakers,
        max_speakers=max_speakers,
        response_format=response_format,
    )


async def _run_whisperx(
    *,
    file: UploadFile,
    model: str,
    language: str | None,
    task: str,
    diarize: bool,
    batch_size: int,
    compute_type: str,
    device: str,
    output_format: str,
    min_speakers: int | None,
    max_speakers: int | None,
    response_format: str,
) -> JSONResponse | PlainTextResponse:
    if diarize and not HF_TOKEN:
        raise HTTPException(
            status_code=400, detail="HF_TOKEN is required when diarize=true"
        )

    suffix = Path(file.filename or "upload.bin").suffix or ".bin"
    req_id = uuid.uuid4().hex[:12]

    with tempfile.TemporaryDirectory(prefix=f"whisperx_{req_id}_") as tmpdir:
        tmp = Path(tmpdir)
        input_path = tmp / f"input{suffix}"
        output_dir = tmp / "out"
        output_dir.mkdir(parents=True, exist_ok=True)

        with input_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        cmd = [
            WHISPERX_BIN,
            str(input_path),
            "--model",
            model,
            "--output_dir",
            str(output_dir),
            "--output_format",
            output_format,
            "--compute_type",
            compute_type,
            "--device",
            device,
            "--batch_size",
            str(batch_size),
            "--task",
            task,
        ]

        if language:
            cmd += ["--language", language]
        if diarize:
            cmd += ["--diarize", "--hf_token", HF_TOKEN]
            if min_speakers is not None:
                cmd += ["--min_speakers", str(min_speakers)]
            if max_speakers is not None:
                cmd += ["--max_speakers", str(max_speakers)]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "WhisperX execution failed",
                    "stderr": proc.stderr[-4000:],
                    "stdout": proc.stdout[-2000:],
                    "command": cmd,
                },
            )

        base = input_path.stem
        json_path = output_dir / f"{base}.json"
        txt_path = output_dir / f"{base}.txt"

        if response_format == "text":
            if txt_path.exists():
                return PlainTextResponse(
                    txt_path.read_text(encoding="utf-8", errors="replace")
                )
            if json_path.exists():
                payload = json.loads(json_path.read_text(encoding="utf-8"))
                text = payload.get("text") or "\n".join(
                    seg.get("text", "") for seg in payload.get("segments", [])
                )
                return PlainTextResponse(text)
            raise HTTPException(
                status_code=500, detail="WhisperX did not produce expected text output"
            )

        if not json_path.exists():
            raise HTTPException(
                status_code=500, detail="WhisperX did not produce expected JSON output"
            )

        payload = json.loads(json_path.read_text(encoding="utf-8"))

        if response_format == "json":
            return JSONResponse({"text": payload.get("text", "")})

        verbose = {
            "task": task,
            "language": payload.get("language", language),
            "duration": payload.get("duration"),
            "text": payload.get("text", ""),
            "segments": payload.get("segments", []),
            "words": payload.get("word_segments") or payload.get("words") or [],
            "x_diarization_enabled": diarize,
            "x_request_id": req_id,
            "x_whisperx_model": model,
        }
        return JSONResponse(verbose)
