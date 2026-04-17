# IT Procurement Analytics — Enterprise Spend Analysis

> A data analytics project simulating enterprise IT procurement
> management: extract purchase-order data, normalize it with SQL,
> and surface cost-optimization opportunities for stakeholders.

**Live report:** [it-procurement-analytics.vercel.app](https://it-procurement-analytics.vercel.app)
**GitHub:** [github.com/EthanH2004/it-procurement-analytics](https://github.com/EthanH2004/it-procurement-analytics)
**Narrative findings:** [`FINDINGS.md`](FINDINGS.md)
**Technical design:** [`DESIGN.md`](DESIGN.md)

---

## Project Overview

This project analyzes a synthetic 1,000-row IT procurement portfolio
($4.92B spend, 25 vendors, 6 business units) end-to-end in SQL, with
findings rendered as a polished static report.

**The four questions this analysis answers** are the core questions
any IT spend analyst answers on a regular basis:

1. **What do we own and what does it cost?** (portfolio baseline)
2. **What's renewing soon?** (the 90-day window — where auto-renewal
   waste gets caught)
3. **What are we paying for and not using?** (utilization reclaim)
4. **Where are we fragmented?** (vendor consolidation candidates)

---

## Headline Results

| Finding                           | Value              | Why it matters                              |
| --------------------------------- | ------------------ | ------------------------------------------- |
| Portfolio size                    | $4.92B / 1,000 POs | Context for every other number              |
| Software-license share            | 89% of spend       | Where optimization effort should concentrate |
| Renewals in next 90 days          | 45 worth **$310M** | Demand-validation checkpoint                 |
| Underutilized active assets       | 67, tying up **$274M** | Most defensible reclaim argument         |
| BU × category pairs with 3+ vendors | 10               | Consolidation targets                        |
| Total addressable opportunity     | ~$305M (~6% of portfolio) | Inside industry-typical 3–8% band   |

---

## How It Works (30-second tour)

```
generate_data.py  →  data/procurement.csv  (1,000 rows, seeded)
      │
      ▼
 analyze.py       →  SQL on SQLite          →  out/findings.json
                                                out/chart_*.png
      │
      ▼
 build_page.py    →  out/index.html  (self-contained static report)
```

Three scripts, ~300 lines total. Every number on the final page
traces back to a specific SQL query that can be re-run.

---

## Run It Yourself

```bash
pip install pandas matplotlib
python scripts/generate_data.py   # ~1s → data/procurement.csv
python scripts/analyze.py         # ~2s → findings.json + 3 charts
python scripts/build_page.py      # <1s → out/index.html

# open the report
python -m http.server 8765 --directory out
# visit http://localhost:8765
```

Runtime: ~4 seconds end-to-end on a stock laptop. No database server,
no cloud account, no BI tool.

---

## Skills Demonstrated

| Area | Implementation |
| ---- | -------------- |
| SQL querying & normalization | `scripts/analyze.py` — 7 SQL queries against SQLite |
| Expense-reduction analysis | FINDINGS §5–§7 — renewals, reclaim, consolidation |
| Data pipeline design | CSV → SQLite → JSON → static HTML |
| Visualization | Matplotlib charts; CSV drops into Excel / Power BI 1:1 |
| Reproducibility | Fixed random seed — byte-identical outputs every run |
| Technical communication | Each finding paired with a plain-English recommendation |

---

## What's in This Repo

```
README.md           ← you are here
FINDINGS.md         ← narrative findings + recommendations
DESIGN.md           ← architecture and design decisions
data/
  procurement.csv   ← the 1,000-row dataset (seeded, reproducible)
scripts/
  generate_data.py  ← CSV generator
  analyze.py        ← SQL + chart generation
  build_page.py     ← HTML renderer
out/
  index.html        ← the final static report (open in browser)
  findings.json     ← structured numeric results
  chart_*.png       ← category / vendors / BU charts
```

---

## About the Data

The dataset is a 1,000-row synthetic CSV generated with a fixed random
seed, documented in [`DESIGN.md §3.1`](DESIGN.md). Real enterprise
procurement data is confidential, so the schema was modeled on what's
commonly present in ServiceNow ITAM and SAP Ariba exports.
Category-specific price and quantity ranges were enforced so the
aggregates are realistic. Absolute dollars aren't a benchmark;
the value is in the method.

---

## About

**Ethan Hennenhoefer** · Austin, TX · [Ethan@Hennenhoefer.org](mailto:Ethan@Hennenhoefer.org)  
B.S. Information Technology, Texas Tech University (May 2026)  
Rawls College of Business — coursework spans database systems,
data analytics, and the business core (accounting, finance, management).
