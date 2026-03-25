import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "PersonalProjectBot/1.0"}


def scrape_page(url, timeout=10):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for s in soup(["script", "style", "noscript"]):
            s.decompose()

        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


def find_internal_links(base_url, html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    base_domain = urlparse(base_url).netloc
    links = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        parsed = urlparse(href)
        if parsed.netloc == base_domain and parsed.scheme in ("http", "https"):
            links.add(href.split("#")[0])
    return list(links)


def scrape_multiple(urls):
    out = {}
    for i, url in enumerate(urls):
        try:
            print("Scraping", url)
            text = scrape_page(url)
            if text and text.strip():
                out[f"doc_{i}"] = text
            else:
                print(f"Empty content for {url}")
        except Exception as e:
            print("Failed", url, e)
        time.sleep(0.5)
    return out


if __name__ == "__main__":
    pages = ["https://example.com/"]
    docs = scrape_multiple(pages)
    for k, v in docs.items():
        print(k, len(v))
