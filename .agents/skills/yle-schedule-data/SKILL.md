---
name: yle-schedule-data
description: Diagnose missing programmes in this guide by tracing the schedule files published by yle-guide-scraper.
---

# Yle schedule data

Verified 2026-11-14:

- Required layout (Antti, 2026-11-14): Radio 1 schedules belong under
  `yle/yle-radio-1/YYYY/MM/DD.yaml`. Retaining the channel directory allows other
  channels to be added later.
- The [scraper repository](https://github.com/akaihola/yle-guide-scraper) owns API
  compatibility and corrections to its data history. This guide consumes the
  stable channel-specific layout; do not add fallbacks for misplaced data or
  depend on scraper commit hashes that a history rewrite would invalidate.
- A successful fetch or deployment does not prove that usable programmes exist.
  The [analyzer](../../../schedule_analyzer.py) must exit unsuccessfully when no
  files or no recurring programmes are found. This stops the Pages workflow
  before an empty guide replaces the published site.
- Future file names alone do not establish fresh broadcast data. Inspect actual
  programme start times and the generated guide, not just file or row counts.
- HTML generation copies static assets into the working directory. Run trial
  builds from a temporary directory to avoid changing repository assets.
