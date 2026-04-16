ARG WHISPERX_TAG=no_model

FROM ghcr.io/jim60105/whisperx:${WHISPERX_TAG}

ENV UV_SYSTEM_PYTHON=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY app.py ./

EXPOSE 8010

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
