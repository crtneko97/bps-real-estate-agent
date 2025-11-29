# real_estate/storage.py

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List, Set

from .models import ListingDetail

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

LISTINGS_PATH = DATA_DIR / "latest_listings.json"
SEEN_IDS_PATH = DATA_DIR / "seen_ids.json"


def save_listings(listings: Iterable[ListingDetail]) -> None:
    """
    Save all current listings to JSON.
    """
    data = [asdict(l) for l in listings]
    with LISTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_listings() -> List[ListingDetail]:
    """
    Load listings from JSON (if the file exists).
    """
    if not LISTINGS_PATH.exists():
        return []

    from .models import ListingDetail  # avoid circular imports at top

    with LISTINGS_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    listings: List[ListingDetail] = []
    for item in raw:
        listings.append(ListingDetail(**item))
    return listings


def load_seen_ids() -> Set[int]:
    """
    Load set of booli_id that we've seen before.
    """
    if not SEEN_IDS_PATH.exists():
        return set()

    with SEEN_IDS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return set(int(x) for x in data)


def save_seen_ids(ids: Iterable[int]) -> None:
    """
    Save set of booli_id we've seen.
    """
    unique_ids = sorted(set(int(x) for x in ids))
    with SEEN_IDS_PATH.open("w", encoding="utf-8") as f:
        json.dump(unique_ids, f, ensure_ascii=False, indent=2)
