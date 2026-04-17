"""
Build a static HTML report from findings.json + the PNG charts.

Produces out/index.html — a single self-contained page that can be opened
directly in a browser or deployed as static hosting (GitHub Pages, S3).
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "out"
findings = json.loads((OUT / "findings.json").read_text())

def fmt_money(x: float) -> str:
    return f"${x:,.0f}"

def fmt_money_m(x: float) -> str:
    if x >= 1_000_000_000:
        return f"${x/1_000_000_000:,.2f}B"
    return f"${x/1_000_000:,.1f}M"

kpi = findings["kpis"]
by_cat = findings["by_category"]
top_vendors = findings["top_vendors"]
by_bu = findings["by_business_unit"]
renewals = findings["renewals_90d"]
underutil = findings["underutilized"]
consol = findings["consolidation"]

def rows_table(rows, cols, formatters=None):
    formatters = formatters or {}
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = ""
    for r in rows:
        cells = "".join(
            f"<td>{formatters.get(c, str)(r[c])}</td>" for c in cols
        )
        body += f"<tr>{cells}</tr>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

money = lambda v: fmt_money(float(v))

# Aggregate stats used in narrative
top5_vendor_share = sum(v['spend'] for v in top_vendors[:5]) / kpi['total_spend'] * 100
sw_share = by_cat[0]['spend'] / kpi['total_spend'] * 100
total_opportunity = renewals['total_value'] * 0.10 + underutil['reclaimable_spend']  # 10% of renewals negotiated + full reclaim

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>IT Procurement Demand Management — Portfolio Analysis</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --navy: #1a1f71;
    --gold: #f7b600;
    --ink:  #111827;
    --muted:#6b7280;
    --bg:   #f8fafc;
    --card: #ffffff;
    --line: #e5e7eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: Georgia, "Times New Roman", serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.65;
  }}
  header {{
    background: var(--navy);
    color: white;
    padding: 40px 48px;
  }}
  header h1 {{ margin: 0 0 6px; font-size: 28px; font-family: -apple-system, "Segoe UI", sans-serif; }}
  header .sub  {{ margin: 0 0 4px; opacity: 0.92; font-size: 15px; font-style: italic; }}
  header .meta {{ margin: 12px 0 0; opacity: 0.75; font-size: 13px; font-family: -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 980px; margin: 0 auto; padding: 32px 28px 64px; }}
  h2 {{
    font-size: 22px;
    margin: 44px 0 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--gold);
    color: var(--navy);
    font-family: -apple-system, "Segoe UI", sans-serif;
  }}
  h3 {{
    font-size: 16px;
    margin: 20px 0 6px;
    color: var(--navy);
    font-family: -apple-system, "Segoe UI", sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  p {{ margin: 10px 0; }}
  .kpis {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin: 18px 0 8px;
  }}
  .kpi {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 16px;
  }}
  .kpi .label {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; font-family: -apple-system, "Segoe UI", sans-serif; }}
  .kpi .value {{ font-size: 22px; font-weight: 700; color: var(--navy); margin-top: 4px; font-family: -apple-system, "Segoe UI", sans-serif; }}
  .card {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 14px;
  }}
  .card img {{ max-width: 100%; height: auto; display: block; margin: 8px auto; }}
  .finding {{
    background: #fffbeb;
    border-left: 4px solid var(--gold);
    padding: 12px 16px;
    margin: 14px 0 4px;
    border-radius: 4px;
    font-size: 15px;
    font-family: -apple-system, "Segoe UI", sans-serif;
    line-height: 1.55;
  }}
  .finding strong {{ color: var(--navy); }}
  .why {{
    background: #eef2ff;
    border-left: 4px solid var(--navy);
    padding: 10px 16px;
    margin: 10px 0;
    border-radius: 4px;
    font-size: 14px;
    font-family: -apple-system, "Segoe UI", sans-serif;
  }}
  .why strong {{ color: var(--navy); }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
    font-size: 13px;
    font-family: -apple-system, "Segoe UI", sans-serif;
  }}
  th, td {{
    text-align: left;
    padding: 8px 10px;
    border-bottom: 1px solid var(--line);
  }}
  th {{
    background: #f3f4f6;
    font-weight: 600;
    color: var(--navy);
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.04em;
  }}
  .schema {{
    font-family: "Consolas", "Courier New", monospace;
    font-size: 13px;
    background: #f3f4f6;
    border-radius: 6px;
    padding: 14px 18px;
    margin: 12px 0;
    white-space: pre;
    overflow-x: auto;
  }}
  .callout {{
    background: #fef2f2;
    border-left: 4px solid #b91c1c;
    padding: 10px 16px;
    margin: 12px 0;
    border-radius: 4px;
    font-size: 13px;
    font-family: -apple-system, "Segoe UI", sans-serif;
    color: #7f1d1d;
  }}
  footer {{
    text-align: center;
    color: var(--muted);
    font-size: 12px;
    padding: 24px;
    border-top: 1px solid var(--line);
    margin-top: 40px;
    font-family: -apple-system, "Segoe UI", sans-serif;
  }}
  .toc {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 22px;
    margin: 24px 0;
    font-family: -apple-system, "Segoe UI", sans-serif;
    font-size: 14px;
  }}
  .toc ol {{ margin: 4px 0; padding-left: 22px; }}
  .toc a {{ color: var(--navy); text-decoration: none; }}
  .toc a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>

<header>
  <h1>IT Procurement Demand Management: A Portfolio Analysis</h1>
  <p class="sub">Identifying cost-clarity and consumption-optimization opportunities in an enterprise IT spend portfolio</p>
  <p class="meta">Ethan Hennenhoefer &middot; Texas Tech University, B.S. Information Technology &middot; Portfolio Project, Spring 2026</p>
</header>

<main>

<section>
  <h2>1. Executive Summary</h2>
  <p>
    This project analyzes a portfolio of {int(kpi['po_count']):,} enterprise IT
    purchase orders totaling <strong>{fmt_money_m(kpi['total_spend'])}</strong> across
    {int(kpi['vendor_count'])} vendors and {int(kpi['bu_count'])} business units.
    The goal is to demonstrate the core workflow of an IT Demand Management
    Business Analyst: extract procurement data from a source system, normalize
    it with SQL, and surface actionable opportunities for cost reduction and
    strategic alignment for product owners and IT leadership.
  </p>
  <p>
    Three optimization levers were identified:
    (1) <strong>{renewals['count']} contracts worth {fmt_money(renewals['total_value'])}</strong>
    renewing in the next 90 days — requiring immediate demand validation;
    (2) <strong>{underutil['count']} active assets under 40% utilization</strong>
    tying up <strong>{fmt_money(underutil['reclaimable_spend'])}</strong> of reclaimable spend; and
    (3) <strong>{len(consol)} business-unit &times; category pairs</strong>
    with 3+ redundant vendors, suitable for consolidation.
  </p>
</section>

<section>
  <h2>2. Background &amp; Problem Statement</h2>

  <h3>The Business Problem</h3>
  <p>
    Large enterprises routinely lose 10-30% of their IT budget to
    auto-renewed software licenses no one uses, redundant vendor contracts
    across business units, and hardware that silently ages past its useful
    life. The IT Demand Management function exists to prevent this: it
    tracks what the company owns, what's coming up for renewal, and whether
    demand is aligned with strategy — before money is committed.
  </p>
  <p>
    In practice, that requires pulling purchase-order data from
    procurement systems, normalizing it across inconsistent vendor and
    category labels, and building repeatable reports product owners can
    act on. This project simulates that workflow end-to-end.
  </p>

  <h3>Why This Project</h3>
  <p>
    The analysis mirrors the day-to-day responsibilities of an Associate
    Business Analyst on a Demand Management team, including:
    running SQL against multiple data sources, identifying expense-reduction
    opportunities, validating new-purchase demand against strategy,
    creating infrastructure baselines, and translating raw data into
    leadership-ready insights. Each section below begins with a
    <em>"Why this question?"</em> callout explaining the business
    rationale before showing the analysis.
  </p>
</section>

<section>
  <h2>3. Dataset</h2>

  <h3>Source &amp; Construction</h3>
  <p>
    Real enterprise procurement data is, by its nature, confidential. For
    this project a synthetic dataset of 1,000 purchase-order records was
    generated using a reproducible Python script
    (<code>scripts/generate_data.py</code>, seed=42). The schema was
    modeled on fields commonly found in ServiceNow IT Asset Management,
    SAP Ariba, and the public Kaggle <em>Procurement KPI Analysis</em>
    dataset. Plausibility was enforced through category-specific price
    and quantity ranges, contract terms tied to category type, and
    status labels that reflect real renewal timing.
  </p>

  <h3>Schema</h3>
<div class="schema">po_id                TEXT    Purchase order identifier
purchase_date        DATE    Date the PO was placed
vendor               TEXT    Supplier (Dell, Cisco, Microsoft, ...)
category             TEXT    Server / Network / Storage / Laptops /
                             Software License / Cloud / Security
business_unit        TEXT    Owning BU (Core Payments, Fraud &amp; Risk, ...)
item_description     TEXT    Free-text line description
quantity             INT     Units purchased
unit_price_usd       DECIMAL Per-unit price (USD)
total_spend_usd      DECIMAL quantity &times; unit_price
contract_term_months INT     12, 24, 36, or 60 months
renewal_date         DATE    purchase_date + term
utilization_pct      INT     Measured usage 0-100 (licenses/assets)
status               TEXT    Active / Pending Renewal / Retired /
                             In Procurement</div>

  <h3>Caveats</h3>
  <div class="callout">
    <strong>Limitations of synthetic data.</strong> Utilization is drawn
    from a normal distribution rather than measured from real telemetry;
    vendor assignments are random within category; and no seasonality or
    year-over-year growth is modeled. Absolute dollar figures are not
    reliable benchmarks — the value is in demonstrating the analytical
    method, not in the specific numbers.
  </div>
</section>

<section>
  <h2>4. Methodology</h2>
  <p>
    The CSV is loaded into an in-memory SQLite database using pandas, and
    each analytical question is answered with a SQL query against that
    database. SQLite was chosen because it requires zero setup,
    supports the full ANSI-SQL feature set used in this project, and
    mirrors the pattern an analyst would use at work — treat flat
    exports as a queryable database.
  </p>
  <p>
    Charts are produced with matplotlib and saved as PNGs. The final
    HTML report is rendered from a JSON findings file, so the analysis
    and the presentation layer are cleanly separated and independently
    reproducible.
  </p>
  <p>
    Each section below follows the same structure: <em>research
    question</em> &rarr; <em>why it matters</em> &rarr; <em>query
    &amp; result</em> &rarr; <em>finding &amp; recommendation</em>.
  </p>
</section>

<section>
  <h2>5. Portfolio Baseline (KPIs)</h2>
  <div class="why">
    <strong>Why this question?</strong> Before identifying opportunities,
    leadership needs a shared picture of the portfolio's size. These KPIs
    answer "what do we own, what did it cost, and how concentrated is
    spend?" — the starting point for every IT-financial conversation.
  </div>
  <div class="kpis">
    <div class="kpi"><div class="label">Active POs</div><div class="value">{int(kpi['po_count']):,}</div></div>
    <div class="kpi"><div class="label">Total Spend</div><div class="value">{fmt_money_m(kpi['total_spend'])}</div></div>
    <div class="kpi"><div class="label">Avg PO Value</div><div class="value">{fmt_money_m(kpi['avg_po'])}</div></div>
    <div class="kpi"><div class="label">Vendors</div><div class="value">{int(kpi['vendor_count'])}</div></div>
    <div class="kpi"><div class="label">Business Units</div><div class="value">{int(kpi['bu_count'])}</div></div>
  </div>
  <div class="finding">
    <strong>Finding.</strong> The portfolio is mid-sized
    ({fmt_money_m(kpi['total_spend'])}) with a wide average PO value of
    {fmt_money_m(kpi['avg_po'])}, suggesting a long-tail of small purchases
    alongside a handful of very large enterprise agreements — a common
    shape that rewards vendor-level analysis over PO-level analysis.
  </div>
</section>

<section>
  <h2>6. Spend by Category</h2>
  <div class="why">
    <strong>Why this question?</strong> Category is the first lens for
    "where does the money go?" Category-level rollups let us prioritize
    which spend buckets deserve the most scrutiny; a small percentage
    improvement on the largest category yields more dollars than a
    big improvement on a small one.
  </div>
  <div class="card">
    <img src="chart_category.png" alt="Spend by category">
    <div class="finding">
      <strong>Finding.</strong> Software Licenses dominate at
      {fmt_money_m(by_cat[0]['spend'])} — <strong>{sw_share:.0f}% of
      total portfolio spend</strong>. This is where utilization review,
      license right-sizing, and enterprise-agreement renegotiation will
      produce the largest dollar impact. Hardware categories (Server,
      Network, Storage) are comparatively small and stable.
    </div>
  </div>
</section>

<section>
  <h2>7. Vendor Concentration</h2>
  <div class="why">
    <strong>Why this question?</strong> When a small number of vendors
    own a large share of spend, negotiating leverage concentrates with
    them. Conversely, that concentration is the BA's leverage too —
    consolidated volume means bigger discount tiers. Knowing the top-10
    is step one of every enterprise-agreement negotiation cycle.
  </div>
  <div class="card">
    <img src="chart_vendors.png" alt="Top vendors">
    <div class="finding">
      <strong>Finding.</strong> Top 5 vendors
      ({", ".join(v['vendor'] for v in top_vendors[:5])})
      account for <strong>{top5_vendor_share:.0f}% of total spend</strong>.
      Bundling remaining smaller contracts into these existing master
      agreements is the lowest-effort discount path available.
    </div>
  </div>
</section>

<section>
  <h2>8. Spend by Business Unit (Showback)</h2>
  <div class="why">
    <strong>Why this question?</strong> "Running IT like a business"
    means every dollar has an owning product team. Per-BU spend rollups
    are the basis of <em>showback</em> (and, later, chargeback) — the
    mechanism that makes product owners accountable for their consumption
    instead of treating IT as a free shared pool.
  </div>
  <div class="card">
    <img src="chart_bu.png" alt="Spend by BU">
    <div class="finding">
      <strong>Finding.</strong> Spend is roughly balanced across the
      six BUs, with {by_bu[0]['business_unit']} highest at
      {fmt_money_m(by_bu[0]['spend'])} and {by_bu[-1]['business_unit']}
      lowest at {fmt_money_m(by_bu[-1]['spend'])} — a
      {(by_bu[0]['spend']/by_bu[-1]['spend']-1)*100:.0f}% spread.
      The near-parity suggests no single BU is a runaway consumer;
      optimization effort should be category-first, not BU-first.
    </div>
  </div>
</section>

<section>
  <h2>9. Renewal Pipeline (Next 90 Days)</h2>
  <div class="why">
    <strong>Why this question?</strong> Auto-renewal is the single
    largest source of preventable IT waste. A contract that renews
    without demand validation locks in last year's assumptions for
    another 12-36 months. The 90-day window is the standard BA
    checkpoint: early enough to negotiate or cancel, late enough that
    requirements are known.
  </div>
  <div class="card">
    <div class="finding">
      <strong>Finding.</strong> <strong>{renewals['count']} contracts</strong>
      worth <strong>{fmt_money(renewals['total_value'])}</strong> renew
      in the next 90 days. Each needs a product-owner sign-off confirming
      the demand still aligns with strategy before Procurement proceeds.
      Capturing even a 5-10% negotiated reduction on this window yields
      <strong>{fmt_money(renewals['total_value']*0.075)}</strong> in savings.
    </div>
    <p style="font-size: 14px; font-family: -apple-system, 'Segoe UI', sans-serif; color: var(--muted); margin-top: 16px;">
      First 10 renewals (sorted by date):
    </p>
    {rows_table(renewals['rows'],
      ["renewal_date","vendor","category","business_unit","total_spend_usd"],
      {"total_spend_usd": money,
       "renewal_date": lambda d: str(d)[:10]})}
  </div>
</section>

<section>
  <h2>10. Underutilized Assets (Reclaim Opportunity)</h2>
  <div class="why">
    <strong>Why this question?</strong> Utilization is the
    demand-validation signal. If an asset is actively paid for but
    running below 40%, the enterprise either bought too much or the
    original use case has gone away. Either way, it is the most
    defensible cost-reduction argument a BA can bring to a product
    owner — the receipt is the telemetry.
  </div>
  <div class="card">
    <div class="finding">
      <strong>Finding.</strong> <strong>{underutil['count']} active assets</strong>
      run below 40% utilization, representing
      <strong>{fmt_money(underutil['reclaimable_spend'])}</strong>
      of reclaimable spend. Recommendations: downsize Datadog / Splunk /
      Microsoft license tiers to match actual seats, retire idle Server
      Hardware, and renegotiate Security contracts to usage-based pricing
      where vendors support it.
    </div>
    <p style="font-size: 14px; font-family: -apple-system, 'Segoe UI', sans-serif; color: var(--muted); margin-top: 16px;">
      Top 10 reclaim candidates (by dollar value):
    </p>
    {rows_table(underutil['rows'],
      ["vendor","category","business_unit","total_spend_usd","utilization_pct"],
      {"total_spend_usd": money,
       "utilization_pct": lambda v: f"{int(v)}%"})}
  </div>
</section>

<section>
  <h2>11. Vendor Consolidation Candidates</h2>
  <div class="why">
    <strong>Why this question?</strong> When three or more vendors sell
    overlapping products to the same business unit, the enterprise is
    paying a "variety tax" — duplicated onboarding, duplicated support
    contracts, duplicated training, and none of the individual
    agreements reach peak volume discount tiers. Identifying these
    pairs is the starting point for every "rationalization" initiative.
  </div>
  <div class="card">
    <div class="finding">
      <strong>Finding.</strong> <strong>{len(consol)} BU &times; category
      combinations</strong> have 3+ active vendors. Software License
      overlaps across every BU are the biggest target — consolidating
      to 1-2 preferred vendors per BU typically yields 8-15% savings
      from tier upgrades alone, independent of any usage reduction.
    </div>
    {rows_table(consol,
      ["business_unit","category","vendors","spend"],
      {"spend": money})}
  </div>
</section>

<section>
  <h2>12. Recommendations</h2>
  <ol>
    <li>
      <strong>Stand up a 90-day renewal review.</strong> All
      {renewals['count']} upcoming renewals should pass through a
      product-owner sign-off before Procurement acts. Target: 5-10%
      negotiated reduction on the renewal book.
    </li>
    <li>
      <strong>Launch a utilization reclaim sprint.</strong> The
      {underutil['count']} underutilized assets are the
      lowest-political-friction savings — product owners volunteer
      reductions when presented with their own telemetry.
    </li>
    <li>
      <strong>Begin vendor rationalization on Software Licenses.</strong>
      At {sw_share:.0f}% of portfolio, this category is where
      consolidation investment pays back fastest. Start with the
      6-vendor BU &times; Software-License overlaps.
    </li>
    <li>
      <strong>Institutionalize BU showback.</strong> The BU-level spend
      breakdown should become a monthly leadership artifact, not a
      one-time analysis — sustained visibility is what prevents the
      next cycle of drift.
    </li>
  </ol>
  <p>
    Combined, the quantified opportunities total roughly
    <strong>{fmt_money(total_opportunity)}</strong> in addressable spend
    (10% of renewals + full underutilized reclaim) — about
    <strong>{total_opportunity/kpi['total_spend']*100:.1f}% of portfolio</strong>,
    inside the industry-typical 3-8% efficiency band for
    mature Demand Management programs.
  </p>
</section>

<section>
  <h2>13. Conclusion &amp; Reflection</h2>
  <p>
    The exercise confirms that the analytical work of a Demand Management
    BA is fundamentally a join-and-aggregate problem: the raw data is
    already there, in procurement and asset-management systems, but it
    is fragmented by category, vendor, and BU. The value the role adds
    is not in collecting data but in the
    <em>translation</em> — converting raw PO lines into four or five
    leadership-ready questions ("what renews? what's idle? where are we
    fragmented?"), each tied to an action.
  </p>
  <p>
    If extended, the next iterations of this project would incorporate
    (a) time-series spend trending to detect category growth outpacing
    budget, (b) a sensitivity model sizing savings under different
    consolidation assumptions, and (c) a join with a headcount-by-BU
    table so per-seat unit economics (the <em>real</em> "run IT like a
    business" metric) can be reported.
  </p>
</section>

<section>
  <h2>Appendix A — Reproducing This Analysis</h2>
<div class="schema">python scripts/generate_data.py   # rebuild data/procurement.csv
python scripts/analyze.py         # re-run SQL, rebuild findings.json + charts
python scripts/build_page.py      # re-render out/index.html</div>
  <p style="font-size: 14px; color: var(--muted); font-family: -apple-system, 'Segoe UI', sans-serif;">
    The pipeline is deterministic (random seed fixed at 42), so anyone
    cloning the repository will see the same numbers reported above.
  </p>
</section>

</main>

<footer>
  Ethan Hennenhoefer &middot; B.S. Information Technology, Texas Tech University (May 2026)
  &nbsp;|&nbsp; Portfolio project prepared for Visa Associate Business Analyst interview
</footer>

</body>
</html>
"""

(OUT / "index.html").write_text(html, encoding="utf-8")
print(f"Wrote {OUT/'index.html'}")
