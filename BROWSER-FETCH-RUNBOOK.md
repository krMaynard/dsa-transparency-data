# Runbook — working the browser-fetch backlog from a persistent Claude Code session

Companion to [`SOURCES-NEEDING-BROWSER.md`](./SOURCES-NEEDING-BROWSER.md). This is
the turnkey setup for a **persistent** Claude Code session on a home box (e.g. a
ThinkCentre) to fetch the sources our headless datacenter scraper couldn't, then
run the repo's existing extractors so the results become queryable.

Why a home box beats the cloud sandbox for this: a **residential IP** (clears most
bot walls), a **real persistent browser** (renders JS, holds logins/cookies), and
**local disk + long runtime** (bulk PDFs, retries). The one thing it can't fake is
**EU geo** — see the egress note.

---

## 0. Prerequisites (once)

```bash
# both repos, as siblings (the API build reads the data repo)
git clone https://github.com/krMaynard/dsa-transparency-data.git
git clone https://github.com/krMaynard/transparency-report-api.git
# python deps used by the extractors
pip install pdfplumber openpyxl pandas requests
# claude code, if not already installed
npm i -g @anthropic-ai/claude-code    # or your usual install
```

**EU egress (do this before Section B/C).** Many DSA / harmonised reports are
geo-fenced to the EU/EEA. If the ThinkCentre is *in* the EU, you're done. If not,
put an **EU exit** in front of the browser (WireGuard/VPN to an EU endpoint, or an
EU HTTP proxy Playwright routes through). Without it, a real browser still hits a
"not available in your region" wall on those sources.

## 1. Give the session a browser (Playwright MCP)

Claude Code drives a browser through an MCP server. The Microsoft **Playwright
MCP** is the standard one (verify the current package name when you install). A
version-controlled config template ships in this repo — just copy it:

```bash
cp .mcp.example.json .mcp.json     # Claude Code auto-loads .mcp.json in this repo
npx playwright install chromium    # the browser itself
```

Or add it imperatively instead of the copy:

```bash
claude mcp add playwright -- npx @playwright/mcp@latest
# EU-geofenced sources from a non-EU box: append  --proxy-server=http://EU_HOST:PORT
# (edit the args in .mcp.example.json / .mcp.json to make it stick)
```

That exposes `browser_navigate`, `browser_click`, `browser_snapshot`,
`browser_pdf_save`, `browser_download`, etc. — enough to render a page, follow a
"download" control, and save a file. (Any equivalent browser MCP works; you just
need navigate + save-file.)

## 2. Run the session

From the **data repo**, so file paths and the extractors are right there:

```bash
cd dsa-transparency-data
claude          # interactive; or run headless/persistent under tmux/systemd
```

Keep it persistent (tmux, `systemd --user`, or `screen`) so it survives across the
queue and holds any logged-in browser session. Paste the **kickoff prompt** (§5)
to set the mission and guardrails.

---

## 3. The per-source loop

For **every** item, the shape is the same:

> **navigate → save the file to the right dir → run that dataset's extractor →
> verify it produced rows → backfill the catalogue → commit.**

Where each section's files go and what to run:

| Backlog § | Save fetched file to | Then run | Done when |
|---|---|---|---|
| **A** NY ToS | `ny-tos-reports/pdfs/<catalogue filename>.pdf` | `python3 ny-tos-reports/extract_narrative.py` | flip that row's `access` → `public` in `ny_tos_reports.csv`; extractor emits pages |
| **C** Harmonised template | `harmonised-reports/raw/<slug>.<xlsx\|xls\|zip>` + add `"<slug>": ("<file>", "<kind>")` to `SOURCES` in `harmonised-reports/extract.py` | `cd harmonised-reports && python3 extract.py` | `extracted/<slug>/NN_*.csv` written; then the verify + API steps below |
| **D** CA AB 587 | `ca-ab587/pdfs/<catalogue filename>.pdf` | `python3 ca-ab587/extract_narrative.py` | backfill `archived`/`sha256`/`bytes` in `ca-ab587/ca_ab587_reports.csv` |
| **E** India IT Rules | `india-it-rules/raw/<file>` + add `(file, kind, url)` to `SOURCES` in `india-it-rules/build_india.py` | `python3 india-it-rules/build_india.py` | new publisher's monthly rows appear in the built JSON |
| **B / C hub-pending / G1 / G2** | as above, by report type | the matching `build_*.py` / `extract.py` | rows produced; new platforms added to the relevant `SOURCES`/`SLUG_META` |

