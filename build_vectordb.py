import json
import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)
load_dotenv(".env.local", override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "vectordb")
JSON_FILE = "documents.json"
KNOWLEDGE_BASE_DIR = "knowledge_base"

client = OpenAI(api_key=OPENAI_API_KEY)
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = chroma_client.get_or_create_collection("personal_project_docs")


def embed_text(text: str):
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding


def chunk_text(text: str, max_words=400):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i : i + max_words])


def ingest_json_documents():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for doc in data["documents"]:
        base_id = doc["id"]
        url = doc["url"]
        category = doc.get("category", "general")
        title = doc.get("title", "")
        content = doc["content"]

        for i, chunk in enumerate(chunk_text(content)):
            collection.add(
                ids=[f"{base_id}_{i}"],
                documents=[chunk],
                embeddings=[embed_text(chunk)],
                metadatas=[
                    {
                        "source_url": url,
                        "category": category,
                        "title": title,
                        "source_type": "web",
                    }
                ],
            )


def ingest_txt_files():
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        return

    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if not filename.lower().endswith(".txt"):
            continue

        filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            continue

        base_id = os.path.splitext(filename)[0]

        for i, chunk in enumerate(chunk_text(text)):
            collection.add(
                ids=[f"internal_{base_id}_{i}"],
                documents=[chunk],
                embeddings=[embed_text(chunk)],
                metadatas=[
                    {
                        "source_url": "internal",
                        "category": "internal",
                        "title": base_id.replace("_", " ").title(),
                        "source_type": "internal",
                    }
                ],
            )


if __name__ == "__main__":
    ingest_json_documents()
    ingest_txt_files()
    print("Vector DB build complete (JSON + TXT).")
