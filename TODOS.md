# TODOS — AI Learning Skill

---

## TODO: Source Quality Cache (V2)

**What:** After Enhancement 2 (content skimming) runs per-source quality scoring, save
scores to `~/.gstack/learning/.source-cache.json` keyed by URL + role.

**Why:** On re-runs for the same product, the skill currently re-browses and re-scores
all 14 candidate URLs. With a cache, already-scored URLs skip the browse call entirely,
cutting the validation+skimming pass from ~70-110 sec back to ~10-20 sec for repeat runs.

**Pros:**
- Significant time savings for power users who re-run the skill monthly
- Makes the 7-min ceiling a non-issue after first run

**Cons:**
- Cache staleness — a source's content or quality can change
- Requires a TTL (30 days recommended) and invalidation on URL redirect changes
- Adds a cache read/write step to the combined validation pass

**Context:** Designed in the V1.x office-hours session as "Enhancement 2 Approach C."
Not built in V1 to keep scope tight. Current design doc:
`~/.gstack/projects/ai-learning/kiba-main-design-20260403-153545.md`

**Depends on:** Enhancement 2 (E2 — content skimming) must be fully implemented first.

**Where to start:** Add a `cache_check(url, role)` lookup at the start of the combined
validation pass. If cached and < 30 days old: skip browse, use cached score. If not
cached or stale: run full browse + score, then write result to cache.

---

## TODO: Parallelized Browse Processing (V2 performance)

**What:** Run the 14-source combined validation+skimming pass in parallel rather than
sequentially. Each source browse call is independent I/O.

**Why:** Sequential processing takes 70-110 sec. Parallel processing (6 concurrent)
could cut this to 15-20 sec — 4-5x speedup.

**Pros:** Dramatically reduces generation time for users who care about speed.

**Cons:**
- The browse binary may not support concurrent sessions (needs testing)
- Parallel results need to be collected and ordered after completion
- More complex SKILL.md logic

**Context:** Identified in /plan-eng-review. Deferred because timing is not a concern
for the primary use case (one-time product analysis). User confirmed low priority.

**Depends on:** Enhancement 1B + 2 (the combined validation+skimming pass) must be stable first.

---

## TODO: Hosted URL Delivery (V2 — inline messaging experience)

**What:** After generating all 15 day HTML files + manifest.json, optionally publish them
as a static mini-site (Cloudflare Pages, GitHub Pages, or Netlify Drop) so the scheduler
can send a URL per day instead of a file attachment. URL pattern: `{host}/day-01.html`,
`{host}/day-02.html`, etc. Scheduler sends today's day URL.

**Why:** V1.x delivers HTML files — users tap to download and open in a browser. A hosted
URL renders directly in Telegram/WhatsApp's in-app browser, no download needed. With 15
separate files (V2), the manifest makes this easy: one upload per curriculum run covers all
15 days.

**Design choice (updated in /plan-eng-review 2026-04-05):** Option 1 — host all 15 files
at once on curriculum generation. Not Option 2 (per-day on-demand upload), which requires
scheduler-side complexity. One upload per curriculum run, scheduler reads manifest for URLs.

**Pros:**
- Better in-app experience for messaging delivery (link vs. file download)
- Manifest.json already maps day → filename → can trivially map day → URL
- One upload, 15 days of delivery sorted

**Cons:**
- Requires external service setup (GitHub token for Pages, Cloudflare CLI, or Netlify token)
- All 15 days publicly accessible at the hosted URL (privacy consideration — content visible)
- Adds external dependency

**Context:** Discussed in V1 office-hours session. V1 decision: files not URLs (only 1 file
then). V2 now generates 15 files + manifest, making URL delivery cleaner. The manifest
serves as the scheduler's day-index regardless of whether URLs or file paths are used.

**Where to start:** After Step 5 generates all 15 files and manifest.json, add an optional
Step 5.5: read manifest, upload all files to static host, update manifest with `"url"` field
per day entry. Scheduler uses `days[N].url` if present, `days[N].file` as fallback.

**Depends on:** V2 enhancements (15-file generation + manifest.json) must be complete first.

---

