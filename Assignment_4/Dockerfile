# Unsupervised credit card fraud detection with a PyOD AutoEncoder.
# Everything runs inside the container, so nothing is installed on the host.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MPLBACKEND=Agg

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run as an unprivileged user; data/ and output/ are usually bind-mounted.
RUN useradd --create-home appuser \
    && mkdir -p data output \
    && chown -R appuser /app
USER appuser

CMD ["python", "fraud_detection.py"]
