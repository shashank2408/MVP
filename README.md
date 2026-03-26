# Product Search Pipeline

A real-time product search platform built on Kafka and OpenSearch. Product events stream through an enrichment pipeline that generates semantic embeddings, then get indexed and exposed through a multi-modal search API with a browser UI.

---

## What It Does

- Ingests product lifecycle events (created, viewed, sold, returned, etc.) via Kafka
- Enriches each product with tags, synonyms, search keywords, and a semantic embedding vector
- Indexes enriched products into OpenSearch with a KNN-ready mapping
- Exposes five search strategies through a REST API and browser UI

---

## Architecture

```
products.json
     │
     ▼
 [Producer] ──► Kafka (port 9092) ──► [Consumer]
                                           │
                                     [Enricher]
                                     · tags + synonyms
                                     · semantic embedding
                                           │
                                           ▼
                                     [OpenSearch] ◄── [Search API]
                                      (port 9200)       (port 8000)
```

| Service | Container | Port |
|---|---|---|
| Kafka broker | `kafka` | `9092` (external), `29092` (internal) |
| OpenSearch | `opensearch` | `9200` |
| Producer | `producer` | — |
| Consumer | `consumer` | — |
| Search API | `search-api` | `8000` |

---

## Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development only)

---

## Getting Started

**1. Clone and start all services**

```bash
docker compose up --build
```

Startup order is orchestrated automatically via healthchecks:
1. Kafka and OpenSearch initialise
2. Producer publishes product events to Kafka
3. Consumer enriches and indexes products into OpenSearch
4. Search API becomes available at `http://localhost:8000`

**2. Verify data is indexed**

```bash
curl http://localhost:9200/products/_count
```

**3. Open the search UI**

Navigate to `http://localhost:8000` in your browser.

---

## Search API

Base URL: `http://localhost:8000`

All search endpoints accept a `q` (query string) and optional `size` (default `10`) parameter.

| Endpoint | Strategy | Description |
|---|---|---|
| `GET /search/keyword?q=` | Multi-match | Exact and partial term matching across name, category, tags, and brand |
| `GET /search/fuzzy?q=` | Fuzzy | Tolerates typos and spelling variations |
| `GET /search/phrase?q=` | Phrase | Matches the exact phrase in order |
| `GET /search/vector?q=` | KNN vector | Semantic similarity using `all-MiniLM-L6-v2` embeddings |
| `GET /search/hybrid?q=` | Hybrid | Combines BM25 keyword score with vector similarity |

**Example**

```bash
curl "http://localhost:8000/search/hybrid?q=wireless+headphones&size=5"
```

---

## Adding Products

Products are driven from `products.json` at the project root. Each entry is a product event:

```json
{
  "event_id": "evt-1001",
  "event_type": "PRODUCT_CREATED",
  "product_id": "p101",
  "name": "Lululemon Yoga Mat",
  "category": "fitness",
  "price": 109.99,
  "locale": "en-CA",
  "timestamp": "2026-03-19T08:15:00Z"
}
```

**Supported event types:** `PRODUCT_CREATED`, `PRODUCT_VIEWED`, `PRODUCT_ADDED_TO_CART`, `PRODUCT_ADDED_TO_WISHLIST`, `PRODUCT_SOLD`, `PRODUCT_RETURNED`, `PRODUCT_RESTOCKED`, `PRODUCT_DISCOUNTED`

After updating `products.json`, re-run the producer:

```bash
docker compose up -d --build --no-deps producer
```

Documents are upserted by `product_id` — re-publishing events for an existing product updates it in place.

---

## Supplemental Metadata

`tags.json` provides additional enrichment keyed by `product_id`:

```json
{
  "p101": {
    "brand": "Lululemon",
    "labels": ["yoga", "fitness", "non-slip"],
    "synonyms": ["exercise mat", "gym mat"]
  }
}
```

---

## Project Structure

```
├── compose.yml                  — all services
├── products.json                — product event input
├── tags.json                    — supplemental metadata
├── kafka/                       — Kafka Docker image (KRaft mode)
├── opensearch/                  — OpenSearch Docker image
├── producer/                    — Producer Dockerfile
├── consumer/                    — Consumer Dockerfile
├── search/                      — Search API Dockerfile
└── src/
    ├── base/                    — domain models and base abstractions
    ├── clients/                 — Kafka and OpenSearch clients
    ├── enrichment/              — product enrichment + embedding generation
    ├── indexing/                — OpenSearch mapping, index config factory, indexer
    ├── pipeline/                — producer/consumer orchestration and entrypoints
    └── search/                  — search methods and FastAPI endpoints
```

---

## Local Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run producer locally (requires Kafka running)
PYTHONPATH=src python -m pipeline.run_producer \
  --input products.json \
  --topic product-updates \
  --bootstrap-servers localhost:9092

# Run consumer locally (requires Kafka + OpenSearch running)
PYTHONPATH=src python -m pipeline.run_consumer \
  --topic product-updates \
  --bootstrap-servers localhost:9092 \
  --tags tags.json \
  --index products \
  --opensearch-host localhost \
  --opensearch-port 9200

# Run search API locally
PYTHONPATH=src uvicorn search.api:app --reload
```
