# BIS Standards RAG Engine

### AI-Powered Recommendation Engine for Indian Standards

A Retrieval-Augmented Generation (RAG) engine that identifies potentially applicable Indian Standards for **procurement specifications, product descriptions, technical requirements, and tender documents**.

Built for **Smart India Hackathon 2026 — SIH26108**.

---

## What It Does

The system combines semantic and keyword retrieval to find relevant Indian Standards and provides evidence-grounded recommendations including:

- Applicable standards
- Current editions and amendments
- Scope and technical requirements
- Testing and inspection requirements
- Allied and referenced standards
- BIS certification / CRS information where available
- Procurement relevance
- Confidence and supporting evidence

### Core Principle

> **Retrieve the relevant BIS evidence first, then use the LLM to explain it.**

The LLM is not treated as the source of truth.

---

## Architecture

```text
Query / Tender
      │
      ▼
Query Normalization
      │
      ▼
┌───────────────────────┐
│    Hybrid Retrieval   │
│                       │
│ Vector + Keyword      │
└───────────┬───────────┘
            ▼
         Ranking
            ▼
    Relevance Filtering
            ▼
     Confidence Scoring
            ▼
    Metadata Enrichment
            ▼
 Standards Relationships
            ▼
         Evidence
            ▼
           LLM
            ▼
     Structured JSON
```

---

## Retrieval

### Semantic Search

Uses:

```text
BAAI/bge-small-en-v1.5
```

with **384-dimensional embeddings** and MongoDB Atlas Vector Search.

### Keyword Search

MongoDB Atlas Search provides exact matching for:

- IS numbers
- Part numbers
- Technical terminology
- Product terminology

### Hybrid Search

Vector and keyword results are retrieved in parallel and combined using rank-based scoring.

---

## Knowledge Base

Standards are stored as structured records plus searchable evidence chunks.

Metadata can include:

```text
Standard number
Title
Scope
Category
Applicable domains
Keywords
Technical requirements
Testing and inspection
Allied standards
Current edition
Amendments
Compliance
Procurement relevance
Standard relationships
Source
```

Database:

```text
MongoDB Atlas
├── standards
└── chunks
```

---

## Tender Support

Tender documents can be processed to extract:

```text
Product
Materials
Performance
Testing
Certification
Intended use
Installation context
```

These requirements are then passed through the same RAG pipeline.

---

## LLM Layer

Provider fallback chain:

```text
Groq
  ↓
Mistral
  ↓
OpenRouter
  ↓
Deterministic RAG fallback
```

Providers use short timeouts and disabled retries.

If all providers fail, the system can still return a structured response based on retrieved evidence.

---

## Example

**Query**

```text
What Indian Standard applies to reinforced concrete water storage tanks?
```

**Example result**

```text
Primary:
IS 3370 (Part 2):2021

Supporting:
IS 3370 (Part 1):2021

Related:
IS 456:2000
```

The response can also include edition, amendments, testing, certification information, procurement relevance, relationships, and retrieved evidence.

---

## Performance

Representative RAG timings:

```text
Parallel retrieval:        ~0.54 s
Metadata enrichment:       ~0.87 s
Relationship expansion:    ~0.32 s
Total RAG recommendation:  ~1.8 s
```

A complete LLM recommendation request was successfully tested at approximately **4.55 seconds**.

---

## API

```text
GET  /health
POST /recommend
POST /recommend/llm
POST /recommend/llm/tender
```

FastAPI documentation:

```text
/docs
```

---

## Tech Stack

| Component | Technology |
|---|---|
| API | FastAPI |
| Database | MongoDB Atlas |
| Vector Search | MongoDB Atlas Vector Search |
| Keyword Search | MongoDB Atlas Search |
| Embeddings | BGE-small-en-v1.5 |
| LLM | Groq / Mistral / OpenRouter |
| PDF Processing | PyMuPDF |
| Validation | Pydantic |
| Language | Python |

---

## Limitations

- Recommendation quality depends on the indexed standards dataset.
- Semantic similarity does not always mean direct procurement applicability.
- Certification requirements may depend on current regulations and QCOs.
- The knowledge base does not represent the complete BIS catalogue.
- Final procurement decisions should be verified against authoritative BIS sources.

---

## Future Work

- Expand BIS standards coverage
- Domain-specific reranking
- Improved multilingual retrieval
- Automated BIS source verification
- Expanded certification/QCO mapping
- OCR and table extraction for tender documents
- Retrieval evaluation benchmarks

---

## Core Idea

```text
Knowledge Base
      ↓
Retrieval
      ↓
Ranking
      ↓
Evidence
      ↓
LLM Explanation
```

> **Retrieve first. Reason over retrieved evidence second.**
