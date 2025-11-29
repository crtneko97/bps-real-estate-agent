# real_estate/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ListingSummary:
    booli_id: int
    url: str
    address: str
    area: str
    city: str
    price_sek: int
    living_area_m2: float
    rooms: float
    floor_text: str
    monthly_fee_sek: Optional[int]
    has_elevator: bool
    has_balcony: bool
    has_outdoor_space: bool
    status_text: str  # "8 dagar på Booli", "Inkommet igår", etc.

@dataclass
class ListingDetail(ListingSummary):
    drift_cost_sek: Optional[int] = None
    floor_of: Optional[str] = None  # "2 av 3"
    days_on_booli: Optional[int] = None
    booli_views: Optional[int] = None
    ownership_type: Optional[str] = None  # "bostadsrätt"
    building_year: Optional[int] = None
    broker_name: Optional[str] = None
    broker_company: Optional[str] = None
    broker_website_url: Optional[str] = None