## TODO: Cross-Platform Delivery Scheduler (Linux + Windows)

**What:** The delivery automation currently uses macOS launchd for scheduling. Linux users
need a cron job; Windows users need Task Scheduler (`schtasks`). Add platform detection
in Step 5.5 of `SKILL.md` so the skill generates the right scheduler artifact per OS.

**Why:** The skill is intended to be a universal AI learning tool. Users on Linux or Windows
get `deliver.py` but no working scheduler — their daily emails never fire.

**Pros:**
- Makes the skill truly cross-platform
- cron is simpler than launchd (one `crontab -e` line); Windows schtasks is more complex but
  well-documented

**Cons:**
- Adds OS detection logic to Step 5.5
- Windows Task Scheduler syntax is significantly different from launchd/cron
- Testing requires access to Linux and Windows environments

**Context:** Identified in /plan-eng-review (delivery automation PR). macOS chosen for v1
because that's the current user's platform. Deferred to keep v1 scope tight.

**Where to start:** In Step 5.5 of `SKILL.md`, add:
```bash
PLATFORM=$(python3 -c 'import sys; print(sys.platform)')
```
If `darwin` → generate launchd plist (current behavior).
If `linux` → generate `~/.gstack/learning/delivery.cron` and install with `crontab`.
If `win32` → generate a `schtasks` command and print instructions for manual setup.

**Depends on:** Daily email delivery automation (this PR) must be merged first.

---

## TODO: Outlook-Compatible Email Template

**What:** The current day HTML files use modern CSS (stylesheets, CSS variables, flexbox).
Outlook's email renderer ignores `<style>` blocks and CSS variables, producing an unstyled,
unreadable wall of text. Adding a second email-safe HTML template alongside each day file
would let `deliver.py` send an Outlook-compatible version instead of the full day HTML.

**Why:** Outlook is common in corporate environments. If a learner's work email is Outlook,
every daily email is a broken experience. The full-featured day HTML files are great for
browser viewing but not for email delivery to Outlook.

**Pros:**
- Makes the email readable in all major clients (Gmail, Apple Mail, Outlook)
- Email-safe template can be generated alongside the full HTML at negligible cost

**Cons:**
- Adds a second template to the curriculum generator (more SKILL.md complexity)
- Email-safe HTML is intentionally stripped-down — loses some visual richness
- Needs to be kept in sync with full HTML content

**Context:** Identified in /plan-eng-review. Deferred because Gmail/Apple Mail are the
primary client for the current user. The plain-text fallback (added in the delivery PR)
partially mitigates Outlook issues.

**Where to start:** In the curriculum generator (Step 4 of `SKILL.md`), generate a second
`day-NN-email.html` per day — table-based layout, no CSS variables, all styles inline.
In `deliver.py`, check if `day-NN-email.html` exists alongside `day-NN.html`; if so, send
the email version instead of the full version.

**Depends on:** Daily email delivery automation (this PR) must be merged first.

---

## TODO: Delivery Audit Log Command

**What:** Add a `delivery history` / `delivery status` command that reads `delivery.log`
and prints a formatted table of sent/failed entries, showing which days went out and when.

**Why:** Without this, the user has to manually read raw JSON from `delivery.log` to audit
whether their daily emails are actually firing. A formatted summary makes it easy to spot
gaps: "Day 5 failed — did I get it?"

**Pros:**
- Makes the delivery system auditable without opening log files
- Can surface patterns: "3 consecutive failures" → SMTP credentials may have expired
- Low complexity — reads delivery.log and formats output

**Cons:**
- Adds another command the user needs to know about
- delivery.log already exists; power users can parse it with `jq`

**Context:** Identified in /plan-eng-review. delivery.log is created by the delivery PR.
A reporting command is pure value-add with no dependencies beyond the log file existing.

**Where to start:** Add a `check_delivery` trigger to `SKILL.md` that runs:
```python
import json; [print(json.loads(l)) for l in open('~/.gstack/learning/delivery.log')]
```
Then format as a table: `Date | Day | Status | Recipient`.

**Depends on:** Daily email delivery automation (this PR) must be merged first.
