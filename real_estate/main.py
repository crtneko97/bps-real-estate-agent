# real_estate/main.py

from .controllers import get_interesting_apartments
from .storage import load_seen_ids


def main():
    before = load_seen_ids()  # IDs from previous runs
    apartments = get_interesting_apartments()

    print(f"Found {len(apartments)} interesting apartments:\n")

    for a in apartments:
        is_new = a.booli_id not in before
        marker = "NEW" if is_new else "OLD"
        print(
            f"[{marker}] {a.address} ({a.area}, {a.city}) "
            f"{a.living_area_m2} m², {a.rooms} rum, "
            f"pris {a.price_sek} kr, avgift {a.monthly_fee_sek} kr/mån, "
            f"vån {a.floor_text} | url: {a.url}"
        )


if __name__ == "__main__":
    main()

