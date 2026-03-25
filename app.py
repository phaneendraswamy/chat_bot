import json
import logging
import os
import time
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from openai import OpenAI

load_dotenv(".env", override=True)
load_dotenv(".env.local", override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "personal_vectordb")
APP_ENV = os.getenv("APP_ENV", "development")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

if OPENAI_API_KEY:
    logger.info("Loaded OpenAI API key ending with: %s", OPENAI_API_KEY[-6:])
else:
    logger.warning("OPENAI_API_KEY is not set.")

app = Flask(__name__, static_url_path="", static_folder=".")
CORS(app)

MAX_HISTORY = 8

DIAGRAM_MAP = {
    "architecture": "https://www.informatica.com/content/dam/informatica-com/en/images/misc/mdm-reference-architecture-diagram.png",
    "mdm": "https://www.informatica.com/content/dam/informatica-com/en/images/misc/mdm-reference-architecture-diagram.png",
    "healthcare": "https://cdn-icons-png.flaticon.com/512/2966/2966334.png",
    "manufacturing": "https://cdn-icons-png.flaticon.com/512/3061/3061341.png",
    "financial": "https://cdn-icons-png.flaticon.com/512/2168/2168666.png",
    "finance": "https://cdn-icons-png.flaticon.com/512/2168/2168666.png",
    "retail": "https://cdn-icons-png.flaticon.com/512/3081/3081559.png",
    "education": "https://cdn-icons-png.flaticon.com/512/2232/2232688.png",
    "public": "https://cdn-icons-png.flaticon.com/512/4205/4205906.png",
    "travel": "https://cdn-icons-png.flaticon.com/512/3125/3125848.png",
}

INTENT_LINKS = {
    "pricing": "/",
    "contact": "/",
    "portfolio": "/",
}

try:
    from vector_search import search as vector_search

    VECTOR_ENABLED = True
    VECTOR_IMPORT_ERROR = None
except Exception as exc:
    VECTOR_ENABLED = False
    VECTOR_IMPORT_ERROR = str(exc)
    logger.warning("vector_search import failed: %s", exc)


def get_relevant_diagram(message, ai_response):
    text = (message + " " + ai_response).lower()
    if "architecture" in text or "tech stack" in text:
        return DIAGRAM_MAP["architecture"]
    if "mdm" in text or "master data" in text:
        return DIAGRAM_MAP["mdm"]
    for key, url in DIAGRAM_MAP.items():
        if key in text:
            return url
    return None


def detect_handoff(history, message):
    msg = message.lower()
    triggers = ["human", "agent", "support", "person", "stupid", "bad bot", "useless", "talk to someone"]
    if any(t in msg for t in triggers):
        return True
    if len(history) >= 3:
        last_msgs = [h["content"] for h in history[-3:] if h["role"] == "user"]
        if len(last_msgs) == 3 and len(set(last_msgs)) == 1:
            return True
    return False


def build_rag_prompt(context, question):
    return f"""
You are a Retrieval-Augmented Generation assistant.
Answer the user ONLY from the retrieved context below.

CONTEXT:
{context}

USER QUESTION:
{question}

INSTRUCTIONS:
1. Treat "RAG" as "Retrieval-Augmented Generation".
2. Use only the retrieved context. Do not use outside knowledge.
3. If the context does not contain the answer, clearly say that the database does not contain enough information.
4. Do not invent project details.
5. Keep the answer concise and practical.

OUTPUT JSON FORMAT:
{{
  "answer": "Direct answer here.",
  "suggested_questions": ["Ask another question from the database", "Upload more project notes", "Rebuild the vector database"]
}}
"""


def build_local_fallback(message, context_available):
    if context_available:
        answer = (
            "The database returned relevant context, but the language model is unavailable right now. "
            "Please try again in a moment, or ask after restarting the service."
        )
    else:
        answer = (
            "I could not find enough relevant information in the database to answer that. "
            "Add more project documents or notes to the knowledge base, rebuild the vector database, and try again."
        )
    return {
        "answer": answer,
        "suggested_questions": [
            "Ask another question from the database",
            "Upload more project notes",
            "Rebuild the vector database",
        ],
    }


