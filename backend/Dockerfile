FROM python:3.11-slim AS deps

WORKDIR /app
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt


FROM python:3.11-slim AS runtime

RUN useradd -m appuser

WORKDIR /app
COPY --from=deps /usr/local /usr/local
COPY . .

RUN mkdir -p data && chown -R appuser:appuser /app

USER appuser

EXPOSE 18080

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c \
    "import urllib.request; \
    urllib.request.urlopen('http://localhost:18080/health')" \
    || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "18080"]
