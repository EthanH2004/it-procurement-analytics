# IT Procurement Demand Management — Portfolio Analysis

> A self-contained data project built for the **Visa Associate Business
> Analyst (New Grad 2026)** role. It simulates the day-to-day work of
> an IT Demand Management BA: extract procurement data, normalize it
> with SQL, and surface cost-optimization opportunities for product
> owners.

**Live report:** [visa-ba-portfolio.vercel.app](https://visa-ba-portfolio.vercel.app)
**GitHub:** [github.com/EthanH2004/visa-ba-portfolio](https://github.com/EthanH2004/visa-ba-portfolio)
**Narrative findings:** [`FINDINGS.md`](FINDINGS.md)
**Technical design:** [`DESIGN.md`](DESIGN.md)

---

## Why This Project

The Visa Associate BA job description asks for someone who can:

> *"Run SQL scripts to extract data from multiple data sources and
> normalize data based on product owner feedback."*
>
> *"Identify expense reduction opportunities with product owners and
> create plans and tracking to ensure execution."*
>
> *"Draw actionable insights from raw data using strong quantitative
> skills and be able to influence stakeholder leadership."*

Rather than tell an interviewer I can do this, I built the thing. This
project is a 1,000-row synthetic IT procurement portfolio
($4.92B spend, 25 vendors, 6 business units) analyzed end-to-end in SQL,
with the findings rendered as a polished static report.

**The four questions this report answers** are the exact questions a
Demand Management BA answers every week:

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
traces back to a specific SQL query an interviewer can re-run.

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

## What Skills This Demonstrates (Mapped to the JD)

| Visa JD Requirement | Where It Shows Up |
| ------------------- | ----------------- |
| SQL querying, normalization across sources | `scripts/analyze.py` — 7 SQL queries against SQLite |
| Identifying expense-reduction opportunities | FINDINGS §5–§7 (renewals, reclaim, consolidation) |
| Demand validation against strategy | 90-day renewal pipeline + utilization reclaim |
| Infrastructure asset baseline | Portfolio KPIs + category rollup |
| Cost clarity programs for leadership | BU showback section |
| Actionable insights from raw data | Each finding paired with a recommendation |
| Running IT like a business | Per-BU spend, per-category unit economics |
| Analytical tools (Excel / Tableau / Power BI-class) | Matplotlib charts; CSV drops into Excel / Power BI 1:1 |

---

## What's in This Repo

```
README.md           ← you are here — the pitch
FINDINGS.md         ← narrative findings + recommendations
DESIGN.md           ← architecture, data-science design choices, trade-offs
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

## Interview Q&A — Backup Answers

The three questions a hiring manager is most likely to ask about
this project:

### "Is the data real?"

No — it's a 1,000-row synthetic dataset generated with a fixed random
seed, documented in [`DESIGN.md §3.1`](DESIGN.md). Real enterprise
procurement data is confidential, so I modeled the schema on what's
commonly present in ServiceNow ITAM, SAP Ariba, and the public Kaggle
*Procurement KPI* dataset. Category-specific price and quantity ranges
were enforced so the aggregates are plausible. Absolute dollars aren't
a benchmark; the value is in the method.

### "Why SQLite and not just pandas?"

Two reasons.

1. **The queries are portable.** Every SQL statement in `analyze.py`
   will run unchanged against SQL Server, BigQuery, or Snowflake —
   which is what I'd use at Visa. Pandas code wouldn't transfer.
2. **It's auditable.** A reviewer can read the seven queries and
   reason about them directly. Chained pandas `groupby` calls are
   harder to review, harder to explain, and mix business logic with
   syntax.

Full rationale in [`DESIGN.md §3.2`](DESIGN.md).

### "What would you change if this were a real Visa project?"

Four things — covered in [`DESIGN.md §6`](DESIGN.md):

1. **Replace modeled utilization with real telemetry.** Pull from
   FlexNet / Sassafras for on-prem licenses, or Apptio / Flexera for
   cloud. That changes the reclaim list from "plausible" to
   "defensible in a product-owner meeting."
2. **Add vendor-name normalization.** "Microsoft", "MSFT Corp.",
   "Microsoft Corporation" all show up in real procurement exports.
   A fuzzy match + canonical dictionary is the first real task.
3. **Push queries to the warehouse.** At scale you don't pull raw
   rows client-side — you run the SQL where the data lives and pull
   aggregates.
4. **Institutionalize the report.** This is a one-shot today; in
   production it becomes a monthly scheduled refresh feeding a
   Power BI dashboard the Demand Management team owns.

---

## About

**Ethan Hennenhoefer** · Austin, TX · [Ethan@Hennenhoefer.org](mailto:Ethan@Hennenhoefer.org)
B.S. Information Technology, Texas Tech University (May 2026)

Prior IT experience: Software Engineering Intern (AI/ML) at SHI
International — built Azure Functions + ServiceNow integrations for an
enterprise service-desk AI assistant. AI Solutions Intern — built
AI-driven proposal automation (2-week → 2-day cycle-time reduction).

This project was built as preparation for the Visa Associate BA
interview and is the artifact I'd want to screen-share in the first
five minutes.
