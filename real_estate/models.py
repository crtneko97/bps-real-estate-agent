# real_estate/models.py

from dataclasses import dataclass
from typing import Optional, List



@dataclass
class ListingSummary:
    booli_id: int
    url: str
    address: str
    area: str
    city: str
    price_sek: int

    living_area_m2: Optional[float] = None
    rooms: Optional[float] = None
    monthly_fee_sek: Optional[int] = None
    floor_text: Optional[str] = None
    status_text: Optional[str] = None

    # 👇 these three are what scraper_list.py is still passing in
    has_elevator: Optional[bool] = None
    has_balcony: Optional[bool] = None
    has_outdoor_space: Optional[bool] = None

@dataclass
class Viewing:
    raw_text: str


@dataclass
class ListingDetail:
    booli_id: int
    url: str
    address: str
    area: str
    city: str
    price_sek: int

    living_area_m2: Optional[float] = None
    rooms: Optional[float] = None
    floor_text: Optional[str] = None
    monthly_fee_sek: Optional[int] = None

    has_elevator: Optional[bool] = None
    has_balcony: Optional[bool] = None
    has_outdoor_space: Optional[bool] = None
    status_text: Optional[str] = None

    drift_cost_sek: Optional[int] = None
    floor_of: Optional[str] = None
    booli_views: Optional[int] = None
    days_on_booli: Optional[int] = None
    ownership_type: Optional[str] = None
    building_year: Optional[int] = None

    broker_name: Optional[str] = None
    broker_company: Optional[str] = None
    broker_website_url: Optional[str] = None
    broker_email: Optional[str] = None
    broker_phone: Optional[str] = None

    viewings: Optional[List[Viewing]] = None

