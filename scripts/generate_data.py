"""
Generate a realistic IT hardware & software procurement dataset for a demo
mirroring a Visa-style Demand Management use case.

Schema is modeled on real enterprise IT asset / procurement records:
PO line items with vendor, category, business unit, purchase + renewal
dates, spend, utilization, and status.

Run: python scripts/generate_data.py
Outputs: data/procurement.csv
"""
from __future__ import annotations
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUT = Path(__file__).parent.parent / "data" / "procurement.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

VENDORS = {
    "Server Hardware": ["Dell", "HPE", "Lenovo", "Supermicro"],
    "Network Hardware": ["Cisco", "Arista", "Juniper", "Palo Alto"],
    "Storage": ["NetApp", "Pure Storage", "Dell EMC"],
    "Laptops": ["Dell", "Lenovo", "Apple", "HP"],
    "Software License": ["Microsoft", "Oracle", "Splunk", "Datadog", "ServiceNow", "Salesforce"],
    "Cloud Services": ["AWS", "Azure", "GCP"],
    "Security": ["CrowdStrike", "Palo Alto", "Okta", "Zscaler"],
}

BUSINESS_UNITS = [
    "Core Payments",
    "Fraud & Risk",
    "Merchant Services",
    "Data Platform",
    "Corporate IT",
    "Consumer Products",
]

STATUSES = ["Active", "Active", "Active", "Active", "Pending Renewal", "Retired", "In Procurement"]

# Rough unit price ranges by category (USD)
PRICE_RANGES = {
    "Server Hardware": (8_000, 45_000),
    "Network Hardware": (5_000, 120_000),
    "Storage": (15_000, 250_000),
    "Laptops": (1_200, 3_800),
    "Software License": (500, 250_000),
    "Cloud Services": (10_000, 800_000),
    "Security": (5_000, 180_000),
}

QTY_RANGES = {
    "Server Hardware": (1, 25),
    "Network Hardware": (1, 12),
    "Storage": (1, 5),
    "Laptops": (10, 300),
    "Software License": (1, 500),
    "Cloud Services": (1, 1),
    "Security": (1, 50),
}

TERMS = [12, 24, 36]  # months

def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

ROWS = 1000
start = date(2023, 1, 1)
end = date(2026, 3, 31)

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "po_id",
        "purchase_date",
        "vendor",
        "category",
        "business_unit",
        "item_description",
        "quantity",
        "unit_price_usd",
        "total_spend_usd",
        "contract_term_months",
        "renewal_date",
        "utilization_pct",
        "status",
    ])

    for i in range(1, ROWS + 1):
        cat = random.choice(list(VENDORS.keys()))
        vendor = random.choice(VENDORS[cat])
        bu = random.choice(BUSINESS_UNITS)
        qty = random.randint(*QTY_RANGES[cat])
        unit = round(random.uniform(*PRICE_RANGES[cat]), 2)
        total = round(qty * unit, 2)
        pdate = rand_date(start, end)
        term = random.choice(TERMS) if cat in ("Software License", "Cloud Services", "Security") else random.choice([12, 36, 60])
        rdate = pdate + timedelta(days=term * 30)
        util = max(5, min(100, int(random.gauss(68, 22))))
        status = random.choice(STATUSES)
        # Heuristic: if renewal within 90 days of "today", mark Pending Renewal more often
        today = date(2026, 4, 16)
        if 0 <= (rdate - today).days <= 90 and status == "Active":
            if random.random() < 0.6:
                status = "Pending Renewal"
        desc = f"{vendor} {cat}"
        w.writerow([
            f"PO-{i:05d}",
            pdate.isoformat(),
            vendor,
            cat,
            bu,
            desc,
            qty,
            f"{unit:.2f}",
            f"{total:.2f}",
            term,
            rdate.isoformat(),
            util,
            status,
        ])

print(f"Wrote {ROWS} rows to {OUT}")
