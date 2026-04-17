# Findings — IT Procurement Demand Management Analysis

**Author:** Ethan Hennenhoefer, B.S. Information Technology, Texas Tech University (May 2026)
**Companion to:** [`out/index.html`](out/index.html) (visual report) and [`DESIGN.md`](DESIGN.md) (technical design)

---

## Executive Summary

This project analyzes a portfolio of **1,000 enterprise IT purchase orders
totaling $4.92B** across 25 vendors and 6 business units. The objective
is to demonstrate the core workflow of an IT Demand Management Business
Analyst: extract procurement data from a source system, normalize it
with SQL, and surface actionable opportunities for cost reduction and
strategic alignment.

Three optimization levers were identified:

1. **45 contracts worth $310M** renewing in the next 90 days — requiring
   immediate demand validation.
2. **67 active assets under 40% utilization** tying up **$274M** of
   reclaimable spend.
3. **10 business-unit × category pairs** with 3+ redundant vendors —
   strong consolidation candidates.

Combined addressable spend: **~$305M**, roughly **6% of the portfolio** —
inside the industry-typical 3–8% efficiency band for mature Demand
Management programs.

---

## 1. Portfolio Baseline

| KPI              | Value   |
| ---------------- | ------- |
| Active POs       | 1,000   |
| Total Spend      | $4.92B  |
| Average PO Value | $4.92M  |
| Vendors          | 25      |
| Business Units   | 6       |

**Why this matters.** Before identifying opportunities, leadership
needs a shared picture of the portfolio's size. The wide spread between
median and average PO value signals a long-tail of small purchases
alongside a handful of very large enterprise agreements — a shape that
rewards vendor-level analysis over PO-level analysis.

---

## 2. Spend by Category

| Category          | Spend    | % of Portfolio |
| ----------------- | -------- | -------------- |
| Software License  | $4.37B   | 89%            |
| Security          | $264M    | 5%             |
| Storage           | $63M     | 1%             |
| Cloud Services    | $60M     | 1%             |
| Network Hardware  | $58M     | 1%             |
| Server Hardware   | $55M     | 1%             |
| Laptops           | $53M     | 1%             |

**Finding.** Software Licenses dominate spend at **89% of the portfolio**.
This is where utilization review, license right-sizing, and
enterprise-agreement renegotiation will produce the largest dollar
impact. Hardware categories are comparatively small and stable.

**Why this matters.** Category-level rollups let us prioritize which
spend buckets deserve the most scrutiny. A 2% improvement on Software
Licenses ($87M) is worth more than a 50% improvement on Laptops ($26M).

---

## 3. Vendor Concentration

**Top 5 vendors: Datadog, Splunk, Salesforce, Microsoft, Oracle.**
These account for **78% of total spend** — a highly concentrated
book. The top 10 reach roughly 96%.

**Finding.** When 5 vendors own the majority of spend, negotiating
leverage concentrates with them — but that concentration is also the
BA's leverage. Consolidated volume means bigger discount tiers, and
bundling smaller contracts into existing master agreements is the
lowest-effort discount path.

---

## 4. Spend by Business Unit

| Business Unit     | Spend   |
| ----------------- | ------- |
| Data Platform     | $913M   |
| Corporate IT      | $890M   |
| Fraud & Risk      | $844M   |
| Consumer Products | $828M   |
| Merchant Services | $742M   |
| Core Payments     | $707M   |

**Finding.** Spend is roughly balanced, with only a 29% spread between
highest and lowest BU. No single BU is a runaway consumer, so
optimization effort should be **category-first**, not BU-first.

**Why this matters.** Per-BU spend rollups are the basis of *showback*
(and, later, chargeback) — the mechanism that makes product owners
accountable for their consumption instead of treating IT as a free
shared pool.

---

## 5. Renewal Pipeline (Next 90 Days)

**45 contracts worth $310M renew before July 15, 2026.**

First 10 (by date):

| Renewal    | Vendor      | Category          | Business Unit     | Spend       |
| ---------- | ----------- | ----------------- | ----------------- | ----------- |
| 2026-04-16 | Microsoft   | Software License  | Fraud & Risk      | $5.36M      |
| 2026-04-16 | Lenovo      | Laptops           | Corporate IT      | $0.27M      |
| 2026-04-17 | Azure       | Cloud Services    | Merchant Services | $0.75M      |
| 2026-04-19 | Dell EMC    | Storage           | Data Platform     | $0.34M      |
| 2026-04-19 | GCP         | Cloud Services    | Consumer Products | $0.19M      |
| 2026-04-21 | Dell EMC    | Storage           | Data Platform     | $0.25M      |
| 2026-04-21 | Lenovo      | Server Hardware   | Corporate IT      | $0.34M      |
| 2026-04-22 | GCP         | Cloud Services    | Merchant Services | $0.17M      |
| 2026-04-24 | Okta        | Security          | Corporate IT      | $0.98M      |
| 2026-04-25 | HPE         | Server Hardware   | Consumer Products | $0.38M      |

