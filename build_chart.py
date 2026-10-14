"""
build_chart.py: builds chart.html, a summary chart page, from claims.json,
sources.json and REPORT.md.

Only claims that REPORT.md marks "verified" are drawn. Held claims are listed
separately with their reason. Run `python3 verify.py` first so REPORT.md is
current, then `python3 build_chart.py`.

Plain Python, standard library only. No AI calls.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# Which claims feed which panel. Change these lists as claims are added.
PANELS = {
    # year -> claim ids, one bar per source
    "volume": ["c4", "c5", "c17", "c8", "c7"],
    "investors": ["c1", "c2", "c3"],
    "caprates": ["c6", "c10", "c11"],
    "named": ["c15", "c12", "c16"],
    "fundamentals": ["c13", "c14", "c9"],
}


def report_status():
    """claim_id -> (status, reason), read from REPORT.md's table."""
    status = {}
    for line in (HERE / "REPORT.md").read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 8 and cells[0].startswith("c") and cells[0][1:].isdigit():
            status[cells[0]] = (cells[6].replace("*", ""), cells[7])
    return status


def main():
    claims = json.loads((HERE / "claims.json").read_text())
    sources = {s["id"]: s for s in json.loads((HERE / "sources.json").read_text())}
    status = report_status()
    rows = []
    for c in claims:
        st, reason = status.get(c["claim_id"], ("held", "not in REPORT.md; run verify.py"))
        src = sources.get(c["source_id"], {})
        rows.append({
            "id": c["claim_id"], "subject": c["subject"], "value": c["value"],
            "unit": c["unit"], "period": c["period"], "quote": c["quote"],
            "source": src.get("title", c["source_id"]), "url": src.get("url", ""),
            "status": st, "reason": reason,
        })
    data = json.dumps({"claims": rows, "panels": PANELS}, ensure_ascii=False)
    data = data.replace("</", "<\\/")
    template = (HERE / "chart_template.html").read_text()
    (HERE / "chart.html").write_text(template.replace("/*__DATA__*/null", data))
    verified = sum(r["status"] == "verified" for r in rows)
    print(f"Wrote chart.html: {verified} verified claims drawn, {len(rows) - verified} held listed separately.")


if __name__ == "__main__":
    main()
