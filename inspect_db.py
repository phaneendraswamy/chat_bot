import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "vectordb")

client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = client.get_collection("lumen_data_docs")

data = collection.get(include=["metadatas"])

urls = set()

for meta in data["metadatas"]:
    if meta and meta.get("source_type") == "web":
        urls.add(meta.get("source_url"))

print(f"\nTotal unique web links in DB: {len(urls)}\n")
for url in sorted(urls):
    print(url)
