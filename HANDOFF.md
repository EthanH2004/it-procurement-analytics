# Handoff Prompt — Copy This Into A New Claude Code Session

You are continuing a project that was set up in a previous session. You
have **no memory** of that session. Everything you need is in this
directory and in this document.

---

## Who & What

- **Target user:** Eric (the dad). He's handing this off on behalf of
  his son **Ethan Hennenhoefer**, a Texas Tech IT major graduating
  May 2026.
- **Purpose of the project:** A portfolio artifact for Ethan's
  interview with **Visa** for the *Associate Business Analyst, New
  College Grad 2026* role in Austin, TX. The interviewer should see
  a **public GitHub repo** and a **live Vercel URL**.
- **What the project is:** A self-contained data analysis — 1,000-row
  synthetic IT procurement dataset, SQL analysis in Python (SQLite
  in-memory), charts via matplotlib, and a polished static HTML
  report. Built to mirror the exact workflow of an IT Demand
  Management BA.
- **Environment:** Windows 10, bash shell (git-bash), Python 3.10 at
  `C:\Users\Eric\AppData\Local\Programs\Python\Python310`. Project
  path: `C:\Users\Eric\projects\Ethan_visa`. (If the handoff zip was
  extracted somewhere else, adjust accordingly.)

---

## Your Job (In Order)

1. **Sanity-check the project**
   - Read `README.md`, `FINDINGS.md`, `DESIGN.md` so you understand
     the deliverable.
   - Re-run the pipeline to make sure nothing is broken:
     ```bash
     python scripts/generate_data.py
     python scripts/analyze.py
     python scripts/build_page.py
     ```
   - Confirm `out/index.html`, `out/findings.json`, and three
     `out/chart_*.png` files regenerated.

2. **Initialize Git & push to GitHub**
   - `gh auth status` — confirm Eric is logged in. If not, walk him
     through `gh auth login`.
   - `git init`, add a meaningful first commit. Suggested message:
     `Initial commit — IT procurement demand management portfolio project`
   - Create the GitHub repo **public** via `gh repo create`. Suggested
     name: `visa-ba-portfolio` (confirm with Eric first). Description:
     *"Portfolio analysis project for Visa Associate BA role — SQL,
     Python, static report."*
   - Push `main`.
   - **Confirm with Eric before pushing** — this is the moment the
     repo goes public.

3. **Deploy to Vercel**
   - Vercel treats this as a static project. The deployable is the
     `out/` directory.
   - Add a `vercel.json` at the project root. The simplest working
     config for a static site served from `out/`:
     ```json
     {
       "buildCommand": null,
       "outputDirectory": "out",
       "framework": null
     }
     ```
     If that doesn't behave, a fallback is to add a root-level
     `index.html` that redirects to `/` or move `out/*` to root.
     Check Vercel docs if you hit a snag —
     https://vercel.com/docs/projects/project-configuration.
   - Install Vercel CLI if not present: `npm i -g vercel`.
   - From project root: `vercel` (first time — walks Eric through
     project linking), then `vercel --prod` to ship.
   - The CLI will prompt for login — Eric will do it in the browser.
   - Capture the production URL.

4. **Update README with the live URL**
   - Replace the placeholder note in `README.md` with the Vercel URL
     so the interviewer can click straight through.
   - Commit + push.

5. **Final verification**
   - Open the Vercel URL in a browser. Confirm KPIs, charts, and
     findings render. Confirm nothing is broken (images load, CSS
     applied).
   - Report the final URLs (GitHub + Vercel) back to Eric.

---

## Important Context

### The data is synthetic
The dataset is a 1,000-row seeded synthetic CSV, documented in
`DESIGN.md §3.1`. Real procurement data is confidential. Don't let a
reviewer mistake this for production data. The `FINDINGS.md`
Limitations section (§9) and the HTML report's "Caveats" callout make
this explicit.

