# real_estate/controllers.py

from typing import List

from .config import (
    SEARCH_URL,
    MAX_PRICE_SEK,
    MIN_LIVING_AREA_M2,
    MAX_MONTHLY_FEE_SEK,
)
from .models import ListingDetail, ListingSummary
from .scraper_list import parse_list_page
from .scraper_detail import enrich_with_detail
from .storage import save_listings, load_seen_ids, save_seen_ids


def is_interesting(summary: ListingSummary) -> bool:
    if summary.price_sek and summary.price_sek > MAX_PRICE_SEK:
        return False
    if summary.living_area_m2 and summary.living_area_m2 < MIN_LIVING_AREA_M2:
        return False
    if (
        summary.monthly_fee_sek is not None
        and summary.monthly_fee_sek > MAX_MONTHLY_FEE_SEK
    ):
        return False
    return True


def get_interesting_apartments() -> List[ListingDetail]:
    summaries = parse_list_page(SEARCH_URL)
    filtered = [s for s in summaries if is_interesting(s)]
    details: List[ListingDetail] = [enrich_with_detail(s) for s in filtered]

    # persist for later use
    save_listings(details)

    # also update seen IDs
    previous_seen = load_seen_ids()
    all_ids = previous_seen.union({d.booli_id for d in details})
    save_seen_ids(all_ids)

    return details

