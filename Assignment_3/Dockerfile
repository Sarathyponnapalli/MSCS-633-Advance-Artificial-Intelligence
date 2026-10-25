# Terminal Q&A chatbot (Django + ChatterBot). Everything runs inside the
# container, so nothing is installed on the host.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run as an unprivileged user that owns the SQLite database.
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# Create the database and train the bot at build time so chat starts instantly.
RUN python manage.py migrate --noinput && python manage.py train

CMD ["python", "manage.py", "chat"]
