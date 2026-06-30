FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

# Default: run the demo pipeline (real data is fetched via scripts/realdata/ at runtime)
CMD ["python", "-m", "mm_tte_survival.cli", "make-demo-data", "--out", "data/demo"]
