# real_estate/http_client.py  (optional but nice)

import requests
from bs4 import BeautifulSoup
from .config import USER_AGENT, REQUEST_TIMEOUT

HEADERS = {"User-Agent": USER_AGENT}

def fetch_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")
