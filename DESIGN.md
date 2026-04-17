# System Architecture & Design

Technical design document for the IT Procurement Demand Management
portfolio analysis.

**Companion to:** [`README.md`](README.md) (overview) and
[`FINDINGS.md`](FINDINGS.md) (analytical results).

---

## 1. Goals & Non-Goals

### Goals

- **Reproducibility.** Anyone cloning the repository should be able to
  run three commands and get byte-identical outputs.
- **Separation of concerns.** Data generation, analysis, and presentation
  are three independent scripts that communicate through files on disk.
- **Explainability.** Every number on the final page is traceable back
  to a specific SQL query that a reviewer can read and re-run.
- **No proprietary dependencies.** Works on a stock Python install —
  no database server, no BI tool license, no cloud account.

### Non-Goals

- Interactive dashboarding (a static page is sufficient for the portfolio
  demo and has zero hosting cost).
- Real-time data. The pipeline is batch; refreshing means re-running it.
- Handling multi-gigabyte data. SQLite in-memory is the right tool for
  the 1,000-row regime this project targets.

---

## 2. High-Level Architecture

```
┌──────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│ generate_data.py │ ───▶ │ data/            │ ───▶ │ analyze.py      │
│                  │      │   procurement.csv│      │  (SQL on SQLite)│
└──────────────────┘      └──────────────────┘      └────────┬────────┘
                                                             │
                                                             ▼
                                                    ┌────────────────┐
                                                    │ out/           │
                                                    │  findings.json │
                                                    │  chart_*.png   │
                                                    └────────┬───────┘
                                                             │
                                                             ▼
                                                   ┌───────────────────┐
                                                   │ build_page.py     │
                                                   │  → out/index.html │
                                                   └───────────────────┘
```

Each box is a pure function over its inputs. Re-running any downstream
stage is cheap; upstream stages don't need to know about downstream
stages.

---

## 3. Component Design

### 3.1 `scripts/generate_data.py` — Data Generation

**Purpose.** Produce a deterministic synthetic dataset that mimics the
structure of real enterprise procurement data.

**Design decisions:**

| Decision | Rationale |
| --- | --- |
| Use `random.seed(42)` | Reproducibility — same output every run. |
| Category-specific price & qty ranges | Uniform random across the whole catalog would produce nonsense (1 laptop for $250K, 500 servers for $1K each). Realistic ranges make the aggregates defensible. |
| Contract term tied to category | Software/Cloud/Security default to 12–36 mo; hardware to 12/36/60 mo — matches real enterprise MSA norms. |
| Status weighted toward "Active" | Most POs in a real portfolio are active; the sampler biases to that. |
| Renewal-date / status coupling | If `renewal_date` is within 90 days of "today" and status is Active, probabilistically upgrade to "Pending Renewal". This is the only dependent column — it's what makes Section 9 of the findings meaningful. |
| Utilization drawn from `gauss(68, 22)` clamped to [5, 100] | Mirrors the rough shape of real license-server telemetry: most seats in the 50–85% band, long left tail of under-used licenses. |

**Schema (13 columns):**

```sql
po_id                TEXT      PO identifier (PO-00001 .. PO-01000)
purchase_date        DATE      When the PO was placed
vendor               TEXT      Dell, Microsoft, Cisco, ...
category             TEXT      One of 7 fixed categories
business_unit        TEXT      One of 6 fixed BUs
item_description     TEXT      Free-text composed from vendor + category
quantity             INTEGER   Category-bounded
unit_price_usd       DECIMAL   Category-bounded, 2dp
total_spend_usd      DECIMAL   quantity × unit_price (precomputed)
contract_term_months INTEGER   12, 24, 36, or 60
renewal_date         DATE      purchase_date + term_months × 30
utilization_pct      INTEGER   Clamped Gaussian, 5–100
status               TEXT      Active / Pending Renewal / Retired / In Procurement
```

**Output:** `data/procurement.csv` (1,000 rows, ~110 KB).

---

### 3.2 `scripts/analyze.py` — Analysis Engine

