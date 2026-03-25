# AI Engineer Portfolio Project – LLM + RAG Assistant

## Overview

This project is a production-oriented AI application that demonstrates how to build, deploy, and operate an LLM-powered system with Retrieval-Augmented Generation (RAG), fallback handling, and observability.

It is designed to showcase real-world AI engineering practices including API design, system reliability, and intelligent response generation using structured and unstructured data.

---

## Key Features

* LLM-powered conversational assistant using OpenAI APIs
* Retrieval-Augmented Generation (RAG) using ChromaDB
* Context-aware response generation with prompt injection
* Multi-mode responses:

  * Direct answers for simple queries
  * Consultative reasoning for complex inputs
* Graceful fallback when LLM or vector search fails
* Observability features:

  * Request ID tracking
  * Latency measurement
  * Diagnostics in API responses
* Intent detection and human handoff logic
* Deployment-ready (Docker + Render)
* Lightweight evaluation workflow

---

## System Architecture

### High-Level Flow

User → Frontend → Flask API → Vector Retrieval → Prompt Construction → LLM → Response + Diagnostics

---

### Components

* **Frontend:** Chat interface (HTML, CSS, JavaScript)
* **Backend:** Flask API for orchestration
* **LLM Layer:** OpenAI chat completions
* **Retrieval Layer:** ChromaDB vector database
* **Observability:** Latency tracking, request IDs, diagnostics
* **Fallback System:** Local response generation when dependencies fail

---

## Request Flow

1. User sends message to `/api/chat`
2. Backend classifies query (direct vs consultative)
3. Vector search retrieves relevant context
4. Context is injected into prompt
5. LLM generates structured response
6. API returns:

   * answer
   * suggested questions
   * diagnostics
   * latency

If any component fails:

* System returns a **safe fallback response**

---

## Why This Project Stands Out

Unlike typical chatbot demos, this system demonstrates:

* Production-style API architecture
* Failure-aware system design
* Graceful degradation when services fail
* Separation of concerns across retrieval, prompting, and generation
* Observability and diagnostics built into responses
* Deployment-ready infrastructure

This project focuses on **building reliable AI systems**, not just calling an LLM API.

---

## Tech Stack

* Python
* Flask + Flask-CORS
* OpenAI API
* ChromaDB (Vector Database)
* HTML, CSS, JavaScript
* Docker
* Render

---

## API Endpoints

| Endpoint      | Method | Description                          |
| ------------- | ------ | ------------------------------------ |
| `/`           | GET    | Serves frontend UI                   |
| `/api/chat`   | POST   | Handles user queries with RAG + LLM  |
| `/api/health` | GET    | System health status                 |
| `/api/status` | GET    | Service capabilities and diagnostics |

---

## Setup Instructions

```bash
pip install -r requirements.txt
python build_vectordb.py
python app.py
```

Open:

```
http://localhost:5000
```

---

## Environment Variables

```env
OPENAI_API_KEY=your_api_key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIR=personal_vectordb
APP_ENV=development
```

---

## Evaluation Strategy

This project includes a lightweight evaluation workflow to validate:

* API availability
* Response quality
* Fallback behavior
* Latency tracking

```bash
python evaluate.py
```

---

## Design Decisions

* **Flask backend** for simplicity and clear API structure
* **ChromaDB** for lightweight, local RAG demonstration
* **JSON responses** for predictable frontend integration
* **Prompt templates** for controlled response behavior
* **Optional retrieval layer** to ensure system resilience

---

## Failure Handling Strategy

This system is designed to remain functional under failure conditions:

* If OpenAI API fails:

  * Returns structured fallback response
* If vector search fails:

  * Continues without retrieval
* If both fail:

  * Returns safe local response

This ensures **graceful degradation instead of system failure**.

---

## Observability & Monitoring

The system includes built-in diagnostics:

* `request_id` for tracing requests
* `latency_ms` for performance tracking
* Error indicators for:

  * vector search
  * model calls

This helps in debugging and performance monitoring.

---

## Limitations

* Uses ChromaDB (not optimized for large-scale production)
* No hybrid or re-ranking retrieval strategy
* No multi-agent orchestration
* No persistent conversation memory
* Limited evaluation metrics

---

## Future Improvements

* Add agent orchestration (LangGraph / CrewAI)
* Upgrade vector database (OpenSearch / Elasticsearch)
* Implement hybrid search and re-ranking
* Add CI/CD pipeline
* Introduce advanced evaluation metrics
* Add user feedback loop and analytics

---

## Portfolio Summary

This project demonstrates:

* End-to-end LLM application development
* RAG-based system design
* Failure-aware backend engineering
* API-driven architecture
* Deployment-ready AI systems

It reflects practical experience in building **real-world AI applications**, not just experimental models.

---
