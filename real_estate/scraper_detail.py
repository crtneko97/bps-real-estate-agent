# real_estate/scraper_detail.py

import re
from typing import Optional

from bs4 import BeautifulSoup

from .http_client import fetch_soup
from .models import ListingSummary, ListingDetail

INT_RE = re.compile(r"[^\d]")

def _int_from_text(text: str) -> Optional[int]:
    digits = INT_RE.sub("", text)
    return int(digits) if digits else None

def enrich_with_detail(summary: ListingSummary) -> ListingDetail:
    soup = fetch_soup(summary.url)
    text = soup.get_text(" ", strip=True)

    # Some patterns we know are present from the accessible HTML.:contentReference[oaicite:3]{index=3}
    drift_cost = None
    m = re.search(r"Driftskostnaden är ([\d\s]+) kr/mån", text)
    if m:
        drift_cost = _int_from_text(m.group(1))

    floor_of = None
    m = re.search(r"Den ligger på våning\s+(\d+\s+av\s+\d+)", text)
    if m:
        floor_of = m.group(1)

    days_on_booli = None
    m = re.search(r"varit till salu i (\d+) dagar", text)
    if m:
        days_on_booli = int(m.group(1))

    views = None
    m = re.search(r"har (\d+)\s+sidvisningar på Booli", text)
    if m:
        views = int(m.group(1))

    ownership_type = None
    m = re.search(r"Den här lägenheten är en ([^.]+)\.", text)
    if m:
        ownership_type = m.group(1).strip()

    building_year = None
    m = re.search(r"Byggår\s+(\d{4})", text)
    if m:
        building_year = int(m.group(1))

    # Broker information (we may need to tweak this once you inspect the full HTML)
    broker_name = None
    broker_company = None

    heading = soup.find(
        lambda tag: tag.name in {"h2", "h3"}
        and "Ansvarig mäklare" in tag.get_text()
    )
    if heading:
        broker_block = heading.find_next("article") or heading.find_next("div")
        if broker_block:
            # Usually "Anders Ångström Svensk Fastighetsförmedling" etc.
            broker_text = broker_block.get_text(" ", strip=True)
            # naive split: first two words name, rest company
            parts = broker_text.split()
            if len(parts) >= 2:
                broker_name = " ".join(parts[:2])
            if len(parts) > 2:
                broker_company = " ".join(parts[2:])

    broker_website_url = None
    link = soup.find("a", string=lambda s: s and "Läs mer hos mäklaren" in s)
    if link and link.has_attr("href"):
        broker_website_url = link["href"]

    return ListingDetail(
        **summary.__dict__,
        drift_cost_sek=drift_cost,
        floor_of=floor_of,
        days_on_booli=days_on_booli,
        booli_views=views,
        ownership_type=ownership_type,
        building_year=building_year,
        broker_name=broker_name,
        broker_company=broker_company,
        broker_website_url=broker_website_url,
    )
