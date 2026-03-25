# Render Deployment Guide

This guide explains how to deploy the personal AI assistant to Render.

## Quick Setup

1. Push the project to GitHub
2. Create a new Render web service
3. Name it `personal-ai-assistant`
4. Set the build command to `pip install -r requirements.txt && python build_vectordb.py`
5. Set the start command to `gunicorn --bind 0.0.0.0:$PORT app:app`
6. Add `OPENAI_API_KEY`
7. Add `CHROMA_PERSIST_DIR=/tmp/vectordb`
