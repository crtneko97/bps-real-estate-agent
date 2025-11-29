# real_estate/scraper_list.py

import re
from urllib.parse import urljoin
from typing import List

from bs4 import BeautifulSoup

from .http_client import fetch_soup
from .models import ListingSummary


PRICE_RE = re.compile(r"(\d[\d\s]*)\s*kr")
AREA_RE = re.compile(r"(\d+(?:,\d+)?)")
ROOMS_RE = re.compile(r"(\d+(?:,\d+)?)")
BOOLI_ID_RE = re.compile(r"/annons/(\d+)")
STATUS_RE = re.compile(r"(dagar på Booli|Inkommet idag|Inkommet igår|Snart till salu)")


def parse_price(text: str) -> int:
    """
    '1 995 000 kr' -> 1995000
    """
    m = PRICE_RE.search(text)
    if not m:
        return 0
    digits = re.sub(r"[^\d]", "", m.group(1))
    return int(digits) if digits else 0


def parse_m2(text: str) -> float:
    """
    '26 m²' or '33,5 m²' -> 26.0 / 33.5
    """
    m = AREA_RE.search(text)
    if not m:
        return 0.0
    return float(m.group(1).replace(",", "."))


def parse_rooms(text: str) -> float:
    """
    '1 rum' or '1,5 rum' -> 1.0 / 1.5
    """
    m = ROOMS_RE.search(text)
    if not m:
        return 0.0
    return float(m.group(1).replace(",", "."))


def parse_list_page(search_url: str) -> List[ListingSummary]:
    """
    Parse the Booli search page and return a list of ListingSummary objects.
    Uses the card container + sub-elements instead of h3.next_siblings.
    """
    soup = fetch_soup(search_url)
    results: List[ListingSummary] = []

    # Each listing card has this content container (from your screenshots).
    # We anchor on that as "one listing".
    cards = soup.select("div.object-card-layout__content")

    for card in cards:
        # --- Address + URL ---
        header_link = card.select_one("h3 a[href*='/annons/']")
        if not header_link:
            continue

        address = header_link.get_text(strip=True)
        url = urljoin(search_url, header_link["href"])

        # Booli ID from /annons/<id>
        id_match = BOOLI_ID_RE.search(url)
        booli_id = int(id_match.group(1)) if id_match else 0

        # --- Area + city ---
        # Example text: "Lägenhet · Aspudden · Stockholm"
        area = ""
        city = ""
        preamble = card.select_one("span.object-card__preamble")
        if preamble:
            parts = [p.strip() for p in preamble.get_text(strip=True).split("·")]
            if len(parts) >= 3:
                area = parts[1]
                city = parts[2]

        # --- Price ---
        price_sek = 0
        price_div = card.select_one("div.object-card__price-container")
        if price_div:
            price_sek = parse_price(price_div.get_text(" ", strip=True))

        # --- Data list: m², rum, vån, avgift ---
        # From your screenshot this is:
        # <ul class="object-card__data-list">
        #   <li>26 m²</li>
        #   <li>1 rum</li>
        #   <li>vån 2</li>
        #   <li>2 024 kr/mån</li>
        # </ul>
        living_area_m2 = 0.0
        rooms = 0.0
        floor_text = ""
        monthly_fee_sek = None

        data_items = card.select("ul.object-card__data-list li")
        if len(data_items) >= 1:
            living_area_m2 = parse_m2(data_items[0].get_text(" ", strip=True))
        if len(data_items) >= 2:
            rooms = parse_rooms(data_items[1].get_text(" ", strip=True))
        if len(data_items) >= 3:
            floor_text = data_items[2].get_text(" ", strip=True)
        if len(data_items) >= 4:
            monthly_fee_sek = parse_price(data_items[3].get_text(" ", strip=True))

        # --- Status text (days on Booli / incoming / soon) ---
        full_text = card.get_text(" ", strip=True)
        status_match = STATUS_RE.search(full_text)
        status_text = status_match.group(0) if status_match else ""

        # --- Flags: Hiss / Balkong / Uteplats ---
        has_elevator = "Hiss" in full_text
        has_balcony = "Balkong" in full_text
        has_outdoor_space = "Uteplats" in full_text

        summary = ListingSummary(
            booli_id=booli_id,
            url=url,
            address=address,
            area=area,
            city=city,
            price_sek=price_sek,
            living_area_m2=living_area_m2,
            rooms=rooms,
            floor_text=floor_text,
            monthly_fee_sek=monthly_fee_sek,
            has_elevator=has_elevator,
            has_balcony=has_balcony,
            has_outdoor_space=has_outdoor_space,
            status_text=status_text,
        )
        results.append(summary)

    return results

