import os

import chromadb
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env", override=True)
load_dotenv(".env.local", override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "vectordb")
HEADERS = {"User-Agent": "PersonalProjectBot/1.0"}

chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = chroma_client.get_or_create_collection("personal_project_docs")


def embed_text(text: str):
    resp = client.embeddings.create(model="text-embedding-3-small", input=text)
    return resp.data[0].embedding


def chunk_text(text: str, chunk_size=1000, overlap=200):
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)


def scrape_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


with open("links.txt", "r", encoding="utf-8") as f:
    urls = [line.strip().strip('"\'') for line in f if line.strip() and line.startswith("http")]

for url in urls:
    print(f"Scraping {url}")
    content = scrape_page(url)
    if not content or len(content) < 200:
        continue

    title = url.split("/")[-1].replace("-", " ").title() or "Home"
    category = "industry" if "/industries/" in url else "partner" if "/partners/" in url else "general"

    chunks = chunk_text(content)
    for i, chunk in enumerate(chunks):
        collection.add(
            ids=[f"web_{hash(url)}_{i}"],
            documents=[chunk],
            embeddings=[embed_text(chunk)],
            metadatas=[
                {
                    "source_url": url,
                    "title": title,
                    "category": category,
                    "source_type": "web",
                }
            ],
        )

print("Vector DB updated with current project content.")
