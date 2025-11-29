import time
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from .models import ListingSummary, ListingDetail

HEADERS = {
    "User-Agent": "bps-real-estate-bot/0.1 (personal use; contact: your-email)"
}

def fetch(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def parse_price(text: str) -> int:
    # "1 995 000 kr" -> 1995000
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0

def parse_list_page(search_url: str) -> list[ListingSummary]:
    soup = fetch(search_url)
    results: list[ListingSummary] = []

    # TODO: refine selectors with your browser's devtools:
    cards = soup.find_all("h3")  # placeholder – you'll tighten this
    for h3 in cards:
        link = h3.find("a")
        if not link:
            continue
        title = link.get_text(strip=True)
        relative = link["href"]
        url = urljoin(search_url, relative)

        # Walk nearby DOM nodes to find price/area/rooms/floor/fee
        container = h3.parent
        text_block = container.get_text(" ", strip=True)

        # Rough extraction with regex; you can refine:
        price_match = re.search(r"([\d\s]+kr)", text_block)
        area_match = re.search(r"(\d+[,.]?\d*)\s*m²", text_block)
        rooms_match = re.search(r"(\d+[,.]?\d*)\s*rum", text_block)
        fee_match = re.search(r"([\d\s]+kr/mån)", text_block)

        price = parse_price(price_match.group(1)) if price_match else 0
        living_area = float(area_match.group(1).replace(",", ".")) if area_match else 0
        rooms = float(rooms_match.group(1).replace(",", ".")) if rooms_match else 0
        monthly_fee = parse_price(fee_match.group(1)) if fee_match else None

        booli_id_match = re.search(r"/annons/(\d+)", url)
        booli_id = int(booli_id_match.group(1)) if booli_id_match else 0

        summary = ListingSummary(
            booli_id=booli_id,
            url=url,
            address=title,
            area="",     # TODO: parse from "Lägenhet · Aspudden · Stockholm"
            city="",
            price_sek=price,
            living_area_m2=living_area,
            rooms=rooms,
            floor_text=text_block,  # TODO: tighten
            monthly_fee_sek=monthly_fee,
            has_elevator="Hiss" in text_block,
            has_balcony="Balkong" in text_block,
            has_outdoor_space="Uteplats" in text_block,
            status_text=text_block,
        )
        results.append(summary)

    return results

def enrich_with_detail(summary: ListingSummary) -> ListingDetail:
    soup = fetch(summary.url)
    text = soup.get_text(" ", strip=True)

    # Example extractions – refine later with better selectors:
    days_on_booli = None
    match = re.search(r"varit till salu i (\d+) dag", text)
    if match:
        days_on_booli = int(match.group(1))

    # Broker name: often shown near "Ansvarig mäklare"
    broker_name = None
    for heading in soup.find_all(["h2", "h3"]):
        if "Ansvarig mäklare" in heading.get_text():
            # e.g. next sibling might contain name + company
            broker_section = heading.find_next()
            if broker_section:
                broker_name = broker_section.get_text(" ", strip=True)
            break

    # "Läs mer hos mäklaren" link:
    broker_link = soup.find("a", string=lambda s: s and "Läs mer hos mäklaren" in s)
    broker_website_url = broker_link["href"] if broker_link else None

    return ListingDetail(
        **summary.__dict__,
        broker_name=broker_name,
        broker_company=None,   # refine later
        broker_phone=None,
        broker_email=None,
        broker_website_url=broker_website_url,
        days_on_booli=days_on_booli,
        booli_views=None,
        drift_cost_sek=None,
        floor_of=None,
    )