### Harmonised-template reports get a two-repo round-trip

For Section C (and any newly-found harmonised platform), the canonical end-to-end
steps live in the **`add-dsa-report` skill** in this repo
(`.claude/skills/add-dsa-report/`). In short, after `extract.py`:

```bash
# 1) confirm it extracted + is queryable
python3 .claude/skills/add-dsa-report/verify.py <slug> "<Display Name>"

# 2) API side: name the platform, re-vendor, reseed
#    (in ../transparency-report-api)
#    - add  "<slug>": ("<Display Name>", "<tier>")  to seed_harmonised.py SLUG_META
python ../transparency-report-api/scripts/revendor_data.py --summary-out -
python ../transparency-report-api/seed.py 2>&1 | tail -2
```

`verify.py <slug> "<Name>"` exiting 0 with an `OK: …` line is the definition of
done for a harmonised platform. Let the skill guide the judgment calls (display
name, `tier`, catalogue category).

### After a batch — always

```bash
# data repo: keep the catalogue current
python3 link_archives.py && python3 build_reports_db.py   # reconcile archived links
# API repo: re-vendor + reseed + run tests before shipping
cd ../transparency-report-api && python -m pytest test_api.py -q
```

Then commit on a working branch and open PRs in both repos (data: raw/ + extracted/
+ catalogue; API: `SLUG_META` + re-vendored `data/`).

---

## 4. Recommended order (easiest confirmed wins first)

1. **§D — CA AB 587** (100 PDFs). Pure fetch + disk, no geo/bot walls. Warm-up.
2. **§G1 — bot-walled clusters**. Residential IP is the whole unlock; confirm which
   platforms actually publish a report, fetch the ones that do.
3. **§B + §C — JS pages & harmonised hub-pending**. ← **enable EU egress first.**
4. **§E — India blocked publishers** (Snap, Reddit, Quora, Josh). Cloudflare +
   client-side render fall to a residential browser. (Telegram/WhatsApp are hard —
   defer.)
5. **§A — NY ToS login-gated**. First just open one `ag.ny.gov` URL in the browser:
   if it serves the PDF, it was only UA-blocking → batch it. If it's a real login,
   sign in once (human) and let the session reuse the cookie.
6. **§G2 — scout-for-more regimes**. Search + fetch; keep a human in the loop.

---

## 5. Kickoff prompt (paste into the session)

> You are working the browser-fetch backlog in `SOURCES-NEEDING-BROWSER.md` for the
> DSA transparency dashboard. You have a Playwright MCP browser and a residential
> (EU-routed) connection. Work the sections in the order in `BROWSER-FETCH-RUNBOOK.md`
> §4. For each source: open it in the browser, save the report file into the dir the
> runbook table names, run that dataset's extractor, confirm it produced rows (for
> harmonised platforms, `verify.py <slug> "<Name>"` must exit 0), and backfill the
> catalogue columns. Commit in small per-batch commits on a branch and open PRs in
> both repos when a section is done.
> **Rules:** respect robots.txt and each site's ToS; throttle (a few seconds between
> requests, no parallel hammering); if a site shows a CAPTCHA or a real login wall,
> **stop and ask me** rather than trying to defeat it; never fabricate a number — if
> a report can't be fetched or parsed, mark the catalogue row and move on; leave the
> judgment calls (a new platform's display name, `tier`, catalogue category, whether
> a page even *is* a DSA report) to me when unsure.

---

## 6. What it still won't beat

- **Genuine credentialed portals** without your login (some NY ToS filings, if the
  wall is real). One-time human sign-in fixes these; automation alone won't.
- **Hard interactive CAPTCHAs / aggressive automation-detection** on a few sites.
- **EU geo** if the box isn't in the EU and you skip the proxy (Section 0).
- **Reports that don't exist.** Much of `REPORT_LOCATIONS.md`'s "searched, not found"
  is genuinely empty (out-of-scope or unpublished) — §G1 lists only the *bot-walled*
  subset worth a browser; don't chase the rest.
