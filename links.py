import json
import re
from urllib.parse import urlparse

INPUT_FILE = "links.txt"
OUTPUT_FILE = "documents.json"


def sanitize_url(raw: str) -> str:
    return raw.strip().strip('"').strip("'")


def infer_category(url: str) -> str:
    if "/partners/" in url:
        return "partner"
    if "/services/" in url:
        return "service"
    if "/industries/" in url or "/financial-services" in url:
        return "industry"
    if "/blogs" in url or "/blog" in url:
        return "blog"
    if "/resource/" in url:
        return "resource"
    return "general"


def make_id(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-").lower() or "home"


def make_title(url: str) -> str:
    slug = urlparse(url).path.strip("/").split("/")[-1]
    return (slug or "home").replace("-", " ").title()


def generate_documents(urls):
    documents = []

    for raw in urls:
        url = sanitize_url(raw)
        if not url or not url.startswith("http"):
            continue

        title = make_title(url)
        category = infer_category(url)

        documents.append(
            {
                "id": make_id(url),
                "title": title,
                "url": url,
                "category": category,
                "content": f"{title} information captured for this personal project.",
            }
        )

    return {"documents": documents}


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = f.readlines()

    data = generate_documents(urls)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Generated {len(data['documents'])} documents -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
