FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY tags.json .

ENV PYTHONPATH=/app/src

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

CMD ["python", "-m", "pipeline.run_consumer", "--topic", "product-updates", "--bootstrap-servers", "kafka:29092", "--tags", "tags.json", "--index", "products", "--opensearch-host", "opensearch", "--opensearch-port", "9200"]
