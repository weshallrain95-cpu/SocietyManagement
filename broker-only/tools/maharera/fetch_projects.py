"""Collect MahaRERA's public list of registered projects for one district (default: Thane, 517).

Reads only the public search-result list (no login, no CAPTCHA): RERA number, project name, promoter,
location text, pincode, map pin when given, last modified, and the public details link. The details
pages sit behind a CAPTCHA and are NOT read by this tool.

Polite by design: one page at a time with a pause between pages; resumes where it stopped.

    python3 fetch_projects.py --district 517 --out thane_projects.csv
"""

import argparse
import csv
import html
import os
import re
import sys
import time
import urllib.request

BASE = "https://maharera.maharashtra.gov.in/projects-search-result"
UA = "Mozilla/5.0 (OnlyBroker data research; contact: founder)"
FIELDS = ["rera_no", "project_name", "promoter", "location", "pincode", "district", "state", "lat", "lng", "last_modified", "details_url"]


def fetch(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001
            wait = 5 * (i + 1)
            print(f"  retry in {wait}s after {e}", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"gave up on {url}")


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s or "")).strip()


def parse(page):
    out = []
    for card in re.split(r'<div class="row shadow p-3 mb-5 bg-body rounded">', page)[1:]:
        rera = re.search(r"#\s*(P\d{8,14})", card)
        if not rera:
            continue
        name = re.search(r'<h4 class="title4"><strong>(.*?)</strong>', card, re.S)
        prom = re.search(r'<p class="darkBlue bold ">(.*?)</p>', card, re.S)
        loc = re.search(r'fa-location-dot"></em>(.*?)</a>', card, re.S)
        q = re.search(r"maps/search/\?api=1&amp;query=([-\d.]*),([-\d.]*)", card)

        def field(label):
            m = re.search(r'<div class="greyColor">' + label + r"</div>\s*<p>(.*?)</p>", card, re.S)
            return text(m.group(1)) if m else ""

        det = re.search(r'href="(https://maharerait\.maharashtra\.gov\.in/public/project/view/\d+)"', card)
        out.append(
            {
                "rera_no": rera.group(1),
                "project_name": text(name.group(1)) if name else "",
                "promoter": text(prom.group(1)) if prom else "",
                "location": text(loc.group(1)) if loc else "",
                "pincode": field("Pincode"),
                "district": field("District"),
                "state": field("State"),
                "lat": q.group(1) if q else "",
                "lng": q.group(2) if q else "",
                "last_modified": field("Last Modified"),
                "details_url": det.group(1) if det else "",
            }
        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--district", default="517")
    ap.add_argument("--out", default="thane_projects.csv")
    ap.add_argument("--pause", type=float, default=1.5)
    ap.add_argument("--max-pages", type=int, default=0)
    ap.add_argument("--start", type=int, default=0, help="first page (for running several collectors side by side)")
    ap.add_argument("--end", type=int, default=0, help="last page")
    a = ap.parse_args()

    seen, start = set(), 1
    if os.path.exists(a.out):
        with open(a.out, newline="") as f:
            rows = list(csv.DictReader(f))
        seen = {r["rera_no"] for r in rows}
        start = len(rows) // 10 + 1
    if a.start:
        start = max(start, a.start) if not os.path.exists(a.out) else a.start + len(seen) // 10
    first = fetch(f"{BASE}?project_name=&project_location=&project_state=27&project_district={a.district}&page=1")
    total = int(re.search(r'colorBlue">(\d+)</span> Result', first).group(1))
    pages = (total + 9) // 10
    if a.max_pages:
        pages = min(pages, a.max_pages)
    if a.end:
        pages = min(pages, a.end)
    print(f"{total} projects, {pages} pages; starting at page {start}", flush=True)
    new_file = not os.path.exists(a.out)
    with open(a.out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for p in range(start, pages + 1):
            page = first if p == 1 else fetch(f"{BASE}?project_name=&project_location=&project_state=27&project_district={a.district}&page={p}")
            got = [r for r in parse(page) if r["rera_no"] not in seen]
            for r in got:
                seen.add(r["rera_no"])
                w.writerow(r)
            f.flush()
            if p % 25 == 0 or p == pages:
                print(f"page {p}/{pages}: {len(seen)} projects so far", flush=True)
            time.sleep(a.pause)


if __name__ == "__main__":
    main()
