# ── Base image ─────────────────────────────────────────────────
FROM python:3.11-slim

# Build args (for Chinese mirror support)
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_EXTRA_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# ── System dependencies ───────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # pdf2image needs poppler
    poppler-utils \
    # libs for PaddlePaddle / OpenCV
    libgomp1 \
    libxext6 \
    libsm6 \
    libxrender1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ───────────────────────────────────────
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 300 \
    -i "${PIP_INDEX_URL}" \
    --extra-index-url "${PIP_EXTRA_INDEX_URL}" \
    -r requirements.txt

# ── App code ──────────────────────────────────────────────────
COPY app/ ./app/

RUN mkdir -p /tmp/df_ocr/uploads && chmod 777 /tmp/df_ocr/uploads

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