### Deterministic outputs
`random.seed(42)` is set at the top of `scripts/generate_data.py`.
Re-running the pipeline produces byte-identical `procurement.csv` and
therefore byte-identical `findings.json` and charts. If you see
different numbers from what's in `FINDINGS.md`, investigate — don't
just silently update the doc.

### Don't delete the committed `out/` directory
Vercel deploys from `out/`. If `out/` is not committed, the deploy
will be empty. Decision made in the previous session: we commit
`out/` rather than run Python in Vercel's build step. Keep it that
way unless there's a reason not to.

### Style / tone
This is a BA portfolio piece — polished, honest, unpretentious.
Visa-brand colors (navy `#1a1f71`, gold `#f7b600`) in the HTML are
intentional. Don't "modernize" the styling into a generic template.

---

## What's In This Directory

```
Ethan_visa/
├── HANDOFF.md                   ← YOU ARE READING THIS
├── README.md                    ← sales pitch, interviewer-facing
├── FINDINGS.md                  ← narrative findings + recommendations
├── DESIGN.md                    ← architecture + data-science design
├── .gitignore
├── BA-job-ad.txt                ← the Visa job description (reference)
├── Resume - Ethan Hennenhoefer.md  ← Ethan's resume (reference)
├── data/
│   └── procurement.csv          ← 1,000-row seeded dataset
├── scripts/
│   ├── generate_data.py         ← builds the CSV
│   ├── analyze.py               ← SQL on SQLite → findings.json + charts
│   └── build_page.py            ← renders the HTML report
├── out/
│   ├── index.html               ← the static report (Vercel serves this)
│   ├── findings.json            ← structured numeric results
│   ├── chart_category.png
│   ├── chart_vendors.png
│   └── chart_bu.png
└── .claude/
    └── launch.json              ← local preview server config (ignore for prod)
```

---

## Known Headline Numbers (To Verify After Regeneration)

If these change after you re-run the pipeline, something is broken:

- **Total spend:** $4.92B across 1,000 POs, 25 vendors, 6 BUs
- **Software License share:** 89% of portfolio ($4.37B)
- **Top 5 vendors:** Datadog, Splunk, Salesforce, Microsoft, Oracle
- **Renewals next 90 days:** 45 contracts, $309,766,685 (~$310M)
- **Underutilized (<40%) active assets:** 67, $273,714,141 (~$274M)
- **Consolidation pairs:** 10 BU × category with 3+ vendors

---

## Safety Rules for Eric's Machine

- **Confirm before pushing.** Making the repo public, deploying live —
  both are irreversible in the "this is now on the public internet"
  sense. Walk Eric through each step before executing.
- **Don't commit secrets.** There are none currently in the repo, but
  double-check. The `.gitignore` already excludes `.env*`.
- **Don't run git with `--force`** unless Eric explicitly asks.
- **Python environment:** pandas 1.3.5, matplotlib 3.5.3, openpyxl
  3.1.5 are already installed. Don't upgrade unless forced to.

---

## If Something Goes Wrong

- **`gh` not authenticated:** `gh auth login`, pick GitHub.com, HTTPS,
  log in via browser.
- **`vercel` CLI not installed:** `npm i -g vercel`. If npm isn't on
  PATH, Eric has Node via nvm — may need `nvm use <version>`.
- **Vercel deploys but page is 404:** check `vercel.json`'s
  `outputDirectory`. You can also try dropping a root-level
  `index.html` that does `<meta http-equiv="refresh" content="0; url=/">`.
- **Scripts fail with ModuleNotFoundError:** `python -m pip install
  pandas matplotlib openpyxl`.
- **Pipeline works but numbers differ from FINDINGS.md:** check that
  `random.seed(42)` is still at the top of `scripts/generate_data.py`
  and that Python major version is still 3.10.

Good luck. Eric's a reasonable collaborator — ask before you do
anything risky.
