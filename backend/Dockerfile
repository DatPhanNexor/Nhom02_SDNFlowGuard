# SDNFlowGuard Backend REST API Container
# Multi-layered, secure, non-root Python 3.10 runtime
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SDNFLOW_FLASK_HOST=0.0.0.0 \
    SDNFLOW_FLASK_PORT=5000 \
    SDNFLOW_DB_PATH=/app/database/sdnflowguard.db \
    SDNFLOW_DEFENSE_MODE=DRY_RUN

WORKDIR /app

# Install Python dependencies cleanly without caching wheels
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend application source
COPY . /app/

# Create application user and set file permissions
RUN useradd -m -u 1000 sdnflow && \
    mkdir -p /app/database /app/logs && \
    chown -R sdnflow:sdnflow /app

USER sdnflow

EXPOSE 5000

# Non-destructive native python healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/api/health', timeout=3).getcode() == 200 else 1)" || exit 1

CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app", "--workers", "1", "--threads", "4", "--timeout", "60"]

