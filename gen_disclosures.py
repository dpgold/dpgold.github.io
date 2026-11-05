"""Regenerate data/disclosures.json from DirDash's disclosures file.  Run:  py gen_disclosures.py

Mirrors DirDash "Generate Summary" with the All-time window: every row regardless of
expiration, grouped by support type, sponsors de-duplicated and sorted.
"""
import datetime, json, pathlib

SRC = pathlib.Path.home() / "OneDrive - University of Southern California/Schaeffer Inst Dir Office/DATA/DirDash/Disclosures/disclosures-data.json"
OUT = pathlib.Path(__file__).parent / "data" / "disclosures.json"

# Sponsors to leave off the public site (type, sponsor).
EXCLUDE = {
    ("Equity", "Precision Medicine Group"),   # no longer held (Dana, 2026-11-05)
}

ORDER = ["Research Grant", "Travel", "Personal Fees", "Equity"]
LABELS = {"Research Grant": "Research grants", "Travel": "Travel", "Personal Fees": "Personal fees", "Equity": "Equity"}

rows = json.loads(SRC.read_text(encoding="utf-8"))["rows"]
by, last_end = {}, {}
for r in rows:
    t = r.get("support") or "Research Grant"
    s = (r.get("sponsor") or "").strip()
    if s and (t, s) not in EXCLUDE:
        by.setdefault(t, []).append(s)
        if r.get("expiration"):
            last_end[t] = max(last_end.get(t, ""), r["expiration"])
        else:
            last_end[t] = "ongoing"

groups = []
for t in ORDER + [k for k in by if k not in ORDER]:
    seen, out = set(), []
    for s in by.get(t, []):
        if s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    if out:
        groups.append({"label": LABELS.get(t, t), "sponsors": sorted(out, key=str.lower), "last_end": last_end.get(t, "")})

OUT.write_text(json.dumps({"source": "DirDash disclosures, all time", "generated": datetime.date.today().isoformat(),
                           "groups": groups}, ensure_ascii=False, indent=1), encoding="utf-8")
for g in groups:
    print(f'{g["label"]} ({len(g["sponsors"])})')
