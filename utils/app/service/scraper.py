# app/service/scraper.py

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FastAPI-Scraper/1.0)"
}

def scrape_url(url: list[str]):
    text_content = []

    for link in url:
        response = requests.get(link, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        paragraphs = soup.find_all("p")
        temp_data = {"url" : link,
                    "content" : "\n".join([para.get_text() for para in paragraphs])}
        text_content.append(temp_data)
        
    return text_content
