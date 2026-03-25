# Architecture Overview

## System flow

1. The browser sends a message to `POST /api/chat`.
2. The Flask backend classifies the request as direct or consultative.
3. The backend queries the vector layer for supporting context.
4. Retrieved context is injected into the LLM prompt.
5. The backend returns answer text, suggestions, latency, and diagnostics.
6. If retrieval or model calls fail, the app returns a safe fallback response.

## Design choices

- Flask keeps the backend simple and easy to explain in interviews.
- ChromaDB provides a lightweight local vector layer for RAG demos.
- Structured JSON responses make the UI and evaluation scripts predictable.
- Health and status endpoints help position this as a deployable service, not just a notebook demo.

## Production-minded features

- env-driven configuration
- startup diagnostics
- request IDs
- latency reporting
- fallback responses
- deployment config for Render and Docker
