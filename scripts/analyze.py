"""
Procurement analysis — runs SQL against the CSV loaded into SQLite
and produces:
  - out/findings.json   (numbers the HTML page reads)
  - out/chart_*.png     (static charts embedded in the page)

Every analysis question mirrors a line in the Visa BA job description:
  - Extract data from multiple sources (CSV -> SQL)
  - Normalize data (clean + aggregate)
  - Identify expense reduction opportunities
  - Validate demand against strategy (utilization analysis)
  - Create infrastructure baseline (asset counts + spend)
  - Cost clarity + key metrics (KPIs)
"""
from __future__ import annotations
import json
import sqlite3
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent.parent
CSV = ROOT / "data" / "procurement.csv"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

TODAY = date(2026, 4, 16)

# ---------- Load into SQLite ----------
df = pd.read_csv(CSV, parse_dates=["purchase_date", "renewal_date"])
conn = sqlite3.connect(":memory:")
df.to_sql("po", conn, index=False)

def q(sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)

findings: dict = {}

# ---------- KPIs ----------
kpi = q("""
    SELECT
      COUNT(*)                                       AS po_count,
      ROUND(SUM(total_spend_usd), 2)                 AS total_spend,
      ROUND(AVG(total_spend_usd), 2)                 AS avg_po,
      COUNT(DISTINCT vendor)                         AS vendor_count,
      COUNT(DISTINCT business_unit)                  AS bu_count
    FROM po
""").iloc[0].to_dict()
findings["kpis"] = kpi

# ---------- Spend by category ----------
by_cat = q("""
    SELECT category,
           ROUND(SUM(total_spend_usd), 2) AS spend,
           COUNT(*)                       AS pos
    FROM po
    GROUP BY category
    ORDER BY spend DESC
""")
findings["by_category"] = by_cat.to_dict(orient="records")

plt.figure(figsize=(9, 4.5))
plt.barh(by_cat["category"], by_cat["spend"] / 1e6, color="#1a1f71")
plt.xlabel("Spend ($M)")
plt.title("Total Spend by Category")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(OUT / "chart_category.png", dpi=120)
plt.close()

# ---------- Top vendors ----------
top_vendors = q("""
    SELECT vendor,
           ROUND(SUM(total_spend_usd), 2) AS spend,
           COUNT(*)                       AS pos
    FROM po
    GROUP BY vendor
    ORDER BY spend DESC
    LIMIT 10
""")
findings["top_vendors"] = top_vendors.to_dict(orient="records")

plt.figure(figsize=(9, 4.5))
plt.barh(top_vendors["vendor"], top_vendors["spend"] / 1e6, color="#f7b600")
plt.xlabel("Spend ($M)")
plt.title("Top 10 Vendors by Spend")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(OUT / "chart_vendors.png", dpi=120)
plt.close()

# ---------- Spend by business unit ----------
by_bu = q("""
    SELECT business_unit,
           ROUND(SUM(total_spend_usd), 2) AS spend
    FROM po
    GROUP BY business_unit
    ORDER BY spend DESC
""")
findings["by_business_unit"] = by_bu.to_dict(orient="records")

plt.figure(figsize=(9, 4.5))
plt.bar(by_bu["business_unit"], by_bu["spend"] / 1e6, color="#1a1f71")
plt.ylabel("Spend ($M)")
plt.title("Spend by Business Unit")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(OUT / "chart_bu.png", dpi=120)
plt.close()

# ---------- Renewals in next 90 days (the money question) ----------
renewals_90 = q(f"""
    SELECT vendor, category, business_unit, total_spend_usd, renewal_date
    FROM po
    WHERE status IN ('Active', 'Pending Renewal')
      AND julianday(renewal_date) - julianday('{TODAY.isoformat()}') BETWEEN 0 AND 90
    ORDER BY renewal_date ASC
""")
findings["renewals_90d"] = {
    "count": int(len(renewals_90)),
    "total_value": float(round(renewals_90["total_spend_usd"].sum(), 2)),
    "rows": renewals_90.head(10).to_dict(orient="records"),
}

# ---------- Underutilized assets (optimization opportunity) ----------
underutil = q("""
    SELECT vendor, category, business_unit, total_spend_usd, utilization_pct
    FROM po
    WHERE status = 'Active'
      AND utilization_pct < 40
    ORDER BY total_spend_usd DESC
""")
findings["underutilized"] = {
    "count": int(len(underutil)),
    "reclaimable_spend": float(round(underutil["total_spend_usd"].sum(), 2)),
    "rows": underutil.head(10).to_dict(orient="records"),
}

# ---------- Vendor consolidation opportunity ----------
# Categories where 3+ vendors are used in the same BU
consolidation = q("""
    SELECT business_unit, category,
           COUNT(DISTINCT vendor)        AS vendors,
           ROUND(SUM(total_spend_usd),2) AS spend
    FROM po
    WHERE status IN ('Active','Pending Renewal')
    GROUP BY business_unit, category
    HAVING vendors >= 3
    ORDER BY spend DESC
    LIMIT 10
""")
findings["consolidation"] = consolidation.to_dict(orient="records")

# ---------- Save findings ----------
# pandas Timestamps / numpy types -> plain Python
def _clean(obj):
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    return obj

(OUT / "findings.json").write_text(json.dumps(_clean(findings), indent=2, default=str))

print("== KPIs ==")
for k, v in kpi.items():
    print(f"  {k}: {v}")
print(f"\nRenewals in next 90 days: {findings['renewals_90d']['count']} "
      f"worth ${findings['renewals_90d']['total_value']:,.0f}")
print(f"Underutilized active assets: {findings['underutilized']['count']} "
      f"tying up ${findings['underutilized']['reclaimable_spend']:,.0f}")
print(f"Consolidation candidates (BU x category with 3+ vendors): {len(consolidation)}")
print(f"\nWrote {OUT/'findings.json'} and 3 charts to {OUT}")
