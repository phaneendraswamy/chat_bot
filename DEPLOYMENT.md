# Deploying to Render

This document provides instructions for deploying the personal AI assistant to Render.

## Prerequisites

1. A Render account
2. An OpenAI API key

## Deployment Steps

1. Push this repository to GitHub
2. Create a new Render web service
3. Use `pip install -r requirements.txt && python build_vectordb.py` as the build command
4. Use `gunicorn --bind 0.0.0.0:$PORT app:app` as the start command
5. Set `OPENAI_API_KEY`
6. Set `CHROMA_PERSIST_DIR=/tmp/vectordb`

Render docs: https://render.com/docs