**Recommendation.** Each renewal needs a product-owner sign-off
confirming demand alignment before Procurement acts. A 5–10% negotiated
reduction on this book yields **~$23M in savings**.

**Why this matters.** Auto-renewal is the single largest source of
preventable IT waste. A contract that renews without demand validation
locks in last year's assumptions for another 12–36 months.

---

## 6. Underutilized Assets (Reclaim Opportunity)

**67 active assets run below 40% utilization, representing $274M of
reclaimable spend.**

Top 10 reclaim candidates:

| Vendor      | Category          | Business Unit     | Spend    | Util |
| ----------- | ----------------- | ----------------- | -------- | ---- |
| Datadog     | Software License  | Consumer Products | $61.1M   | 36%  |
| Microsoft   | Software License  | Data Platform     | $58.1M   | 20%  |
| Salesforce  | Software License  | Core Payments     | $29.1M   | 39%  |
| Splunk      | Software License  | Consumer Products | $24.2M   | 31%  |
| Oracle      | Software License  | Consumer Products | $24.0M   | 33%  |
| ServiceNow  | Software License  | Consumer Products | $24.0M   | 31%  |
| Splunk      | Software License  | Core Payments     | $13.2M   | 12%  |
| Palo Alto   | Security          | Consumer Products | $6.1M    | 17%  |
| ServiceNow  | Software License  | Data Platform     | $6.0M    | 36%  |
| CrowdStrike | Security          | Fraud & Risk      | $3.4M    | 39%  |

**Recommendation.** Downsize observability/monitoring license tiers
(Datadog, Splunk) to match actual seats; retire idle Server Hardware;
renegotiate Security contracts to usage-based pricing where vendors
support it.

**Why this matters.** Utilization is the demand-validation signal. An
asset paid for but running below 40% means either over-buying or a use
case that has gone away. It is the most defensible cost-reduction
argument a BA can bring to a product owner — the receipt is the
telemetry.

---

## 7. Vendor Consolidation Candidates

**10 BU × category pairs have 3+ active vendors serving the same need.**

| Business Unit     | Category         | Vendors | Spend   |
| ----------------- | ---------------- | ------- | ------- |
| Data Platform     | Software License | 6       | $653M   |
| Corporate IT      | Software License | 6       | $538M   |
| Consumer Products | Software License | 6       | $538M   |
| Merchant Services | Software License | 6       | $519M   |
| Core Payments    | Software License  | 6       | $514M   |
| Fraud & Risk      | Software License | 4       | $472M   |
| Corporate IT      | Security         | 4       | $42M    |
| Consumer Products | Security         | 4       | $32M    |
| Data Platform     | Security         | 4       | $21M    |
| Merchant Services | Security         | 4       | $20M    |

**Finding.** Software License overlaps across every BU are the biggest
target. Consolidating to 1–2 preferred vendors per BU typically yields
**8–15% savings** from discount-tier upgrades alone, independent of
any usage reduction.

**Why this matters.** When three or more vendors sell overlapping
products to the same BU, the enterprise is paying a "variety tax" —
duplicated onboarding, support, training, and no single agreement
reaches peak volume discount tiers.

---

## 8. Recommendations (Prioritized)

1. **Stand up a 90-day renewal review.** All 45 upcoming renewals
   should pass through a product-owner sign-off before Procurement
   acts. Target: 5–10% reduction on the renewal book.
2. **Launch a utilization reclaim sprint.** The 67 underutilized
   assets are the lowest-friction savings — product owners volunteer
   reductions when presented with their own telemetry.
3. **Begin vendor rationalization on Software Licenses.** At 89% of
   the portfolio, this category pays back consolidation investment
   fastest. Start with the six 6-vendor BU × Software-License pairs.
4. **Institutionalize BU showback.** The BU-level breakdown should
   become a monthly leadership artifact, not a one-time analysis.

---

## 9. Limitations

- **Synthetic data.** The 1,000 PO records were generated with a seeded
  random process. Absolute dollar figures are not a benchmark — the
  value is in the analytical method, not the specific totals.
- **Utilization is modeled, not measured.** In a real deployment this
  signal would come from license-server telemetry (FlexNet, Sassafras)
  or cloud-cost platforms (Apptio, Flexera).
- **No time-series.** Only a snapshot is analyzed; trend detection
  (category growth outpacing budget) is a natural next extension.
- **No join to headcount.** Per-seat unit economics — the *real*
  "run IT like a business" KPI — require a workforce-size table not
  present in this dataset.

---

## 10. Next Iterations

1. Time-series spend trending to detect categories outpacing budget.
2. Sensitivity / scenario model sizing savings under different
   consolidation assumptions.
3. Join with a headcount-by-BU table to report per-seat unit economics.
4. Add a confidence band around each utilization figure using
   observation-count as a proxy for measurement reliability.
