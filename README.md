# AI Engineer Portfolio Project

This project is a production-minded LLM application designed to align with AI Engineer roles like the Meltwater opening you shared. It demonstrates user-facing chat, Retrieval-Augmented Generation (RAG), fallback handling, deployment readiness, and lightweight evaluation workflows.

## Why this fits the role

- LLM application delivery with OpenAI chat completions
- RAG with ChromaDB and semantic retrieval
- Failure-aware backend design with safe fallbacks
- Health and status endpoints for runtime diagnostics
- Deployment-ready Flask service with Render and Docker support
- Evaluation harness for prompt and response quality checks

## Tech stack

- Python
- Flask + Flask-CORS
- OpenAI API
- ChromaDB
- HTML, CSS, JavaScript frontend
- Render deployment config
- Docker containerization

## Key endpoints

- `GET /` serves the UI
- `POST /api/chat` handles user chat requests
- `GET /api/health` returns runtime health information
- `GET /api/status` returns system capabilities and project metadata

## Local setup

```bash
pip install -r requirements.txt
python build_vectordb.py
python app.py
```

Open `http://localhost:5000`.

## Environment variables

```env
OPENAI_API_KEY=your_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIR=personal_vectordb
API_BASE_URL=http://localhost:5000
APP_ENV=development
```

## Evaluation

This repo includes a lightweight evaluation script so you can show that you think beyond demos.

```bash
python evaluate.py
```

It checks:
- endpoint availability
- basic response quality
- fallback behavior
- latency reporting

## Portfolio talking points

- Built an end-to-end LLM application with Flask, OpenAI, and vector retrieval
- Implemented graceful degradation when the LLM or retrieval layer fails
- Added health/status endpoints and diagnostics for production readiness
- Structured the project for deployment, observability, and evaluation

## Next upgrades

- swap Chroma for OpenSearch or Elasticsearch
- add agent orchestration with LangGraph
- add conversation persistence and feedback analytics
- deploy with Docker + CI/CD pipeline
