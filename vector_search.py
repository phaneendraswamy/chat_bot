import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)
load_dotenv(".env.local", override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "vectordb")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

try:
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = chroma_client.get_or_create_collection("personal_project_docs")
except Exception as e:
    print(f"Error initializing ChromaDB client: {e}")
    chroma_client = None
    collection = None


def embed_text(text):
    if not client:
        raise RuntimeError("OpenAI key is required for embeddings")
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding


def search(query, n_results=4):
    if not client:
        raise RuntimeError("OpenAI key is required for embeddings")
    if not chroma_client or not collection:
        return {"documents": [], "source_urls": []}

    try:
        qvec = embed_text(query)
        results = collection.query(query_embeddings=[qvec], n_results=n_results)
        docs = []
        urls = []

        if results.get("documents"):
            docs = [d for d in results["documents"][0] if d]

        if results.get("metadatas"):
            seen_urls = set()
            for meta in results["metadatas"][0]:
                if meta and meta.get("source_url") and meta["source_url"] not in seen_urls:
                    urls.append(meta["source_url"])
                    seen_urls.add(meta["source_url"])

        return {"documents": docs, "source_urls": urls}
    except Exception as e:
        print(f"Error during vector search: {e}")
        return {"documents": [], "source_urls": []}


if __name__ == "__main__":
    q = "What can this personal AI project do?"
    hits = search(q)
    print("Hits:", len(hits))
    for h in hits:
        print(h[:300])
