# One image, two Azure resources:
#   - Container App (backend API):    default CMD below
#   - Container App Job (ingestion):  command overridden to
#     `python -m backend.data.pipeline` in that resource's definition
#
# Chromium + its matching chromedriver are installed from Debian's own
# apt repo (not Google's) specifically so the two versions are always
# paired by the same apt source — avoids the classic chromedriver/Chrome
# version-mismatch failure, and keeps the image fully offline-buildable
# instead of depending on Selenium Manager downloading a browser at
# container startup. Agrowon's adapter is the only one of the three
# sources that needs a real browser (ET Agriculture and Krishi Jagran
# are plain HTTP).

FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BINARY_PATH=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY alembic/ alembic/
COPY alembic.ini .

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
