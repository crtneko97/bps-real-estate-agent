# real_estate/config.py

SEARCH_URL = (
    "https://www.booli.se/sok/till-salu"
    "?areaIds=8521,874691,4120,1693,115341,95,115347,115353,115349,401672,6558,874661"
    "&objectType=L%C3%A4genhet"
    "&maxRooms=2"
    "&minRooms=1"
    "&maxLivingArea=40"
    "&maxListPrice=2000000"
)

# Basic filters you care about (you can tweak later)
MAX_PRICE_SEK = 2_000_000
MIN_LIVING_AREA_M2 = 20.0
MAX_MONTHLY_FEE_SEK = 3_500  # example

# HTTP config
USER_AGENT = (
    "bps-real-estate-looker/0.1 (personal use; contact: your-email@example.com)"
)

REQUEST_TIMEOUT = 10

