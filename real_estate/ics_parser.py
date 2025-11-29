# real_estate/ics_parser.py

from datetime import datetime
from typing import Dict

def parse_single_ics_event(text: str) -> Dict[str, str]:
    """
    Very simple parser for a single VEVENT .ics text.
    Returns {start, end, description, url, location}.
    Times are returned as ISO strings.
    """
    data: Dict[str, str] = {}

    def get_line(name: str) -> str:
        for line in text.splitlines():
            if line.startswith(name + ":"):
                return line.split(":", 1)[1].strip()
        return ""

    dtstart = get_line("DTSTART")
    dtend = get_line("DTEND")
    desc = get_line("DESCRIPTION")
    url = get_line("URL")
    location = get_line("LOCATION")

    def parse_utc(dt_raw: str) -> str:
        # Example: 20251207T123000Z -> ISO
        try:
            dt = datetime.strptime(dt_raw, "%Y%m%dT%H%M%SZ")
            return dt.isoformat() + "Z"
        except Exception:
            return dt_raw

    if dtstart:
        data["start"] = parse_utc(dtstart)
    if dtend:
        data["end"] = parse_utc(dtend)
    if desc:
        data["description"] = desc
    if url:
        data["url"] = url
    if location:
        data["location"] = location

    return data
