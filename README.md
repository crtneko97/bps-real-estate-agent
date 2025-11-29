# Real Estate Looker (Booli Weekend Project)

> BPS CR 2025-11-29 — MVP / dumpster / weekend project.

This is a small personal tool that watches apartments on [Booli.se](https://www.booli.se/) for me
based on a pre-filtered search URL, and exposes the results to my personal website.

It is **not** a generic “real estate API” and is only meant for my own use.

---

## Purpose

I want to:

- Hunt for 1–2 room apartments around Stockholm in specific areas.
- Apply my own filters (price, area, fee, etc.) on top of Booli's search UI.
- Eventually auto-generate “I’m interested” emails to the responsible broker using AI, similar
  to how my job-application helper works.

Example search URL I’m using right now:

```text
https://www.booli.se/sok/till-salu?areaIds=8521,874691,4120,1693,115341,95,115347,115353,115349,401672,6558,874661&objectType=L%C3%A4genhet&maxRooms=2&minRooms=1&maxLivingArea=40&maxListPrice=2000000

