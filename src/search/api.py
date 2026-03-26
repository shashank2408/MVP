"""FastAPI search endpoints."""

import os
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from clients.opensearch_client import OpenSearchClient
from search.searcher import OpenSearchSearcher

app = FastAPI(title="Product Search API")

_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

_searcher: OpenSearchSearcher | None = None


def get_searcher() -> OpenSearchSearcher:
    global _searcher
    if _searcher is None:
        client = OpenSearchClient(
            host=os.getenv("OPENSEARCH_HOST", "localhost"),
            port=int(os.getenv("OPENSEARCH_PORT", "9200")),
        )
        _searcher = OpenSearchSearcher(
            client=client,
            index_name=os.getenv("OPENSEARCH_INDEX", "products"),
        )
    return _searcher


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Product Search</title>
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>
  <header>
    <h1>Product Search</h1>
    <span>MVP</span>
  </header>
  <main>
    <div class="search-card">
      <div class="search-row">
        <input type="text" id="query" placeholder="Search for products..." />
        <button class="search-btn" onclick="runSearch()">Search</button>
      </div>
      <div class="tabs">
        <button class="tab active" data-type="keyword">Keyword</button>
        <button class="tab" data-type="fuzzy">Fuzzy</button>
        <button class="tab" data-type="phrase">Phrase</button>
        <button class="tab" data-type="vector">Vector</button>
        <button class="tab" data-type="hybrid">Hybrid</button>
      </div>
    </div>

    <div id="results-header" class="results-header" style="display:none">
      <h2 id="search-label"></h2>
      <span class="count" id="result-count"></span>
    </div>
    <div id="results" class="results-list"></div>
  </main>

  <script>
    let activeType = "keyword";

    document.querySelectorAll(".tab").forEach(tab => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        activeType = tab.dataset.type;
        const q = document.getElementById("query").value.trim();
        if (q) runSearch();
      });
    });

    document.getElementById("query").addEventListener("keydown", e => {
      if (e.key === "Enter") runSearch();
    });

    async function runSearch() {
      const q = document.getElementById("query").value.trim();
      if (!q) return;
      const results = document.getElementById("results");
      results.innerHTML = '<div class="loading">Searching...</div>';
      document.getElementById("results-header").style.display = "flex";
      document.getElementById("search-label").textContent =
        activeType.charAt(0).toUpperCase() + activeType.slice(1) + " search";
      try {
        const res = await fetch(`/search/${activeType}?q=${encodeURIComponent(q)}&size=10`);
        if (!res.ok) throw new Error(res.statusText);
        const data = await res.json();
        document.getElementById("result-count").textContent = `${data.length} result${data.length !== 1 ? "s" : ""}`;
        results.innerHTML = data.length ? data.map(renderCard).join("") : '<div class="empty-state">No results found.</div>';
      } catch (err) {
        results.innerHTML = `<div class="error-msg">Error: ${err.message}</div>`;
      }
    }

    function renderCard(p) {
      const tags = (p.tags || []).map(t => `<span class="tag-pill">${t}</span>`).join("");
      const price = p.price != null ? `$${Number(p.price).toFixed(2)}` : "";
      return `
        <div class="result-card">
          <div class="name">${p.name || ""}</div>
          <div class="price">${price}</div>
          <div class="meta">${p.category || ""} ${p.brand ? "· " + p.brand : ""} · ${p.locale || ""}</div>
          ${tags ? `<div class="tags">${tags}</div>` : ""}
        </div>`;
    }
  </script>
</body>
</html>"""


@app.get("/search/keyword")
def keyword_search(q: str = Query(..., description="Search query"), size: int = 10) -> JSONResponse:
    return JSONResponse(get_searcher().keyword(q, size))


@app.get("/search/fuzzy")
def fuzzy_search(q: str = Query(..., description="Search query"), size: int = 10) -> JSONResponse:
    return JSONResponse(get_searcher().fuzzy(q, size))


@app.get("/search/phrase")
def phrase_search(q: str = Query(..., description="Search query"), size: int = 10) -> JSONResponse:
    return JSONResponse(get_searcher().phrase(q, size))


@app.get("/search/vector")
def vector_search(q: str = Query(..., description="Search query"), size: int = 10) -> JSONResponse:
    return JSONResponse(get_searcher().vector(q, size))


@app.get("/search/hybrid")
def hybrid_search(q: str = Query(..., description="Search query"), size: int = 10) -> JSONResponse:
    return JSONResponse(get_searcher().hybrid(q, size))
