# real_estate/scraper_detail.py

import re
from typing import Optional

from bs4 import BeautifulSoup

from .http_client import fetch_soup
from .models import ListingSummary, ListingDetail, Viewing

# --- Regexes ---

INT_RE = re.compile(r"[^\d]")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b0\d[\d\s-]{7,}\d\b")  # rough Swedish mobile/landline pattern

# Example target text after get_text(" ", strip=True):
# "7 dec Öppen visning, föranmäl dig gärna 13:30 – 14:00 ..."
VIEWING_RE = re.compile(
    r"(\d{1,2}\s+\w{3}.*?\d{2}:\d{2}\s*[–-]\s*\d{2}:\d{2}.*?visning)",
    re.IGNORECASE,
)


# --- Helpers ---

def _int_from_text(text: str) -> Optional[int]:
    digits = INT_RE.sub("", text)
    return int(digits) if digits else None


def _parse_viewings_from_booli(text: str) -> list[Viewing]:
    """
    Try to pull out 'visningar' such as:
      7 dec Öppen visning, föranmäl dig gärna 13:30 – 14:00
    For now we keep them as raw strings on Viewing.raw_text.
    """
    viewings: list[Viewing] = []
    for m in VIEWING_RE.finditer(text):
        viewings.append(Viewing(raw_text=m.group(1).strip()))
    return viewings


def _fetch_broker_from_svenskfast(
    url: str,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Go to Svensk Fastighetsförmedling object page and grab:
      - broker_name
      - broker_phone
      - broker_email
    """
    try:
        soup = fetch_soup(url)
    except Exception:
        return None, None, None

    text = soup.get_text("\n", strip=True)

    broker_name: Optional[str] = None
    broker_phone: Optional[str] = None
    broker_email: Optional[str] = None

    # Name is usually just after "Ansvarig mäklare"
    # "Ansvarig mäklare\nAnders Ångström\nFastighetsmäklare\n..."
    name_match = re.search(
        r"Ansvarig mäklare\s+([^\n]+)\s+Fastighetsmäklare", text
    )
    if name_match:
        broker_name = name_match.group(1).strip()

    # First phone number on the page
    phone_match = PHONE_RE.search(text)
    if phone_match:
        broker_phone = re.sub(r"\s+", " ", phone_match.group(0)).strip()

    # First email on the page
    email_match = EMAIL_RE.search(text)
    if email_match:
        broker_email = email_match.group(0).strip()

    return broker_name, broker_phone, broker_email


# --- Main enrichment ---

def enrich_with_detail(summary: ListingSummary) -> ListingDetail:
    """
    Take a ListingSummary from the Booli list page and enrich it with:
      - drift cost, days on Booli, views, ownership type, building year
      - viewings (visningar) parsed from the Booli text
      - broker info fetched via 'Läs mer hos mäklaren' → Svenskfast page
    """
    soup = fetch_soup(summary.url)
    text = soup.get_text(" ", strip=True)

    # --- Booli text-based details ---

    drift_cost: Optional[int] = None
    m = re.search(r"Driftskostnaden är\s+([\d\s]+)\s*kr/mån", text)
    if m:
        drift_cost = _int_from_text(m.group(1))

    floor_of: Optional[str] = None
    m = re.search(r"Den ligger på våning\s+(\d+\s+av\s+\d+)", text)
    if m:
        floor_of = m.group(1).strip()

    days_on_booli: Optional[int] = None
    m = re.search(r"varit till salu i\s+(\d+)\s+dagar", text)
    if m:
        days_on_booli = int(m.group(1))

    views: Optional[int] = None
    m = re.search(r"har\s+([\d\s]+)\s+sidvisningar på Booli", text)
    if m:
        views = _int_from_text(m.group(1))

    ownership_type: Optional[str] = None
    m = re.search(r"Den här lägenheten är en\s+([^.]+)\.", text)
    if m:
        ownership_type = m.group(1).strip()

    building_year: Optional[int] = None
    m = re.search(r"Byggår\s+(\d{4})", text)
    if m:
        building_year = int(m.group(1))

    # --- Visningar (viewings / open house) from Booli text ---

    viewings = _parse_viewings_from_booli(text)

    # --- Broker info via Booli + external page ---

    broker_name: Optional[str] = None
    broker_company: Optional[str] = None
    broker_email: Optional[str] = None
    broker_phone: Optional[str] = None
    broker_website_url: Optional[str] = None

    # 1) Find "Läs mer hos mäklaren" link on Booli listing page
    for a in soup.find_all("a", href=True):
        link_text = a.get_text(" ", strip=True)
        if "Läs mer hos mäklaren" in link_text:
            broker_website_url = a["href"]
            break

    # 2) If it's Svenskfast, fetch broker info there
    if broker_website_url and "svenskfast.se" in broker_website_url:
        b_name, b_phone, b_email = _fetch_broker_from_svenskfast(broker_website_url)
        if b_name:
            broker_name = b_name
        if b_phone:
            broker_phone = b_phone
        if b_email:
            broker_email = b_email
        broker_company = "Svensk Fastighetsförmedling"

    # --- Build final ListingDetail ---

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
        broker_email=broker_email,
        broker_phone=broker_phone,
        broker_website_url=broker_website_url,
        viewings=viewings,
    )