**Purpose.** Run SQL against the CSV and produce structured findings
plus charts.

**Design decisions:**

| Decision | Rationale |
| --- | --- |
| **SQLite in-memory** (`:memory:`) | Zero-setup, fast for 1k rows, real ANSI SQL. The analyst can later copy these queries directly into a BigQuery / Snowflake / SQL Server console with minimal changes. |
| **Load via pandas `to_sql`** | One line to go from CSV → queryable DB; pandas handles type inference. |
| **Each finding = one SQL query** | Every number is auditable. A reviewer can copy-paste any query into a SQL IDE and rerun it against the CSV. |
| **JSON intermediate output** | Decouples analysis from presentation. The HTML builder doesn't need pandas; anyone could build a different renderer (LaTeX, PowerPoint export, Streamlit) from the same `findings.json`. |
| **Matplotlib, no seaborn** | One less dependency. The `Agg` backend means no display server is needed, so this runs in CI or a headless server. |

**SQL queries authored:**

1. **Portfolio KPIs** — `COUNT(*)`, `SUM`, `AVG`, `COUNT(DISTINCT ...)`.
2. **Spend by category** — `GROUP BY category`.
3. **Top 10 vendors by spend** — `GROUP BY vendor ORDER BY SUM(...) DESC LIMIT 10`.
4. **Spend by business unit** — `GROUP BY business_unit`.
5. **Renewals next 90 days** — `WHERE` clause using SQLite's `julianday()` date-diff, filtered to active/pending statuses only.
6. **Underutilized assets** — `WHERE status='Active' AND utilization_pct < 40`.
7. **Consolidation candidates** — `GROUP BY business_unit, category HAVING COUNT(DISTINCT vendor) >= 3`.

**Output:**

- `out/findings.json` — all numeric results.
- `out/chart_category.png` — horizontal bar, $M scale.
- `out/chart_vendors.png` — horizontal bar, gold accent.
- `out/chart_bu.png` — vertical bar.

---

### 3.3 `scripts/build_page.py` — Presentation Layer

**Purpose.** Render a polished, self-contained static HTML report from
`findings.json`.

**Design decisions:**