def ask_openai(prompt, history, context_available, user_message):
    if not client:
        return build_local_fallback(user_message, context_available), "no_api_key"

    messages = [{"role": "system", "content": "You are a helpful, practical AI assistant for a portfolio project."}]
    messages.extend(history[-5:])
    messages.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content), None
    except Exception as exc:
        logger.exception("OpenAI chat call failed")
        fallback = build_local_fallback(user_message, context_available)
        fallback["answer"] += f" Technical detail: {type(exc).__name__}."
        return fallback, str(exc)


def safe_vector_search(message, n_results=3):
    if not VECTOR_ENABLED:
        return {"documents": [], "source_urls": [], "error": VECTOR_IMPORT_ERROR or "Vector search disabled"}

    try:
        result = vector_search(message, n_results=n_results)
        result["error"] = None
        return result
    except Exception as exc:
        logger.exception("Vector search failed")
        return {"documents": [], "source_urls": [], "error": str(exc)}


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "environment": APP_ENV,
            "openai_configured": bool(OPENAI_API_KEY),
            "chat_model": OPENAI_CHAT_MODEL,
            "embedding_model": OPENAI_EMBED_MODEL,
            "vector_enabled": VECTOR_ENABLED,
            "vector_persist_dir": CHROMA_PERSIST_DIR,
        }
    )


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(
        {
            "service": "personal-ai-assistant",
            "environment": APP_ENV,
            "capabilities": {
                "chat_generation": bool(client),
                "rag_search": VECTOR_ENABLED,
                "frontend_widget": True,
                "fallback_responses": True,
                "health_checks": True,
            },
            "notes": [
                "This project is designed as an AI Engineer portfolio demo.",
                "It showcases LLM application delivery, RAG integration, fallback handling, and deployment readiness.",
            ],
        }
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    started_at = time.time()
    request_id = str(uuid.uuid4())

    data = request.json or {}
    message = (data.get("message") or "").strip()
    history = data.get("history", [])[-MAX_HISTORY:]

    if not message:
        return jsonify({"error": "Message required", "request_id": request_id}), 400

    if detect_handoff(history, message):
        return jsonify(
            {
                "response": "It sounds like you want human help. I can still help organize the issue, draft a follow-up, or capture next steps.",
                "suggestions": [],
                "handoff": True,
                "success": True,
                "request_id": request_id,
                "latency_ms": round((time.time() - started_at) * 1000, 2),
            }
        )

    vector_result = safe_vector_search(message, n_results=3)
    docs = vector_result.get("documents", [])
    if not docs:
        fallback = build_local_fallback(message, context_available=False)
        latency_ms = round((time.time() - started_at) * 1000, 2)
        return jsonify(
            {
                "response": fallback["answer"],
                "suggestions": fallback["suggested_questions"],
                "image": None,
                "handoff": False,
                "success": True,
                "request_id": request_id,
                "latency_ms": latency_ms,
                "diagnostics": {
                    "vector_error": vector_result.get("error"),
                    "model_error": None,
                    "source_urls": vector_result.get("source_urls", []),
                },
            }
        )

    context = "\n\n".join(docs)
    prompt = build_rag_prompt(context, message)

    history_for_model = history + [{"role": "user", "content": message}]
    parsed, model_error = ask_openai(prompt, history_for_model, context_available=bool(docs), user_message=message)

    answer = parsed.get("answer", "I apologize, I'm having trouble processing that request.")
    suggestions = parsed.get("suggested_questions", ["Start Over"])
    image_url = get_relevant_diagram(message, answer)

    for key, link in INTENT_LINKS.items():
        if key in message.lower():
            answer += f"\n\n{key.capitalize()}: {link}"

    latency_ms = round((time.time() - started_at) * 1000, 2)
    logger.info(
        "chat_request request_id=%s latency_ms=%s vector_error=%s model_error=%s",
        request_id,
        latency_ms,
        bool(vector_result.get("error")),
        bool(model_error),
    )

    return jsonify(
        {
            "response": answer,
            "suggestions": suggestions,
            "image": image_url,
            "handoff": False,
            "success": True,
            "request_id": request_id,
            "latency_ms": latency_ms,
            "diagnostics": {
                "vector_error": vector_result.get("error"),
                "model_error": model_error,
                "source_urls": vector_result.get("source_urls", []),
            },
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
