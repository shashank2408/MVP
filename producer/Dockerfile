FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY products.json .

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "pipeline.run_producer", "--input", "products.json", "--topic", "product-updates", "--bootstrap-servers", "kafka:29092"]