| Decision | Rationale |
| --- | --- |
| **Plain Python string templating** | No Jinja, no React — one file, zero build step. A reviewer can read the template and the logic side-by-side. |
| **Inline CSS in the `<style>` block** | The output is a single, portable HTML file with three PNG siblings. Can be emailed, zipped, or dropped on any static host. |
| **Visa brand palette** (navy #1a1f71, gold #f7b600) | Signals intent — this is tailored to the role, not a generic template. |
| **Serif body + sans-serif UI** | Mirrors an academic-report feel for the narrative while keeping tables and KPI cards crisp. |
| **"Why this question?" callouts** | Every section justifies itself before showing the result. This is the pedagogical move that separates a findings doc from a dashboard. |

**Output:** `out/index.html` (~16 KB).

---

## 4. Data Science Notes

### Utilization distribution

Utilization is modeled as `clamp(gauss(μ=68, σ=22), 5, 100)`. The
choice of parameters is intentional:

- **μ=68%** lands between the two common enterprise benchmarks —
  Gartner reports software-license utilization clustering at 60–70%
  in mid-maturity IT orgs.
- **σ=22** produces enough left-tail mass (around 7% below 40%) to
  create a defensible reclaim list without the story becoming
  implausible.
- **Clamp [5, 100]** because utilization <5% typically means the
  license was purchased but never deployed — a different conversation
  than underutilization, handled separately in mature programs.

### Renewal-window threshold

Ninety days is the standard BA checkpoint:

- **Earlier** (6+ months) and demand forecasts are noisy — product
  owners haven't finalized next-year requirements.
- **Later** (30 days) and Procurement has already started the renewal
  paperwork; negotiation leverage is gone.
- Ninety days aligns with most enterprise MSA cancellation-notice
  windows and is the window referenced in the Visa BA JD itself.

### Consolidation threshold (3+ vendors)

The "3 or more vendors in the same BU × category" rule is chosen
because:

- With 2 vendors there's usually a deliberate dual-sourcing reason
  (DR, vendor lock-in hedge). Flagging those creates noise.
- With 3+ the redundancy is almost always historical / unintentional.
- This threshold is standard in Gartner's "Vendor Rationalization
  Playbook."

### Statistical caveats

This is a **descriptive** analysis, not an inferential one. No
confidence intervals are reported because:

- The dataset is the entire "universe" of POs, not a sample — so
  classical CI doesn't apply.
- Utilization is modeled, not measured, so any CI would be on the
  model's randomness, not on estimation uncertainty.

A production version would replace the modeled utilization with
real telemetry and report each vendor's reclaim estimate with a
± band tied to observation count.

---

## 5. Reproducibility

**Deterministic seed.** `random.seed(42)` at the top of `generate_data.py`.
Running the three scripts in order always produces the same bytes on
disk for the CSV, JSON, and charts.

**Dependency floor.** Python 3.10, `pandas>=1.3`, `matplotlib>=3.5`,
`openpyxl` (only if reading the abandoned XLSX path). No OS-specific
binaries, no C extensions the user needs to build.

**Runtime.** End-to-end (generate + analyze + render) is under 4
seconds on a stock laptop.

---

## 6. Trade-offs & What I'd Change at Scale

### If this were 1M rows, not 1k

- **Swap SQLite in-memory for DuckDB.** DuckDB handles analytical
  queries over Parquet at 10-100× SQLite speed and would still
  require zero server setup.
- **Pre-aggregate in the warehouse.** In production you'd push most
  of these queries to the source warehouse (Snowflake / BigQuery)
  rather than pulling raw rows client-side.

### If this had real vendor data

- **Normalize vendor names.** "Microsoft", "MSFT Corp.", "Microsoft
  Corporation" all show up in real procurement data — a fuzzy-match
  + canonical-vendor dictionary becomes the first real work.
- **Category taxonomy becomes contested.** Getting product owners to
  agree on whether "Snowflake" is Cloud Services or Software License
  is half the job. This project sidesteps it by assigning categories
  at generation time.

### If the audience were executives, not interviewers

- **Lead with a one-page scorecard**, push the methodology appendix
  to the back.
- **Add a sensitivity tornado chart** on the $305M opportunity —
  what happens if only 40% of underutilized assets can actually be
  reclaimed?
- **Replace absolute dollars with % of budget.** Executives benchmark
  against their own budget, not the gross figure.

### If this had to be maintained

- **Add schema tests.** A handful of `assert` statements that the
  loaded CSV has the expected columns and types, so a silent
  upstream change becomes a loud failure.
- **Split the huge f-string in `build_page.py`.** Fine for now;
  once it has two authors, move to Jinja2.
- **Version the synthetic dataset.** Anyone rerunning with a
  different Python release could get different random output —
  pinning the Python version (or switching to `numpy.random.Generator`
  with `BitGenerator` state pickled) fixes this.

---

## 7. File Inventory

```
Ethan_visa/
├── README.md                 Sales pitch for the interviewer
├── FINDINGS.md               Narrative findings + recommendations
├── DESIGN.md                 This document
├── data/
│   └── procurement.csv       1,000-row synthetic dataset
├── scripts/
│   ├── generate_data.py      Builds the CSV
│   ├── analyze.py            SQL + chart generation
│   └── build_page.py         HTML renderer
├── out/
│   ├── findings.json         Structured analytical results
│   ├── chart_category.png    Spend by category
│   ├── chart_vendors.png     Top 10 vendors
│   ├── chart_bu.png          Spend by BU
│   └── index.html            Final static report
└── .claude/
    └── launch.json           Local preview server config
```

---

## 8. How to Run

```bash
# From project root
python scripts/generate_data.py   # 1s  → data/procurement.csv
python scripts/analyze.py         # 2s  → out/findings.json + charts
python scripts/build_page.py      # <1s → out/index.html
```

Then open `out/index.html` in a browser, or serve it locally:

```bash
python -m http.server 8765 --directory out
# visit http://localhost:8765
```
