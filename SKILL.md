# AI Learning Skill — Product-Centric Curriculum Generator

**What this skill does:** You give it a real AI product you care about (e.g., "Cursor",
"Perplexity", "Notion AI") and your job function. It reverse-engineers the product's
tech stack, researches the competitive landscape and role responsibilities, then
generates a structured 15-session learning curriculum tailored to your role — with
quizzes after every session.

**Time to run:** ~8–12 minutes (first run includes a short learner profile questionnaire: AI level + calibration, daily time, format, delivery email, delivery time). Output: 15 per-day mobile-friendly HTML files + curriculum reference HTML + manifest JSON + markdown curriculum files. Profile is saved and reused on subsequent runs. Optional daily email delivery via macOS launchd (Step 5.5).

---

## SETUP

```bash
LEARNING_DIR="$HOME/.gstack/learning"
mkdir -p "$LEARNING_DIR" 2>/dev/null || LEARNING_DIR="$(pwd)"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
echo "Output directory: $LEARNING_DIR"
echo "Session timestamp: $TIMESTAMP"
```

---

## Step 0: Learner Profile Setup

Before anything else, check whether the user has a saved learner profile. This profile
tailors vocabulary depth, content density, and code example presence for all 15 sessions.

```bash
PROFILE_FILE="$HOME/.gstack/learning/.user-profile.json"
mkdir -p "$HOME/.gstack/learning" 2>/dev/null || true
```

### If the profile file exists

Load and parse `$PROFILE_FILE`. Display:
> "Using your saved learner profile:
> AI level: {ai_level_calibrated} | Daily time: {daily_minutes} min | Format: {format}
> Delivery: {delivery_email} at {delivery_time} (daily)
>
> Continue with this profile, or update it? (continue / update)"

If `delivery_email` or `delivery_time` are **missing** from the loaded profile (legacy v1
profile): treat as a partial first run — ask only Q4 and Q5 before proceeding to Step 1,
then write the profile back as version 2.

- If **continue**: skip to Step 1.
- If **update**: run the full questionnaire (Q1–Q5), overwrite the profile, then continue to Step 1.

The user can also say **"update my profile"** or **"change my preferences"** at any point
during the skill to trigger the full questionnaire (Q1–Q5) and overwrite the saved profile.

The user can say **"update delivery"**, **"change delivery email"**, **"change delivery
time"**, **"update email"**, or **"change my delivery"** at any point to re-run only Q4
and Q5, update those fields, and rebuild the delivery setup (Step 5.5) without re-running
the full questionnaire.

### If the profile file does NOT exist (first run)

Tell the user:
> "Quick setup — 5 questions to personalize your curriculum (takes ~2 minutes)."

Then run the questionnaire below.

---

### Questionnaire (Q1–Q5 + calibration after Q1, asked one at a time)

#### Q1: AI Experience Level

Ask:
> "How do you currently use AI? Pick the one that fits best:
> A) Chat only — I use ChatGPT, Claude, etc. for questions and writing
> B) Vibe coding — I use AI to help write code; tools like Cursor or Copilot
> C) Builder — I build AI-powered products (agents, workflows, integrations)
> D) Deep technical — I work on model training, fine-tuning, or ML systems"

Store as `ai_level_self`: `chat` | `vibe_coder` | `builder` | `deep_technical`

**After receiving their answer, immediately run the Calibration Quiz below before Q2.**

---

### Calibration Quiz (3 questions — run right after Q1)

These 3 questions verify the self-reported level. Scoring is deterministic from a fixed
answer key — no model judgment involved.

**Answer acceptance rule:** Accept the first letter mentioned in the user's response.
"I think it's B but maybe C" → scores as B. If no letter is identifiable, prompt once:
"Which option — A, B, C, or D?" then score that response. Do not prompt a second time;
if still unclear, count as incorrect.

**Calibration Q1:**
> "What does 'context window' mean in a large language model?
> A) The size of the screen where AI outputs are displayed
> B) The total amount of text the model can read and reason about at once
> C) The number of conversations the AI can remember across sessions
> D) A setting that controls how creative the AI's responses are"

**Calibration Q2:**
> "An AI agent calls a tool that returns an error. What should happen next?
> A) The agent stops and asks the user what to do
> B) The agent retries the same tool call with identical parameters
> C) The agent reads the error, reasons about the cause, and adjusts its approach
> D) The agent outputs the raw error message and terminates"

**Calibration Q3:**
> "What is RAG (Retrieval-Augmented Generation) primarily used for?
> A) Making AI responses faster by caching previous answers
> B) Allowing an AI to answer questions using external documents it wasn't trained on
> C) Training a model on your own data to customize its personality
> D) Connecting multiple AI models so they can collaborate on tasks"

**Fixed answer key: Q1 = B, Q2 = C, Q3 = B**

Count correct answers (0–3). Apply this table to get `ai_level_calibrated`:

| Self-reported | Correct answers | Calibrated level |
|---|---|---|
| chat | 0–1 | chat (confirmed) |
| chat | 2–3 | vibe_coder (upgraded) |
| vibe_coder | 0–1 | chat (downgraded) |
| vibe_coder | 2–3 | vibe_coder (confirmed) |
| builder | 0–1 | vibe_coder (downgraded) |
| builder | 2–3 | builder (confirmed) |
| deep_technical | 0–2 | builder (downgraded) |
| deep_technical | 3 | deep_technical (confirmed) |

Tell the user the calibration result briefly:
- If upgraded: "Based on your answers, I've set your level to {calibrated} — one step above what you selected."
- If downgraded: "Based on your answers, I've set your level to {calibrated} — the questions suggest this depth fits better."
- If confirmed: "Your level is confirmed at {calibrated}."

---

#### Q2: Daily Learning Time

Ask:
> "How long do you plan to learn each day?
> A) ~10 minutes — bite-sized, just the essentials
> B) ~20 minutes — standard sessions with full examples
> C) 30+ minutes — deep dives, I want everything"

Store as `daily_minutes`: `10` | `20` | `30` (30 = bucket for 30 or more minutes)

#### Q3: Content Format Preference

Ask:
> "What kind of content helps you learn best?
> A) Text-focused — clear explanations and analogies, no code
> B) Mixed — explanations plus code examples when relevant
> C) Technical — go deep: architecture patterns, code, implementation details"

Store as `format`: `text` | `mixed` | `technical`

#### Q4: Delivery Email

Ask:
> "What email address should your daily learning content be delivered to?"

Free-form text input. **Light validation:** check that the string contains `@` and at
least one `.` after the `@`. If invalid, prompt once: "That doesn't look like an email
address. Please re-enter." Accept whatever is provided on the second attempt.

Store as `delivery_email`.

#### Q5: Delivery Time

Ask:
> "What time of day would you like to receive your daily session?
> A) Morning — 7:00 AM
> B) Midday — 12:00 PM
> C) Evening — 7:00 PM
> D) Custom — I'll tell you a specific time"

If D: prompt once: "What time? (e.g. 8:30 AM, 6:00 PM, or 14:00)"
Parse to `"HH:MM"` 24-hour format. Default to `"07:00"` if unparseable.

Store as `delivery_time`.

---

### Write the profile

Write `$PROFILE_FILE` with this structure:

```json
{
  "version": 2,
  "created": "{ISO 8601 datetime}",
  "updated": "{ISO 8601 datetime}",
  "ai_level_self": "{answer to Q1}",
  "ai_level_calibrated": "{from calibration table}",
  "daily_minutes": {10 | 20 | 30},
  "format": "{text | mixed | technical}",
  "calibration_scores": [{true|false}, {true|false}, {true|false}],
  "delivery_email": "{answer to Q4}",
  "delivery_time": "{answer to Q5 — HH:MM format}"
}
```

**Version note:** Version 2 adds `delivery_email` and `delivery_time`. When a version 1
profile is loaded and those fields are missing, ask only Q4 and Q5, then write back as
version 2. When `version` is missing or < 1: treat as stale, re-run full questionnaire.

**Write-back verification:** After writing, attempt to read back `$PROFILE_FILE` and parse it.
If the file is missing or fails to parse after the write:
> "Note: Could not save your profile to disk — you'll be asked these questions again next
> run. Check write permissions on `~/.gstack/learning/`."
This does not block curriculum generation — warn and continue.

**Profile error handling:**
- If profile exists but fails JSON parse: treat as first run, re-run questionnaire, overwrite.
- If `version` field missing or < 1: treat as stale, re-run questionnaire, overwrite.
- If `version` == 1 and delivery fields missing: ask Q4+Q5 only, write back as version 2.
- If `~/.gstack/learning/` cannot be created: use `$(pwd)` as fallback, print warning.

---

## Step 1: Select Job Function

Ask the user which job function they're learning from. Use AskUserQuestion with the
following format. Do NOT skip this step.

> **Welcome to the AI Learning Skill.**
>
> This skill will generate a personalized 15-session AI learning curriculum anchored
> to a real product you care about. Each session is 15–20 minutes and ends with a quiz.
>
> First: which job function are you learning from?

Present as AskUserQuestion with these options:
- A) Product Manager — business decisions, prioritization, stakeholder communication
- B) Software Engineer — implementation, system design, debugging, performance
- C) UX Designer — user-facing behavior, error states, trust, interaction patterns
- D) Operations / Program Manager — rollout planning, risk, cross-team coordination
- E) Data Analyst — metrics, data quality, evaluation, bias detection
- F) Other / Not listed — will use Product Manager lens as closest general match

**Store the selection as `ROLE`.**

If the user selects F (Other), before proceeding tell them:
> "Your role isn't in the V1 list. I'll generate content from a **Product Manager
> lens** (business/strategy focus) as the closest general match. For a more tailored
> curriculum, you can re-run and choose the role closest to yours above."
>
> Proceeding with PM lens...

Set `ROLE = "Product Manager"` and `ROLE_SLUG = "product-manager"` for the output file.

**Role slug mapping:**
- Product Manager → `product-manager`
- Software Engineer → `software-engineer`
- UX Designer → `ux-designer`
- Operations / Program Manager → `operations-program-manager`
- Data Analyst → `data-analyst`

---

## Step 2: Get the Product

Ask the user (plain text, not AskUserQuestion):

> **Which AI product do you want to learn about?**
>
> Examples: "Cursor", "Perplexity", "Notion AI", "ChatGPT", "GitHub Copilot",
> "Midjourney", "Salesforce Einstein", "Duolingo Max"
>
> Tip: Pick a product you use, work on, or compete with. The more you care about it,
> the more motivating the curriculum will be.

**Store the product name as `PRODUCT`.**

Generate the product slug:
- Lowercase the product name
- Replace spaces with hyphens
- Remove non-ASCII characters
- Example: "Notion AI" → `notion-ai`, "ChatGPT" → `chatgpt`

**Store as `PRODUCT_SLUG`.**

Output filenames:
- Curriculum: `{PRODUCT_SLUG}-{ROLE_SLUG}-curriculum.md`
- Curriculum HTML: `{PRODUCT_SLUG}-{ROLE_SLUG}-curriculum.html`
- Quiz results: `quiz-{PRODUCT_SLUG}-{ROLE_SLUG}-{TIMESTAMP}.md`
- Quiz HTML: `quiz-{PRODUCT_SLUG}-{ROLE_SLUG}-{TIMESTAMP}.html`

Tell the user:
> "Got it. Generating your **{PRODUCT} curriculum for {ROLE}**.
> I'll research the product, verify sources, then build your 15-session learning plan.
> This takes 5–7 minutes — sit tight."

---

## Step 3: Research Phase — 4-Layer Search

Run all searches below using WebSearch. Apply the quality filter after each layer.
If WebSearch is unavailable, skip to Step 4 with empty search results and use
model knowledge for the full curriculum (show the no-search banner at the top of output).

### Quality Filter (apply to every source found)

**Preferred source domains (not exclusive — use judgment for unlisted domains):**
arxiv.org, huggingface.co, openai.com, anthropic.com, deepmind.google, research.google,
YouTube (prefer: 3Blue1Brown, Andrej Karpathy, StatQuest, official product channels),
official product engineering blogs (e.g., cursor.com/blog, engineering.fb.com,
netflixtechblog.com, blog.google/technology/ai/)

**Include a source if it meets ALL of:**
1. Published within the last 24 months (or is a foundational paper/resource)
2. Has a concrete example, code snippet, diagram, or comes from a primary source
3. Is readable/watchable in < 20 minutes (prefer shorter for daily sessions)

**URL specificity filter (Enhancement 1C) — reject index/listing pages:**

Before including any URL, check its path structure. REJECT (do not include as a source)
if the URL ends in any of these index patterns:
```
/           /blog        /blog/       /docs        /docs/
/articles   /resources   /topics      /feed        /rss
/tag/        /category/   /search      /archive
```
**Exception:** Keep the URL if the path has ≥ 2 segments after the section prefix.
- REJECT: `insforge.dev/blog` (index — no specific post)
- KEEP: `insforge.dev/blog/2025/byok-architecture` (specific post, 2+ segments after /blog)
- When in doubt: prefer to search for a more specific URL rather than citing an index page.

If a search result returns an index URL you want to cite, run a follow-up search:
`site:{domain} {specific topic keywords}` to find the direct article URL.

**For each qualifying source, record:**
- Title, URL, platform, estimated read/watch time, one-line summary of its value

---

### Source Diversity Rule (apply per session — all products, all job functions)

Include **as many sources as needed for a learner to fully understand the session's topic** — no fixed minimum or maximum. The right number depends on the complexity of the topic and what's available. A simple concept may need 2-3 focused sources; a complex architecture session may need 6-7. Use judgment: enough to learn, not so many it becomes overwhelming. Distribute sources across these 3 types:

| Type | Guidance | Description |
|------|----------|-------------|
| **Product-authoritative** | Use sparingly | The product's own blog, docs, or official engineering post covering the session's specific feature. Useful for product-specific context — but not the majority. |
| **Neutral / third-party** | Prioritize these | Independent coverage of the underlying technology, concept, or practice: official specs, academic papers, neutral tech blogs, conference talks, third-party comparisons. These are the **primary** learning material. |
| **Role-specific** | Include where relevant | Sources tailored to the learner's job function — PM craft, engineering guides, UX methods, analyst frameworks. Weight these more heavily in Modules 3 and 5. |

**Enforcement rules:**
- **Target:** Aim to keep product-owned sources under **40% of total sources** across the full curriculum. Track the running count as you assign sources — if trending over 40%, prioritize finding neutral alternatives for upcoming sessions. This is a quality target, not a hard limit: exceeding 40% is acceptable when credible neutral sources genuinely don't exist for the remaining topics.
- **Per-session soft cap:** Aim for 1 product-owned source per session. You may use 2 if credible neutral sources for that specific topic are genuinely unavailable — but never as a default.
- **Fallback:** If neutral sources are sparse for a topic, use what's available and add: `⚠️ Limited neutral coverage for this topic — supplement with your own current search.`
- **Widely-documented technologies rule:** For any session covering a technology with rich independent literature (e.g., MCP, PostgreSQL, TypeScript, Transformer architecture, embeddings, LLMs, REST APIs), at least one source must be the official spec, canonical paper, or a neutral explainer — not the product's own take on that technology. These topics have no excuse for lacking neutral sources.
- Role-specific sources are mandatory in Module 3 (Your Role), Module 5 (Day-in-Life), and any session where the quiz's Q3 asks the learner to apply role judgment.

**Rationale:** A learner studying a product through their job function lens needs to understand the underlying technology independently — not just through the vendor's narrative. A PM learning about MCP from only the InsForge blog learns InsForge's take on MCP, not MCP itself.

---

### Layer 1: Product Intelligence (run first — output drives Layer 2)

**Goal:** Identify the actual AI technologies powering {PRODUCT}.

Run these 3 searches:
```
"{PRODUCT}" AI technology how it works
"{PRODUCT}" engineering architecture machine learning
"{PRODUCT}" AI features technical blog 2024 2025
```

**Synthesize a tech stack map:**
From the search results, identify which AI technologies power {PRODUCT}. Common
categories to look for:
- Large Language Models (which ones? GPT-4, Claude, Llama, custom?)
- RAG (Retrieval-Augmented Generation) — used for search/context retrieval
- Embeddings — used for semantic search, similarity
- Fine-tuning — custom model training on proprietary data
- Agent loops / tool calling — multi-step AI reasoning
- Local model inference — on-device AI
- Multimodal (vision, audio, video)
- Recommendation systems
- Computer vision / OCR

If the tech stack is not publicly documented, use your best understanding based on
the product's features, category, and comparable products. Label these:
`[INFERRED — not confirmed in public sources]`

**Store the identified technologies as a list for Layer 2.**

---

### Layer 2: Technology Content (run per identified technology × role lens)

**Goal:** Find learning material for each technology in the stack, through the
{ROLE} lens.

For each technology identified in Layer 1, run these 2 searches using the
role-specific query pattern:

**Role query patterns:**
- Product Manager: `"{technology}" explained product manager non-technical use case article`
- Software Engineer: `"{technology}" implementation tutorial code example python article`
- UX Designer: `"{technology}" user experience design patterns interaction article`
- Operations / Program Manager: `"{technology}" deployment monitoring production operations article`
- Data Analyst: `"{technology}" metrics evaluation business impact measurement article`

**Plus a general search for each technology:**
`"{technology}" explained {current year}`

**Plus a video search for each technology (Enhancement 1C — ensures video coverage):**
`"{technology}" explained video tutorial youtube 2024 2025`
`"{technology}" {ROLE} case study presentation youtube OR vimeo`

Preferred YouTube channels to look for in video results:
- 3Blue1Brown (math/ML fundamentals)
- Andrej Karpathy (neural networks, LLMs)
- StatQuest with Josh Starmer (ML concepts for non-experts)
- Official product channels (OpenAI, Anthropic, Cursor, Google DeepMind, etc.)
- Conference talks (NeurIPS, ICML, Google I/O, WWDC)

Apply quality filter to results. Note which technologies have good external sources
vs. which need model knowledge supplementation.

---

### Layer 3: Job Function Role Content (run once)

**Goal:** Understand what {ROLE} actually does at an AI product company in the
same category as {PRODUCT}.

Run these 3 searches:
```
"{product category}" "{ROLE}" responsibilities AI 2024 2025 article
"{ROLE}" working with AI engineers collaboration workflow article
"{PRODUCT}" "{ROLE}" job responsibilities (may be sparse — supplement with model knowledge)
```

Where product category = the category of {PRODUCT} (e.g., "AI coding assistant",
"AI search engine", "AI writing tool", "AI design tool").

This feeds Module 3 (job function deep dive) and Module 5 (daily responsibilities).

---

### Layer 4: Competitive Landscape (run once)

**Goal:** Understand {PRODUCT}'s market position and key competitors.

First, identify 2-3 main competitors using model knowledge + Layer 1 results.

Then run these 2 searches:
```
"{PRODUCT}" vs "{Competitor1}" vs "{Competitor2}" comparison 2024 2025
"{PRODUCT}" user feedback reviews strengths weaknesses
```

This feeds Module 2 (competitive landscape).

---

### Research Summary (internal — do not print to user yet)

After all layers, assess coverage:

| Category | External Sources Found | Quality |
|---|---|---|
| Tech stack | N sources | Good / Sparse / None |
| Technology learning material | N sources | Good / Sparse / None |
| Role responsibilities | N sources | Good / Sparse / None |
| Competitive landscape | N sources | Good / Sparse / None |

**Determine banner status:**
- If any module has zero external sources → show LIMITED EXTERNAL SOURCES banner
- If all modules have ≥ 2 external sources → no banner needed
- If WebSearch was unavailable → show NO LIVE SEARCH banner

---

## Step 3.5: Combined Link Validation + Content Skimming Pass (Enhancements 1B + 2)

**Check browse binary availability first:**

```bash
B=$(which browse 2>/dev/null)
```

If `$B` is empty (browse binary not installed):
- Skip this entire step
- All sources proceed to Step 4 based on title+snippet only
- Tag every source in the curriculum with `⚠️ [content unverified — browse unavailable]`
- Note: Enhancement 2 text skimming and YouTube transcripts also degrade gracefully

If `$B` is set, proceed with the combined pass below.

**Time budget — set a 90-second hard wall:**

Start a timer. If the combined pass exceeds 90 seconds, trigger the degradation order:
1. Drop YouTube transcript extraction → description-only scoring (saves ~20-30 sec)
2. Drop index-page recovery → immediately mark [UNVERIFIABLE] (saves ~10 sec per miss)
3. Drop content skimming for text → title+snippet fallback (saves ~30 sec)

**Combined pass — run ONCE per candidate source URL:**

For each candidate source URL collected across all 4 layers (up to ~45 URLs total — budget
increased to support sufficient sources per session across 13 sessions, after deduplication and
filtering; target ~3–5 verified sources per session in the final curriculum):

**Step A — HTTP liveness check:**
```bash
curl -sI --max-time 5 {url} -o /dev/null -w "%{http_code} %{redirect_url}"
```
- If 4xx/5xx: DEAD — remove from list, log `⚠️ [dead link — {status code}]`
- If 404/410 specifically: DEAD — remove immediately
- If 403 Forbidden: treat as live-but-gated — tag `⚠️ [may require login]`, keep source
- If 3xx redirect: follow to final URL, re-check the redirected URL
- If HEAD fails with 405/501 (method not allowed): fall back to `curl -r 0-1023 {url}`
  — treat 200 on byte-range GET as live

**Step B — Browse + content extract (single $B goto per URL):**

For each URL that passed Step A:
```
$B goto {url}
```
Per-source timeout: 8 seconds. If `$B goto` exceeds 8 sec:
- Skip Steps B/C/D for this URL
- Keep source based on snippet only
- Tag `⚠️ [content unverified — page timeout]`

**Step C — Index vs Specific page detection:**

After loading the page, ask:
> "Does this page appear to be a **SPECIFIC ARTICLE** or an **INDEX/LISTING PAGE**?
> An index page shows multiple article previews or headlines.
> A specific article has a clear title, author, date, and continuous body text.
> Answer: SPECIFIC or INDEX."

If **SPECIFIC**: record verified page title as canonical source title. Proceed to Step D.

If **INDEX**: trigger recovery flow:
- Run: `site:{domain} {specific article keywords from original query}` (max 10 sec)
- If specific article URL found: update URL, run Steps A-C on new URL
- If not found within 10 sec: mark source as `[UNVERIFIABLE — index page only]`
  and substitute with model knowledge for that section
- Exception: If URL had ≥2 path segments after section prefix AND already passed
  the 1C URL filter, skip recovery — trust the URL specificity.

**Step D — Content quality scoring (Enhancement 2 — text sources):**

For non-YouTube URLs: extract page text
```
$B extract text --selector "article, main, .content, .post-body"
```
If selector extraction fails: use `$B extract text` (full page fallback)

Send first ~500 words to the model:
> "You are evaluating a learning resource for a **{ROLE}** learning **{TECHNOLOGY}**.
> Read this content extract and rate it 1-10 on:
> - Relevance to {TECHNOLOGY} (not just mentions it, actually explains it)
> - Appropriate depth for {ROLE} (not too technical for PM; not too shallow for Eng)
> - Has concrete example, case study, diagram reference, or actionable insight
>
> Output: `SCORE: X/10 | KEEP or SKIP | one-line reason`"

Scoring rules:
- SCORE ≥ 7: include
- SCORE 5-6: include but flag `⚠️ Limited depth — supplement with model knowledge`
- SCORE < 5: skip (unless it's the only source for this module, then keep with flag)
- If > 5 sources score ≥ 7 for a single module: keep top 5 by score.
  Tiebreak: prefer 1 video + ≥ 2 text over all-text.

**Step D — YouTube transcript extraction (Enhancement 2 — video sources):**

When a YouTube URL (youtube.com/watch?v=...) passes Steps A-C:

First check for login gate:
```
$B js "return document.title"
```
If title contains "Sign in" or "Confirm your age": treat as transcript unavailable immediately.
Do not attempt further extraction.

Check page locale:
```
$B js "return document.documentElement.lang"
```
If lang is NOT "en" or starts with "en-": treat as transcript unavailable, fall to description-only.

Otherwise, attempt transcript extraction:
```
$B js "
  const moreBtn = document.querySelector('[aria-label=\"More actions\"]');
  if (moreBtn) moreBtn.click();
"
```
Wait 1 second, then:
```
$B js "
  const segs = document.querySelectorAll('ytd-transcript-segment-renderer');
  const text = Array.from(segs).map(s => s.querySelector('.segment-text')?.textContent).join(' ');
  return text.substring(0, 1500);
"
```

If transcript text is returned (non-empty): run the same relevance+role scoring prompt as
text sources. Tag source as `[Video — transcript verified]` with estimated watch time.

If transcript is empty after two attempts: fall back to description-only.
```
$B js "return document.querySelector('#description')?.textContent?.substring(0, 800)"
```
Score on description. Tag source as `⚠️ Transcript unavailable — scored on description only`.

For non-YouTube video (Vimeo, Loom, conference platforms):
- No transcript extraction — scored on title + description only
- Tag: `⚠️ No transcript available — assessed by description`
- Include if from trusted source (conference channel, official product demo)

If `$B` unavailable for the entire pass:
- Note: `⚠️ Browse binary not available — video assessed by title/description only`

---

## Step 4: Generate the Curriculum

### Learner Profile Injection

Before generating any session content, load the learner profile from Step 0 and apply
the following calibration rules to ALL session content — key concepts, sources summary,
"How this applies to you", "Day summary insight", and quiz questions.

```
LEARNER PROFILE (apply to all session content):
  AI experience: {ai_level_calibrated from profile}
  Daily time: {daily_minutes} minutes (when value is 30, interpret as "30 or more minutes")
  Format: {format from profile}

CONTENT CALIBRATION RULES:

[chat] — Explain every technical term as if the learner has never coded or built software.
  Use real-world analogies (cooking, logistics, finance, hiring). No code snippets.
  "How this applies to you" focuses entirely on business decisions and outcomes.
  Frame 3 (Role Application) in the day summary is especially useful — use it often.

[vibe_coder] — Assume familiarity with AI tools and basic coding concepts (APIs, JSON, functions).
  Use semi-technical language. Include 1–2 short code snippets per session when they
  clarify the concept (pseudocode is fine). "How this applies to you" can reference
  Cursor, GitHub Copilot, or Claude Code workflows.

[builder] — Assume experience building with AI APIs and agents. Use technical vocabulary
  (embeddings, latency, tool calls, RAG pipelines). Include architecture patterns and
  API call examples. "How this applies to you" is systems-thinking and product design.

[deep_technical] — Assume ML/systems engineering background. Include model internals,
  optimization tradeoffs, and infrastructure considerations. Skip foundational analogies.
  Go straight to mechanisms, tradeoffs, and implementation patterns.

[daily_minutes: 10] — Keep session content tight: one key concept explained well, not three
  shallowly. Drop secondary examples and tangents. Quiz stays full (same number of questions,
  same difficulty — only narrative sections shrink).

[daily_minutes: 20] — Standard density. Full "How this applies to you" section, full examples.

[daily_minutes: 30] — Add bonus depth: "going further" pointers using already-researched
  sources, edge cases, architecture diagrams (text-based). Longer "How this applies to you."

[format: text] — No code blocks in any session. All technical concepts explained in prose
  and analogies only.
  ROLE EXCEPTION: Software Engineer and Data Analyst roles always include at least 1 code
  snippet or pseudocode block per session regardless of this setting — these roles require
  code to teach the concept at all. Format preference controls optional code density, not
  structurally required content.

[format: mixed] — Code blocks when they meaningfully clarify a concept. Max 1 per session.

[format: technical] — Code blocks and architecture patterns encouraged throughout.

TIME-FORMAT PRECEDENCE: Time budget takes precedence over format on content volume.
A [technical] format with [10 min/day] still caps narrative length — keep code snippets
short, drop secondary examples. Format controls what types appear; time controls volume.
```

Write the full curriculum document following the structure below exactly.

### Banners (show at top if applicable)

**If limited external sources:**
```
> ⚠️ **LIMITED EXTERNAL SOURCES**
> This curriculum was generated with limited or no verified external sources for some
> sections. Content marked **[Model Knowledge]** reflects the AI model's training data
> and may not reflect the latest developments. Cross-check key technical claims before
> relying on them for work decisions.
```

**If no WebSearch available:**
```
> ⚠️ **NO LIVE WEB SEARCH**
> This curriculum was generated from model training data only — no live web research
> was performed. Verify currency of information, especially for fast-moving areas.
```

---

### Document Header

```markdown
# {PRODUCT} — AI Learning Curriculum for {ROLE}

**Generated:** {current date}
**Product:** {PRODUCT}
**Your role:** {ROLE}
**Total learning time:** ~{N} hours across 15 sessions (15–20 min each)
**Sessions:** 5 modules × 3 sessions + capstone

---

## Why {PRODUCT}?

{2-3 sentences explaining why this product is a great anchor for learning AI.
What makes it interesting technically? What problem does it solve? Why does a
{ROLE} care about it?}

---

## Tech Stack at a Glance

Technologies powering {PRODUCT}:

| Technology | Confidence | What it does in {PRODUCT} |
|---|---|---|
| {tech 1} | Confirmed / [INFERRED] | {one-line explanation} |
| {tech 2} | Confirmed / [INFERRED] | {one-line explanation} |
| ... | | |

*Technologies labeled [INFERRED] are based on product behavior and comparable
systems — not confirmed in public documentation.*

---

## Competitive Snapshot

| | {PRODUCT} | {Competitor 1} | {Competitor 2} |
|---|---|---|---|
| Core AI strength | | | |
| Key differentiator | | | |
| Main weakness | | | |
| Pricing model | | | |

*Source: {citation or [Model Knowledge]}*

---
```

---

### Module Structure

Generate all 5 modules using the session template below. If research was sparse
and fewer than 5 modules can be meaningfully populated, emit 3 modules minimum
(renumber as Module 1–3, skip Module 4 and 5 rather than leaving them empty).

---

### Day Summary Frame Spec

For EVERY session (Sessions 1–13), generate a `session_insight` — a 2–3 sentence block
that appears in the day-summary box at the top of the day's HTML file.

**Pick ONE frame per session based on the session content.** Replace every placeholder
with specific content — product name, mechanism names, role actions, decisions. The output
should read as a standalone sentence or two that would make someone say "I didn't know that"
or "that changes how I'd think about this."

**Three frames:**

- **FRAME 1 — Tech Highlight** (use when the session introduces a core technical concept):
  "{PRODUCT} achieves {X} by {non-obvious mechanism} — instead of {conventional approach},
  it {does Y}. In this session, you'll see exactly how this works."

- **FRAME 2 — Product Insight** (use when the session reveals a market or design decision):
  "Most {product category} tools {do X the standard way}. {PRODUCT} made a deliberate
  choice to {do Y instead} because {specific reason}. This session explains why that matters."

- **FRAME 3 — Role Application** (use when the session has a direct job-function impact):
  "As a {ROLE}, the key takeaway from this session is: {specific action or decision you can
  make differently}. Before reading: {product/feature} means {concrete change}."

**Distribution rule:** Across the 15 sessions, use each frame approximately 5 times (±2).
Do not use the same frame more than 3 consecutive sessions.

---

### Session Template

Use this exact format for EVERY session block:

```markdown
### Session {N}: {Title} ⏱ {X} min

**Day summary insight (pick one frame from the Day Summary Frame Spec above):**
{session_insight — 2–3 sentences using FRAME 1, 2, or 3. Replace ALL placeholders with
specific content. This feeds directly into the day-summary box in the HTML output.}

**What you'll learn:** {One sentence describing the core concept.}

**Key concepts:**
- **{Concept 1}:** {One-sentence plain-English definition}
- **{Concept 2}:** {One-sentence plain-English definition}
- **{Concept 3}:** {One-sentence plain-English definition}

**Sources:**
- [{Title}]({URL}) — {platform}, {X} min — {one-line summary of why useful}
- [{Title}]({URL}) — {platform}, {X} min — {one-line summary}

> **[Model Knowledge]** {Supplemental concept summary when external sources are
> sparse. Label clearly.} *— generated from model training data, not a verified
> external source*

**How this applies to you as a {ROLE}:**

**Current state (without {PRODUCT}):**
1. {Manual or status-quo step 1} — ~{X} min
2. {Manual or status-quo step 2} — ~{X} min
3. {Manual or status-quo step 3} — ~{X} min
*Total: ~{total time}; requires {who/what skill is needed}*

**With {PRODUCT}:**
{1-2 sentences — what changes, what step is eliminated or transformed, what the outcome is}

**What this means for you as {ROLE}:**
{Role-specific takeaway: what decision this enables, what you'd measure, what you'd ask in
a sprint review, what you'd design differently — be concrete and specific to this session's concept}

*Language calibration: PM/Ops/UX → plain English, no code, business impact focus, explain as
to a smart non-technical person. SWE/Data → technical terms, API references, code patterns OK.
If {PRODUCT}'s specific workflow is unconfirmed by research: label examples as
[typical for products in this category] rather than stating them as fact.*

---
#### ✅ Session {N} Quiz

**Q1 (Multiple Choice):** {Scenario stem using role lens — see Role Lens Spec below}

- A) {option}
- B) {option}
- C) {option}
- D) {option}

<details>
<summary>Show Answer</summary>

**Correct: {letter}**

{2-3 sentences explaining why {letter} is right, AND why each wrong option fails.
Be specific about the mistake each wrong answer represents.}

</details>

---

**Q2 (Multiple Choice):** {Second scenario — different focus area from Q1}

- A) {option}
- B) {option}
- C) {option}
- D) {option}

<details>
<summary>Show Answer</summary>

**Correct: {letter}** — {explanation}

</details>

---

**Q3 (Open-ended — reflect and write):**

{Open-ended prompt using role lens — see Role Lens Spec below}

*Your answer:*

> _(Write your answer here)_

*Model answer for self-comparison:*

> {2-3 sentence reference answer. This is what a strong answer looks like — compare
> yours to see what you might have missed or framed differently.}
```

---

### Role Lens Spec — Quiz Question Differentiation

Apply this spec when writing quiz questions. Questions must feel genuinely different
per role — not just job title swapped in.

| Role | Q1/Q2 focus | Wrong answer traps to include | Q3 open-ended framing |
|---|---|---|---|
| Product Manager | Build vs buy decision, prioritization, stakeholder communication, metric selection | Over-indexing on tech complexity; ignoring user impact; picking vanity metrics | "Explain this tradeoff to a non-technical stakeholder in 2-3 sentences." |
| Software Engineer | Debugging, implementation choice, performance tradeoff, system design | Premature optimization; ignoring edge cases; wrong abstraction level | "Walk through how you'd implement or debug this." |
| UX Designer | User-facing behavior, error states, trust signals, interaction patterns | Ignoring empty/error states; over-engineering for rare edge cases; skipping user research | "How would you test whether users understand this AI behavior?" |
| Operations / Program Manager | Rollout planning, risk mitigation, cross-team dependencies, timeline | Skipping pilot phase; ignoring rollback plan; underestimating integration work | "Design a phased rollout plan with at least 2 risk mitigation steps." |
| Data Analyst | Metric definition, data quality, evaluation methodology, bias detection | Vanity metrics; ignoring data quality; confusing correlation with causation | "How would you measure whether this AI feature is actually working?" |

**Example Q1 for "RAG" technology, PM role:**
> You're the Product Manager for {PRODUCT}. Your engineering team is debating whether
> to use RAG or fine-tuning for improving answer quality. The CEO asks you to make the
> call. What factors most influence your decision?
>
> A) Whichever approach gives the highest benchmark score on standard evals
> B) RAG if the knowledge base changes frequently; fine-tuning if the task is narrow and stable
> C) Always fine-tune — it produces more consistent outputs
> D) Ask engineering to implement both and A/B test before deciding

**Correct: B** — RAG is better when data changes frequently (no retraining cost);
fine-tuning is better for narrow, stable tasks where you control the training data.
A is wrong because benchmark scores don't reflect real user value. C is wrong because
fine-tuning is expensive and slow to update. D sounds rigorous but delays a decision
that should be made on first principles, not A/B testing at the architecture level.

---

### Full Module Outline

Generate each module with exactly the sessions shown. Populate content from your
research (Layers 1–4). Use model knowledge to supplement sparse modules.

---

#### Module 1: AI Technology Stack — Learning Days 1–3

*Tech theme: What AI powers {PRODUCT}, and how does it work?*

**Session 1: The Core AI Engine** ⏱ 20 min
- Focus: The primary AI technology (LLM, embedding model, or other) that {PRODUCT} is built on
- Sources (apply diversity rule — as many as needed to learn):
  - 1 neutral: official spec or canonical paper/explainer for the core technology
  - 1 neutral: independent tutorial or conference talk on the technology
  - 1 neutral: third-party blog post covering real-world use of the technology
  - 0–1 product-authoritative: {PRODUCT}'s own blog or docs on this technology (if it adds specific context not covered by neutrals)
  - 0–1 role-specific: {ROLE}-lens article on this technology (from Layer 2 role-query results)
- Quiz: Q1 focuses on understanding what this technology does vs. alternatives; Q3 open-ended on applying this to role

**Session 2: Supporting AI Systems** ⏱ 20 min
- Focus: Secondary technologies (RAG, agents, fine-tuning, local inference, etc.)
- Sources (apply diversity rule — as many as needed to learn):
  - 2–3 neutral: independent coverage of each supporting technology (prefer official docs or canonical explainers)
  - 0–1 product-authoritative: only if {PRODUCT} has a unique take on how it uses these technologies
  - 1 role-specific: Layer 2 role-query result for the most important supporting technology
- Quiz: Q1 focuses on when to use each technology; Q3 on role-specific application

**Session 3: How the AI Stack Fits Together** ⏱ 15 min
- Focus: How the technologies interact at a system level; latency, cost, reliability tradeoffs
- Sources (apply diversity rule — as many as needed to learn):
  - 2 neutral: system design posts or engineering blogs covering the architecture pattern (not specific to {PRODUCT})
  - 1 neutral: tradeoff comparison article (latency vs. accuracy, cost vs. quality, etc.)
  - 0–1 product-authoritative: {PRODUCT}'s engineering blog on its architecture (only if publicly available and specific)
  - 1 role-specific: how a {ROLE} reasons about or communicates these tradeoffs
- Quiz: Q1 focuses on a tradeoff scenario; Q3 on explaining the stack to a stakeholder / debugging a system issue / designing a flow (per role)

---

#### Module 2: Competitive Landscape — Learning Days 4–5

*Theme: Where does {PRODUCT} sit in the market, and why?*

**Session 4: Market Position** ⏱ 20 min
- Focus: Who are the main competitors, how does {PRODUCT} differentiate, what's the moat
- Sources (apply diversity rule — as many as needed to learn):
  - 2–3 neutral: third-party comparisons, analyst takes, or competitor documentation (Layer 4 results)
  - 1 neutral: market category overview from a neutral source (not written by {PRODUCT})
  - 0–1 product-authoritative: {PRODUCT}'s own positioning page or competitive blog post (clearly labeled as vendor perspective)
  - 1 role-specific: how a {ROLE} does competitive analysis in this product category
- Quiz: Q1 focuses on competitive strategy; Q3 on role-specific competitive analysis

**Session 5: User Perspective & Gaps** ⏱ 20 min
- Focus: What users love and complain about; where the product is winning and losing
- Sources (apply diversity rule — as many as needed to learn):
  - 2–3 neutral: user reviews (G2, Reddit, HackerNews, dev community threads), third-party product reviews
  - 1 neutral: benchmark or independent evaluation of {PRODUCT} vs. alternatives
  - 0–1 product-authoritative: customer case study or release note from {PRODUCT} (for grounding)
  - 1 role-specific: how a {ROLE} collects and uses user feedback in product decisions
- Quiz: Q1 focuses on interpreting user feedback; Q3 on what to do about a specific gap

---

#### Module 3: Your Role at This Type of Product — Learning Days 6–8

*Theme: What does a {ROLE} actually do at an AI product like {PRODUCT}?*

**Session 6: Core Responsibilities** ⏱ 20 min
- Focus: Day-to-day responsibilities of a {ROLE} at an AI product company
- Sources (apply diversity rule — as many as needed to learn; weight role-specific heavily for Module 3):
  - 3 role-specific: job descriptions or career guides for {ROLE} at AI-first companies; real practitioner articles about what this role does (Layer 3 results)
  - 1 neutral: research or report on how AI is changing the {ROLE} function
  - 0–1 product-authoritative: {PRODUCT}'s own job posting or team page for this role (only if it reveals unique expectations)
- Quiz: Role lens strongly applied — questions about real decisions this role makes

**Session 7: Cross-Functional Collaboration** ⏱ 20 min
- Focus: How {ROLE} works with ML engineers, designers, PMs, data scientists
- Sources (apply diversity rule — as many as needed to learn):
  - 2–3 role-specific: articles or talks on cross-functional collaboration for {ROLE} in AI product teams (Layer 3 results)
  - 1 neutral: case study or process post on cross-team collaboration at an AI company (not {PRODUCT})
  - 1 neutral: framework or playbook for {ROLE}'s collaboration with technical teammates
- Quiz: Q1 scenario on a cross-team decision; Q3 on navigating a real collaboration challenge

**Session 8: Key Metrics & Success Criteria** ⏱ 20 min
- Focus: How {ROLE} measures success for AI features; what good looks like
- Sources (apply diversity rule — as many as needed to learn):
  - 2–3 role-specific: metric frameworks, dashboards, or benchmarks used by {ROLE} in AI products (Layer 3 results)
  - 1 neutral: canonical reference on evaluation metrics for this type of AI product (e.g., LLM eval, recommendation quality, search relevance)
  - 1 neutral: published post-mortem or case study where metrics drove a product decision
- Quiz: Q1 on distinguishing good metrics from vanity metrics; Q3 on designing a measurement framework

---

#### Module 4: How to Build This — Learning Days 9–11

*Theme: If you were building {PRODUCT} from scratch, how would you do it?*

**Session 9: Architecture & Key Flows** ⏱ 20 min
- Focus: High-level architecture; the 2-3 most important technical flows in {PRODUCT}
- Sources (apply diversity rule — as many as needed to learn):
  - 2 neutral: architecture pattern posts or papers covering the underlying design approach (not {PRODUCT}-specific)
  - 1 neutral: open-source reference implementation or similar product's architecture writeup
  - 0–1 product-authoritative: {PRODUCT}'s own architecture post or technical blog (if it reveals specific implementation detail not available elsewhere)
  - 1 role-specific: how a {ROLE} reads or documents architecture decisions
- Quiz: Role-specific — PM focuses on architecture decisions; Eng on implementation; UX on user flow

**Session 10: Technology Decisions** ⏱ 20 min
- Focus: Why {PRODUCT} likely made the technology choices it did; what the alternatives were
- Sources (apply diversity rule — as many as needed to learn):
  - 2–3 neutral: tradeoff comparison articles for the technology choices made (e.g., "PostgreSQL vs MongoDB for multi-tenant SaaS", "TypeScript vs Go for API layers")
  - 1 neutral: post-mortem or migration story from a company that made a similar technology decision
  - 0–1 product-authoritative: if {PRODUCT} has published a "why we chose X" post, include it — clearly labeled as vendor rationale
- Quiz: Q1 on a build vs buy / make vs use scenario; Q3 on justifying a tech decision

**Session 11: Important Features & Tradeoffs** ⏱ 20 min
- Focus: The 2-3 features that define {PRODUCT}'s AI experience; the engineering/design tradeoffs behind them
- Sources (apply diversity rule — as many as needed to learn):
  - 1–2 product-authoritative: {PRODUCT}'s feature announcement or deep-dive post for each key feature (this is one of the sessions where product-owned content is genuinely the primary reference)
  - 2 neutral: independent coverage of the same features (reviews, developer forum discussions, comparisons)
  - 1 role-specific: how a {ROLE} evaluates or communicates these feature tradeoffs
- Quiz: Q1 on a feature tradeoff; Q3 on designing or evaluating a feature from role perspective

---

#### Module 5: Day-in-the-Life + Capstone — Learning Days 12–15

*Theme: Putting it all together.*

**Session 12: A Day in the Life as {ROLE} at {PRODUCT}** ⏱ 20 min
- Focus: Walk through a realistic workday for a {ROLE} at a company like {PRODUCT}
- Content: Concrete scenario (morning standup → key decisions → afternoon focus work → weekly goals)
- Sources (apply diversity rule — as many as needed to learn; weight role-specific heavily for Module 5):
  - 3 role-specific: "day in the life" articles, interviews, or talks from practitioners in this role at AI product companies (Layer 3 results); career pages or Glassdoor-type posts that reveal real workflows
  - 1 neutral: report or study on how this role is evolving at AI-first companies
  - 0–1 product-authoritative: {PRODUCT} careers page or team blog describing what this role looks like there (only if it adds detail not covered by neutrals)
- Quiz: Q1 on a realistic daily decision; Q3 on prioritizing competing demands

**Session 13: Scenario Simulation** ⏱ 15 min
- Focus: A realistic challenge scenario where you apply everything learned
- Content: Example scenario: "It's Q3. {PRODUCT}'s accuracy dropped 15% after a model update.
  As {ROLE}, what do you do in the first 48 hours?"
- Sources (apply diversity rule — as many as needed to learn):
  - 2–3 neutral: post-mortems, incident reports, or case studies where a {ROLE} had to respond to a similar product challenge at an AI company
  - 1–2 role-specific: frameworks or playbooks for crisis response, root cause analysis, or cross-functional escalation for this role
- Quiz: 2 MC questions on the scenario; Q3 is a structured response to the scenario

**Capstone Quiz** ⏱ 30 min

*Spans all 5 modules. 5 MC + 2 open-ended.*

**Instructions:** Work through these without looking back at the curriculum. Then
check your answers. This tells you what stuck and what needs review.

{Generate 5 MC questions covering one concept from each module, and 2 open-ended
questions requiring synthesis across multiple modules. Use the role lens spec for
all questions. Each MC question should have a `<details>` answer block.}

---

## Step 5: Write Output Files

### Write the curriculum file

```bash
CURRICULUM_FILE="$LEARNING_DIR/{PRODUCT_SLUG}-{ROLE_SLUG}-curriculum.md"
```

Write the full curriculum document generated in Step 4 to this file.

Tell the user:
> ✅ **Curriculum saved to:** `{resolved path}`
>
> Open this file in any markdown reader. Sessions are 15–20 min each.
> Work through one session at a time — don't rush.

### Write the quiz results file (blank template for tracking)

```bash
QUIZ_FILE="$LEARNING_DIR/quiz-{PRODUCT_SLUG}-{ROLE_SLUG}-{TIMESTAMP}.md"
```

Write a blank quiz tracking file:

```markdown
# Quiz Tracker — {PRODUCT} ({ROLE})
Started: {current date}

## Instructions
After completing each session quiz, record your results here.
For MC questions: mark ✅ correct or ❌ incorrect.
For open-ended questions: rate your answer 1-5 and note what you missed.

## Session Results

| Session | Q1 MC | Q2 MC | Q3 Open-ended | Notes |
|---------|-------|-------|---------------|-------|
| Session 1 | | | /5 | |
| Session 2 | | | /5 | |
| Session 3 | | | /5 | |
| Session 4 | | | /5 | |
| Session 5 | | | /5 | |
| Session 6 | | | /5 | |
| Session 7 | | | /5 | |
| Session 8 | | | /5 | |
| Session 9 | | | /5 | |
| Session 10 | | | /5 | |
| Session 11 | | | /5 | |
| Session 12 | | | /5 | |
| Session 13 | | | /5 | |
| Capstone MC 1 | | | — | |
| Capstone MC 2 | | | — | |
| Capstone MC 3 | | | — | |
| Capstone MC 4 | | | — | |
| Capstone MC 5 | | | — | |
| Capstone OE 1 | — | — | /5 | |
| Capstone OE 2 | — | — | /5 | |

## Weak Areas (fill in after capstone)
{Topics where you got MC wrong or rated open-ended < 3}

## Next: What to Review
{Sessions to re-read before moving to V2 curriculum}
```

Tell the user:
> 📊 **Quiz tracker saved to:** `{resolved path}`
>
> Fill this in after each session to track your progress.

### Generate HTML files

After writing the `.md` files, generate all HTML output. This step produces **17 files**:
15 per-day HTML files (the primary delivery artifact), 1 full curriculum reference HTML,
and 1 manifest JSON for the scheduler.

---

#### CSS template (inline into EVERY HTML file generated)

```css
*, *::before, *::after { box-sizing: border-box; }
body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 18px; line-height: 1.7; max-width: 700px;
  margin: 0 auto; padding: 16px; color: #1a1a1a; background: #fff;
}
h1 { font-size: 1.8em; margin-top: 1.5em; }
h2 { font-size: 1.4em; margin-top: 2em; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.3em; }
h3 { font-size: 1.15em; margin-top: 1.5em; }
h4 { font-size: 1em; margin-top: 1.2em; }
a { color: #2563eb; } a:visited { color: #7c3aed; }
blockquote {
  border-left: 4px solid #e5e7eb; margin: 1em 0; padding: 0.5em 1em;
  color: #555; background: #f9fafb; border-radius: 0 4px 4px 0;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9em; }
th, td { border: 1px solid #e5e7eb; padding: 8px 12px; text-align: left; }
th { background: #f3f4f6; font-weight: 600; }
pre { background: #f3f4f6; padding: 16px; border-radius: 6px; overflow-x: auto; font-size: 0.85em; }
code { font-family: "SF Mono","Fira Code",Consolas,monospace; background: #f3f4f6; padding: 2px 5px; border-radius: 3px; font-size: 0.85em; }
pre code { background: none; padding: 0; }
details { border: 1px solid #e5e7eb; border-radius: 6px; padding: 8px 12px; margin: 8px 0; }
summary { cursor: pointer; font-weight: 600; color: #2563eb; }
details[open] summary { margin-bottom: 8px; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 2em 0; }
ul, ol { padding-left: 1.5em; } li { margin-bottom: 0.3em; }
nav#top-nav {
  position: sticky; top: 0; background: #fff; border-bottom: 2px solid #e5e7eb;
  padding: 8px 0; display: flex; gap: 12px; flex-wrap: wrap; z-index: 100; margin-bottom: 24px;
}
nav#top-nav a { text-decoration: none; font-size: 0.85em; font-weight: 600; color: #374151; white-space: nowrap; }
nav#top-nav a:hover { color: #2563eb; }
/* Quiz / answer reveal */
.day-summary { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 14px 18px; margin-bottom: 24px; }
.day-summary strong { font-size: 1.1em; display: block; margin-bottom: 6px; }
.session-insight { font-size: 0.97em; line-height: 1.6; color: #374151; margin: 8px 0 12px 0; padding: 10px 14px; background: rgba(255,255,255,0.6); border-left: 3px solid #2563eb; border-radius: 0 6px 6px 0; }
#quiz-section { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 16px; margin: 24px 0; }
#answer-section { background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 16px; margin: 24px 0; }
.options { list-style: none; padding: 0; margin: 8px 0 12px 0; }
.options li { padding: 6px 10px; border-radius: 4px; }
.options li:hover { background: #f3f4f6; }
.done-btn { background: #2563eb; color: #fff; border: none; padding: 10px 22px; border-radius: 6px; cursor: pointer; font-size: 1em; margin-top: 8px; }
.done-btn:hover { background: #1d4ed8; }
#q3-answer { width: 100%; min-height: 100px; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 0.95em; margin-top: 8px; font-family: inherit; resize: vertical; }
.complete-banner { background: #f0fdf4; border: 2px solid #4ade80; border-radius: 8px; padding: 20px; margin: 24px 0; text-align: center; font-size: 1.1em; }
@media (prefers-color-scheme: dark) {
  body { color: #e5e7eb; background: #111827; }
  h2 { border-color: #374151; }
  blockquote { border-color: #374151; color: #9ca3af; background: #1f2937; }
  th, td { border-color: #374151; } th { background: #1f2937; }
  pre, code { background: #1f2937; }
  details { border-color: #374151; }
  hr { border-color: #374151; }
  nav#top-nav { background: #111827; border-color: #374151; }
  nav#top-nav a { color: #9ca3af; }
  a { color: #60a5fa; } a:visited { color: #a78bfa; }
  .day-summary { background: #1e3a5f; border-color: #3b82f6; }
  .session-insight { color: #d1d5db; background: rgba(0,0,0,0.2); border-left-color: #3b82f6; }
  #quiz-section { background: #1e3a5f; border-color: #3b82f6; }
  #answer-section { background: #14532d; border-color: #4ade80; }
  .options li:hover { background: #1f2937; }
  .done-btn { background: #3b82f6; }
  .done-btn:hover { background: #2563eb; }
  #q3-answer { background: #1f2937; border-color: #374151; color: #e5e7eb; }
  .complete-banner { background: #14532d; border-color: #4ade80; }
}
@media print { nav#top-nav { display: none; } body { font-size: 12pt; max-width: 100%; padding: 0; } a { color: #000; } }
@media (max-width: 480px) { body { font-size: 16px; padding: 12px; } h1 { font-size: 1.5em; } table { font-size: 0.8em; } }
```

---

#### Per-day HTML files (primary delivery artifact)

Generate all 15 day files sequentially. Write each file before generating the next.
The scheduler delivers one file per day.

**File naming:**
```bash
DAY_FILE="$LEARNING_DIR/{PRODUCT_SLUG}-{ROLE_SLUG}-day-{NN}.html"
# NN is zero-padded: 01, 02, ... 15
```

**Day-to-session mapping (follow exactly):**

| File | Content |
|---|---|
| day-01.html | Curriculum header + Session 1 + Quiz 1 |
| day-02.html | Session 2 + Quiz 2 |
| day-03.html | Session 3 + Quiz 3 |
| day-04.html | Session 4 + Quiz 4 |
| day-05.html | Session 5 + Quiz 5 |
| day-06.html | Session 6 + Quiz 6 |
| day-07.html | Session 7 + Quiz 7 |
| day-08.html | Session 8 + Quiz 8 |
| day-09.html | Session 9 + Quiz 9 |
| day-10.html | Session 10 + Quiz 10 |
| day-11.html | Session 11 + Quiz 11 |
| day-12.html | Session 12 + Quiz 12 |
| day-13.html | Session 13 + Quiz 13 |
| day-14.html | Capstone Quiz (5 MC questions, answers hidden) |
| day-15.html | Capstone Quiz answers + Course Complete banner |

**HTML shell for every per-day file:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{PRODUCT} — Day {N} of 15 — {Session Title}</title>
<style>
{CSS TEMPLATE}
</style>
</head>
<body>
<header style="border-bottom:2px solid #e5e7eb;padding:10px 0;margin-bottom:20px;font-size:0.9em;color:#6b7280;">
  {PRODUCT} Learning &nbsp;·&nbsp; <strong>Day {N} of 15</strong>
</header>
<main>
{DAY_CONTENT}
</main>
<script>
window.addEventListener('load', function() {
  var saved = sessionStorage.getItem('q3-answer');
  if (saved) { var el = document.getElementById('q3-answer'); if (el) el.value = saved; }
});
document.addEventListener('DOMContentLoaded', function() {
  var q3 = document.getElementById('q3-answer');
  if (q3) q3.addEventListener('input', function() { sessionStorage.setItem('q3-answer', this.value); });
});
function revealAnswers() {
  var quiz = document.getElementById('quiz-section');
  var ans = document.getElementById('answer-section');
  if (quiz) quiz.style.display = 'none';
  if (ans) { ans.style.display = 'block'; ans.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  sessionStorage.removeItem('q3-answer');
}
</script>
</body>
</html>
```

**{DAY_CONTENT} structure for each day:**

*Day 01 only — curriculum header before summary box:*
```html
<div class="curriculum-header">
  <h1>{PRODUCT} — AI Learning Curriculum for {ROLE}</h1>
  <p>Generated: {date} &nbsp;·&nbsp; 13 sessions + capstone &nbsp;·&nbsp; ~7–10 hours</p>
  <hr>
  <h2>Why {PRODUCT}?</h2>
  <p>{why product paragraph}</p>
  <h2>Tech Stack at a Glance</h2>
  {tech stack table — convert markdown table to HTML}
  <h2>Competitive Snapshot</h2>
  {competitive table — convert markdown table to HTML}
  <hr>
</div>
```

*Every day (01–15) — curriculum map table (appears above the day-summary box):*

Render a 3-column table showing all 5 modules, their day ranges, and a **Focus** line
derived from the actual session content — never hardcoded. Highlight the row whose
day range contains the current day.

**Focus derivation rule:** For each module, use up to 2 sentences derived from
`what_learn` fields — never concept names, never hardcoded strings, no truncation.
- Sentence 1: the `what_learn` of the **first session** in the module (sets the arc entry).
- Sentence 2: the `what_learn` of the **last session** in the module (sets the arc payoff).
- If the module has only one session, use that session's `what_learn` alone.
- Capstone days without `what_learn` are skipped; use the last regular session's field.
Table cells wrap naturally — do NOT apply any character truncation.

```html
<table style="font-size:.82em;margin:0 0 20px 0;">
<thead><tr><th>Module</th><th>Days</th><th>Focus</th></tr></thead>
<tbody>
  <!-- current module row has style="background:#dbeafe;font-weight:600;" and a blue dot indicator -->
  <!-- inactive rows have no background style -->
  <tr style="background:#dbeafe;font-weight:600;">
    <td><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#2563eb;margin-right:6px;vertical-align:middle;"></span>Module 1: AI Technology Stack</td>
    <td style="white-space:nowrap;">1–3</td>
    <td>{first session what_learn} {last session what_learn}</td>
  </tr>
  <tr><td>Module 2: Competitive Landscape</td><td style="white-space:nowrap;">4–5</td><td>{derived focus}</td></tr>
  <tr><td>Module 3: Your Role as {ROLE}</td><td style="white-space:nowrap;">6–8</td><td>{derived focus}</td></tr>
  <tr><td>Module 4: How to Build This</td><td style="white-space:nowrap;">9–11</td><td>{derived focus}</td></tr>
  <tr><td>Module 5: Day-in-Life + Capstone</td><td style="white-space:nowrap;">12–15</td><td>{derived focus}</td></tr>
</tbody>
</table>
```

*Every day (01–13) — day summary box:*
```html
<div class="day-summary">
  <strong>Day {N} of 15 — {Session Title} ⏱ {X} min</strong>
  <div class="session-insight">{session_insight — the 2–3 sentence framed insight generated
  in the session's "Day summary insight" field in Step 4. Use FRAME 1, 2, or 3 content exactly
  as generated. Do not substitute the generic "What you'll learn" sentence here.}</div>
  <p><em>Key concepts:</em></p>
  <ul>
    <li><strong>{Concept 1}:</strong> {one-line definition}</li>
    <li><strong>{Concept 2}:</strong> {one-line definition}</li>
    <li><strong>{Concept 3}:</strong> {one-line definition}</li>
  </ul>
</div>
```

*Every day (01–13) — session learning content:*
Convert the session's markdown (key concepts, sources, "How this applies to you") to HTML
using the standard markdown→HTML rules. The "How this applies to you" section renders as
plain HTML paragraphs — the Current state list, With {PRODUCT} paragraph, and role takeaway.

*Every day (01–13) — quiz section (questions visible, answers hidden):*
```html
<div id="quiz-section">
  <h4>✅ Session {N} Quiz</h4>

  <p><strong>Q1:</strong> {Q1 scenario text}</p>
  <ul class="options">
    <li>A) {option A}</li>
    <li>B) {option B}</li>
    <li>C) {option C}</li>
    <li>D) {option D}</li>
  </ul>

  <p><strong>Q2:</strong> {Q2 scenario text}</p>
  <ul class="options">
    <li>A) {option A}</li>
    <li>B) {option B}</li>
    <li>C) {option C}</li>
    <li>D) {option D}</li>
  </ul>

  <p><strong>Q3 (Open-ended):</strong> {Q3 prompt}</p>
  <textarea id="q3-answer" placeholder="Write your answer here before revealing the model answer..."></textarea>

  <button class="done-btn" onclick="revealAnswers()">Done for today →</button>
</div>

<div id="answer-section" style="display:none">
  <h4>✅ Answers — Session {N}</h4>
  <p><strong>Q1 — Correct: {letter}</strong><br>{2-3 sentence explanation: why correct + why each wrong answer fails}</p>
  <p><strong>Q2 — Correct: {letter}</strong><br>{explanation}</p>
  <p><strong>Q3 — Model answer:</strong><br>{2-3 sentence reference answer for self-comparison}</p>
</div>
```

*Day 14 — Capstone Quiz Part 1 (5 MC questions, all hidden until Done):*
```html
<div class="day-summary">
  <strong>Day 14 of 15 — Capstone Quiz ⏱ 20 min</strong>
  <p><em>Spans all 5 modules. Work through these without looking back at the curriculum.</em></p>
</div>

<div id="quiz-section">
  <h4>📋 Capstone Quiz — Multiple Choice</h4>
  <p><em>Answer all 5 before clicking Done.</em></p>

  <p><strong>Q1:</strong> {MC covering Module 1}</p>
  <ul class="options">...</ul>

  <p><strong>Q2:</strong> {MC covering Module 2}</p>
  <ul class="options">...</ul>

  <p><strong>Q3:</strong> {MC covering Module 3}</p>
  <ul class="options">...</ul>

  <p><strong>Q4:</strong> {MC covering Module 4}</p>
  <ul class="options">...</ul>

  <p><strong>Q5:</strong> {MC covering Module 5}</p>
  <ul class="options">...</ul>

  <button class="done-btn" onclick="revealAnswers()">Check my answers →</button>
</div>

<div id="answer-section" style="display:none">
  <h4>✅ Capstone MC Answers</h4>
  <p><strong>Q1 — Correct: {letter}</strong><br>{explanation}</p>
  <p><strong>Q2 — Correct: {letter}</strong><br>{explanation}</p>
  <p><strong>Q3 — Correct: {letter}</strong><br>{explanation}</p>
  <p><strong>Q4 — Correct: {letter}</strong><br>{explanation}</p>
  <p><strong>Q5 — Correct: {letter}</strong><br>{explanation}</p>
  <p style="margin-top:16px"><em>Open-ended questions are in Day 15 →</em></p>
</div>
```

*Day 15 — Capstone Quiz Part 2 (2 open-ended + Course Complete):*
```html
<div class="day-summary">
  <strong>Day 15 of 15 — Capstone: Open-Ended Questions ⏱ 15 min</strong>
  <p><em>Two synthesis questions. Write your answers, then reveal model answers.</em></p>
</div>

<div id="quiz-section">
  <h4>📋 Capstone Quiz — Open-Ended</h4>

  <p><strong>OE1:</strong> {Open-ended synthesis question spanning multiple modules}</p>
  <textarea id="q3-answer" placeholder="Write your answer here..."></textarea>

  <p><strong>OE2:</strong> {Second synthesis question}</p>
  <textarea id="oe2-answer" style="width:100%;min-height:100px;padding:10px;border:1px solid #d1d5db;border-radius:4px;font-size:0.95em;margin-top:8px;font-family:inherit;resize:vertical;" placeholder="Write your answer here..."></textarea>

  <button class="done-btn" onclick="revealAnswers()">Reveal model answers →</button>
</div>

<div id="answer-section" style="display:none">
  <h4>✅ Capstone Open-Ended Model Answers</h4>
  <p><strong>OE1 — Model answer:</strong><br>{2-3 sentence reference answer}</p>
  <p><strong>OE2 — Model answer:</strong><br>{2-3 sentence reference answer}</p>

  <div class="complete-banner">
    🎉 <strong>Course complete!</strong><br>
    You've finished all 15 sessions of your {PRODUCT} curriculum as a {ROLE}.<br>
    <small>Review your weak areas in the quiz tracker, then revisit those sessions.</small>
  </div>
</div>
```

After writing each day file, tell the user a brief progress line:
> `✅ day-01.html … day-15.html generated`

(Print one summary line after all 15 are done, not 15 individual messages.)

---

#### Curriculum reference HTML (full scrollable study guide)

```bash
CURRICULUM_HTML="$LEARNING_DIR/{PRODUCT_SLUG}-{ROLE_SLUG}-curriculum.html"
```

This is the same full-curriculum reference as before. Use the standard HTML shell with:
- `PAGE_TITLE`: `{PRODUCT} — AI Learning Curriculum for {ROLE} (Reference)`
- `NAV_LINKS`: one `<a href="#module-{N}">Module {N}</a>` per module (5 links)
- Convert the curriculum markdown to HTML using standard rules
- Quiz answers: keep as `<details>/<summary>` (reference doc — answers always accessible)
- No `revealAnswers()` JS needed (the reference doc uses native `<details>`)

Write to `CURRICULUM_HTML`.

Tell the user:
> 📖 **Curriculum reference HTML saved to:** `{resolved path}`
>
> Full study guide — all 15 sessions in one scrollable page. Use for review.

---

#### Quiz tracker HTML

```bash
QUIZ_HTML="$LEARNING_DIR/quiz-{PRODUCT_SLUG}-{ROLE_SLUG}-{TIMESTAMP}.html"
```

Same quiz tracker as before (unchanged format). Use the HTML shell with:
- `PAGE_TITLE`: `Quiz Tracker — {PRODUCT} ({ROLE})`
- `NAV_LINKS`: `<a href="#top">Top</a>` only
- Convert the quiz tracker markdown to HTML using standard rules

Write to `QUIZ_HTML`.

Tell the user:
> 📊 **Quiz tracker HTML saved to:** `{resolved path}`

---

#### Manifest JSON (scheduler reads this)

```bash
MANIFEST_FILE="$LEARNING_DIR/{PRODUCT_SLUG}-{ROLE_SLUG}-manifest.json"
```

Write this file so the scheduler knows which file to deliver each day:

```json
{
  "product": "{PRODUCT}",
  "role": "{ROLE}",
  "generated": "{ISO 8601 datetime}",
  "start_date": "{YYYY-MM-DD — today's date when curriculum is generated}",
  "total_days": 15,
  "days": [
    { "day": 1,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-01.html", "session": "Session 1: {title}" },
    { "day": 2,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-02.html", "session": "Session 2: {title}" },
    { "day": 3,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-03.html", "session": "Session 3: {title}" },
    { "day": 4,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-04.html", "session": "Session 4: {title}" },
    { "day": 5,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-05.html", "session": "Session 5: {title}" },
    { "day": 6,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-06.html", "session": "Session 6: {title}" },
    { "day": 7,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-07.html", "session": "Session 7: {title}" },
    { "day": 8,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-08.html", "session": "Session 8: {title}" },
    { "day": 9,  "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-09.html", "session": "Session 9: {title}" },
    { "day": 10, "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-10.html", "session": "Session 10: {title}" },
    { "day": 11, "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-11.html", "session": "Session 11: {title}" },
    { "day": 12, "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-12.html", "session": "Session 12: {title}" },
    { "day": 13, "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-13.html", "session": "Session 13: {title}" },
    { "day": 14, "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-14.html", "session": "Capstone Quiz Part 1 (MC)" },
    { "day": 15, "file": "{PRODUCT_SLUG}-{ROLE_SLUG}-day-15.html", "session": "Capstone Quiz Part 2 (OE + Complete)" }
  ]
}
```

Tell the user:
> 📋 **Manifest saved to:** `{resolved path}`
>
> Scheduler reads `days[N-1].file` to deliver today's content.

---

### Step 5.5: Delivery Automation Setup

**Runs on every curriculum generation.** Regenerates `deliver.py` and the launchd plist
with the latest profile settings, then reloads the scheduler. The `.smtp-config.json`
is **never** overwritten (preserves credentials).

Read `delivery_email` and `delivery_time` from the loaded profile. If either is missing,
run Q4 and Q5 now (same questions as Step 0), save to profile, then continue.

#### 5.5a — Generate `deliver.py`

Resolve absolute paths (launchd does not expand `~`):
```bash
DELIVER_SCRIPT="$HOME/.gstack/learning/deliver.py"
PYTHON3_PATH=$(which python3)
```

Write `$DELIVER_SCRIPT` with the following content (substitute `$LEARNING_DIR` as the
resolved absolute path, e.g. `/Users/{username}/.gstack/learning`):

```python
#!/usr/bin/env python3
"""AI Learning daily email delivery script. Run daily by launchd."""
import json, smtplib, sys
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

LEARNING_DIR = Path("{RESOLVED_ABSOLUTE_LEARNING_DIR}")

def load(path):
    return json.loads(Path(path).read_text())

def log(msg):
    # delivery.log = structured JSON; separate from stdout/stderr captured by launchd
    log_path = LEARNING_DIR / "delivery.log"
    entry = json.dumps({"ts": datetime.now().isoformat(), "msg": msg})
    with log_path.open("a") as f:
        f.write(entry + "\n")

try:
    smtp_config_path = LEARNING_DIR / ".smtp-config.json"
    if not smtp_config_path.exists():
        msg = "SMTP config not found. Fill in ~/.gstack/learning/.smtp-config.json first."
        print(msg); log(msg); sys.exit(1)

    config = load(smtp_config_path)
    profile = load(LEARNING_DIR / ".user-profile.json")

    if "delivery_email" not in profile:
        msg = "delivery_email not set in profile. Run 'update delivery' to configure."
        print(msg); log(msg); sys.exit(1)

    # Most recently modified manifest — policy for multiple curricula: deliver the newest
    manifests = sorted(LEARNING_DIR.glob("*-manifest.json"),
                       key=lambda p: p.stat().st_mtime, reverse=True)
    if not manifests:
        msg = "No manifest found. Run the AI learning skill first."
        print(msg); log(msg); sys.exit(1)

    manifest = load(manifests[0])

    # Fallback: if manifest lacks start_date (legacy), use generated date
    raw_start = manifest.get("start_date") or manifest.get("generated", "")[:10]
    start_date = date.fromisoformat(raw_start)
    today = date.today()
    day_number = (today - start_date).days + 1

    if day_number < 1:
        print(f"Curriculum starts on {start_date} — nothing to send yet."); sys.exit(0)
    if day_number > manifest["total_days"]:
        print(f"Curriculum complete ({manifest['total_days']} days). No more content."); sys.exit(0)

    day_entry = manifest["days"][day_number - 1]
    html_file = LEARNING_DIR / day_entry["file"]

    if not html_file.exists():
        msg = f"Content file not found: {html_file}"
        print(msg); log(msg); sys.exit(1)

    html_content = html_file.read_text()

    # Build email with plain-text fallback (for Outlook / strict filters)
    subject = (
        f"📚 Day {day_number}/{manifest['total_days']}: "
        f"{manifest['product']} × {manifest['role']} — {day_entry['session']}"
    )
    text_body = (
        f"Day {day_number}/{manifest['total_days']}: {day_entry['session']}\n\n"
        f"Open the HTML version for the full session content.\nFile: {html_file}"
    )
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config["smtp_user"]
    msg["To"] = profile["delivery_email"]
    msg.attach(MIMEText(text_body, "plain"))    # plain first (lower preference)
    msg.attach(MIMEText(html_content, "html"))  # html second (higher preference)

    # Branch on smtp_use_ssl for port-465 providers vs STARTTLS (port 587, default)
    use_ssl = config.get("smtp_use_ssl", False)
    if use_ssl:
        with smtplib.SMTP_SSL(config["smtp_host"], config["smtp_port"]) as smtp:
            smtp.login(config["smtp_user"], config["smtp_password"])
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as smtp:
            smtp.starttls()
            smtp.login(config["smtp_user"], config["smtp_password"])
            smtp.send_message(msg)

    result = f"Day {day_number} sent to {profile['delivery_email']}"
    print(result); log(result)

except Exception as e:
    error_msg = f"Delivery failed: {e}"
    print(error_msg); log(error_msg); sys.exit(1)
```

Make executable:
```bash
chmod +x "$DELIVER_SCRIPT"
```

> **Note:** `deliver.py` is regenerated on every curriculum run. Do not hand-edit it;
> put customizations in `.smtp-config.json` or say "update delivery" to change settings.

#### 5.5b — Generate `.smtp-config.json` template

Write **only if the file does not already exist** (never overwrite credentials):

```bash
SMTP_CONFIG="$HOME/.gstack/learning/.smtp-config.json"
```

```json
{
  "_instructions": "Fill in your SMTP credentials. For Gmail use an App Password (myaccount.google.com/apppasswords). Delete this _instructions key when done. Set smtp_use_ssl to true for port-465 providers (e.g. some Outlook/Exchange servers). Default smtp.gmail.com uses port 587 with STARTTLS.",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_use_ssl": false,
  "smtp_user": "YOUR_GMAIL@gmail.com",
  "smtp_password": "YOUR_APP_PASSWORD"
}
```

Add `.smtp-config.json` to `$HOME/.gstack/learning/.gitignore` (create if missing):
```bash
echo ".smtp-config.json" >> "$HOME/.gstack/learning/.gitignore"
```

#### 5.5c — Generate and load launchd plist

Parse `delivery_time` (format `"HH:MM"`) to extract `HOUR` and `MINUTE` integers.
Resolve all paths to absolute (launchd does NOT expand `~` or `$HOME`):

```bash
PLIST_PATH="$HOME/Library/LaunchAgents/com.gstack.ai-learning.plist"
ABS_DELIVER="$HOME/.gstack/learning/deliver.py"
ABS_STDOUT="$HOME/.gstack/learning/delivery.stdout.log"
ABS_STDERR="$HOME/.gstack/learning/delivery.stderr.log"
```

Write `$PLIST_PATH`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.gstack.ai-learning</string>
    <key>ProgramArguments</key>
    <array>
        <string>{RESOLVED_PYTHON3_PATH}</string>
        <string>{RESOLVED_ABS_DELIVER_PATH}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{HOUR}</integer>
        <key>Minute</key>
        <integer>{MINUTE}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{RESOLVED_ABS_STDOUT}</string>
    <key>StandardErrorPath</key>
    <string>{RESOLVED_ABS_STDERR}</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

Load (or reload) the plist:
```bash
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"
LOAD_EXIT=$?
```

- If `LOAD_EXIT == 0`: print `✅ Scheduler loaded — launchd will deliver daily at {delivery_time}.`
- If `LOAD_EXIT != 0`: print the following warning (do NOT block):
  ```
  ⚠️  Scheduler NOT loaded. Run this manually:
    launchctl load ~/Library/LaunchAgents/com.gstack.ai-learning.plist
  ```

#### 5.5d — Offer to send Day 1 now

After loading the plist (success or failure), ask the user:
> "Want me to send Day 1 now to verify delivery works?
> A) Yes — send now  B) No — I'll test later"

If A: run `python3 "$DELIVER_SCRIPT"` and report the result:
- On success: "✅ Day 1 sent to {delivery_email}. Check your inbox!"
- On failure: print the error and remind the user to fill in `.smtp-config.json` first.

---

### Print delivery block

After Step 5.5, print this personalized block (substituting actual values):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📬 DAILY DELIVERY CONFIGURED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Delivery script:   {ABS_DELIVER}
✅ Scheduler:         com.gstack.ai-learning (launchd)
✅ Sends to:          {delivery_email}
✅ Daily at:          {delivery_time}
✅ Curriculum:        {PRODUCT} × {ROLE} (most recently generated)

⚠️  ONE-TIME SETUP REQUIRED — fill in your SMTP credentials:

  1. Open: {SMTP_CONFIG}
  2. Replace smtp_user and smtp_password

  Gmail users: Get an App Password at
  → myaccount.google.com/apppasswords
  (Requires 2-Step Verification to be ON)

Test delivery anytime:
  python3 {ABS_DELIVER}

Change delivery time or email:
  Say "update delivery"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If `.smtp-config.json` already exists and does NOT contain `_instructions` (i.e., the user
has already configured it), omit the ⚠️ ONE-TIME SETUP section.

---

## Step 6: Final Summary to User

Print a summary in this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {PRODUCT} AI Learning Curriculum — {ROLE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 CURRICULUM
   File: {curriculum filename}.md
   HTML: {curriculum filename}.html  ← open on phone/tablet
   Path: {full path}
   Sessions: 13 sessions + capstone (Days 14–15)
   Total time: ~7–10 hours across 15 days

🧠 TECH STACK IDENTIFIED
   {list each technology found, one per line, with confidence level}

📊 QUIZ TRACKER
   File: {quiz filename}.md
   HTML: {quiz filename}.html  ← mobile-friendly tracker
   Path: {full path}

🗺️ YOUR LEARNING PATH
   Module 1 (Days 1–3):   AI Technology Stack
   Module 2 (Days 4–5):   Competitive Landscape
   Module 3 (Days 6–8):   Your Role as {ROLE}
   Module 4 (Days 9–11):  How to Build This
   Module 5 (Days 12–15): Day-in-the-Life + Capstone

💡 HOW TO USE THIS
   1. The scheduler delivers one day file per day to your device
      OR manually AirDrop day-01.html to start, then request next days
   2. Do ONE session per day — 15–20 min
   3. Answer quiz questions, then tap "Done for today →" to reveal answers
   4. Log your scores in the quiz tracker
   5. After the capstone (Days 14–15), note your weak areas and review those sessions
   6. To take a quiz interactively: tell the bot "quiz me on session N"

⚠️  SOURCE NOTES
   {If model knowledge was used: "Some sections use model knowledge — labeled [Model Knowledge]
   throughout. Cross-check technical claims before using in work decisions."}
   {If all external sources: "All content sourced from verified external resources."}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 7: Interactive Quiz Mode (OpenClaw / Chat Context)

**This step runs ONLY in response to a user message in a chat session.**
Skip this step entirely during curriculum generation (Steps 1–6). Never trigger it automatically.

**Trigger phrases:** "I finished today's material", "quiz me", "quiz me on session N",
"let's do the quiz", "I'm ready for the quiz", "quiz session N"

### Identify which session to quiz

Resolution order:
1. User specifies a session number ("quiz me on session 3") → use Session 3
2. User says "today's quiz" or "quiz me" without a number → ask: "Which session number? (1–13, or 'capstone')"
3. Look for the curriculum markdown file at `~/.gstack/learning/{any}-curriculum.md` → read Q1/Q2/Q3 from that file for the requested session
4. No file found → ask: "Could you paste the quiz section from your day HTML file? I'll run it interactively from there."

### Interactive quiz loop

Once the session is identified and quiz content is loaded:

**Step a — Present Q1:**
Show the full Q1 question text and all four options (A/B/C/D). End with: "Take a moment to think before answering."
Wait for user response.

**Step b — Evaluate Q1:**
Accept any variation: "B", "I think B", "answer B", "B because…", "probably B".
- Correct: "✅ Correct! {2-sentence explanation of WHY it's right + what the wrong answers represent}"
- Incorrect: "❌ Not quite — you picked {X}. {Why X is wrong}. The correct answer is {letter}: {explanation}"

**Step c — Present Q2:**
Same format as Q1. Wait for response. Evaluate same way.

**Step d — Present Q3 (open-ended):**
Show the Q3 prompt. Say: "Write your answer — don't worry about being perfect."
Wait for user response.

Evaluate Q3 with calibrated feedback:
- Quote 1-2 things from their answer that were correct (quote their exact words back)
- Name 1-2 things the model answer covers that they missed (be specific, not generic)
- Rate overall: **Strong** (covers concept + role-specific application) / **Good** (covers concept, generic application) / **Needs review** (misses core concept or contradicts it)
- Show the model reference answer in full for comparison

**Step e — Session score summary:**
```
Session {N} complete ✅
Q1: {✅ Correct / ❌ Incorrect}
Q2: {✅ Correct / ❌ Incorrect}
Q3: {Strong / Good / Needs review}

{If Q1 or Q2 wrong → "Suggested: Re-read the Key Concepts section of Session {N}"}
{If Q3 needs review → "Suggested: Re-read the 'How this applies to you' section of Session {N}"}
{If all correct → "Great session! You're ready for Day {N+1}."}
```

### Capstone quiz mode

If user says "capstone quiz" or "quiz me on the capstone":
- Run Q1–Q5 (MC) in sequence, evaluating each
- Then run OE1 and OE2 (open-ended)
- Score summary at end: "Capstone complete: {X}/5 MC correct, OE1: {rating}, OE2: {rating}"
- If < 3 MC correct: "Consider reviewing the sessions for the modules you missed before marking the curriculum done."

---

## Error Handling

**If WebSearch returns no results for any layer:**
- Continue with model knowledge for that layer
- Mark all model-generated content as `[Model Knowledge]`
- Show the LIMITED EXTERNAL SOURCES banner

**If the product is very obscure (< 3 external sources globally):**
- Do NOT abort
- Use model knowledge for all content
- Add a note: "Note: {PRODUCT} has limited public documentation. This curriculum
  is based primarily on model knowledge about comparable products and public signals
  (job postings, product demos, user reviews). Label: [Model Knowledge]."

**If `~/.gstack/learning/` cannot be created:**
- Use current working directory as fallback
- Print clearly: "Note: Using current directory for output (could not write to ~/.gstack/learning/)"

**If the product name is ambiguous (e.g., "AI" or "Google"):**
- Ask for clarification: "Could you be more specific? For example: 'Google Gemini',
  'Google Search AI Overview', or 'Google Vertex AI'?"

---

## V3 Roadmap (not in scope for this skill version)

These features are planned for future versions:

- **Adaptive loop:** Quiz results from one session influence next session's content emphasis
  (architecture already supports this — Step 5 generates files sequentially, enabling
  quiz-result injection before generating the next day's file)
- **Hosted URL delivery:** Publish all 15 day files as a static site after generation;
  scheduler delivers day URLs instead of files (see TODOS.md for full spec)
- **Source quality cache:** Cache per-URL browse scores to speed up repeat runs
  (see TODOS.md for full spec)
- **Bilingual output:** English/Chinese or bilingual curriculum and quiz questions
- **Engineering sub-roles:** ML Engineer, MLOps, Data Engineer (separate lenses)
- **Parallel search:** Run Layers 2/3/4 concurrently for faster generation
- **Profile write-back verification enhancement:** After writing .user-profile.json in
  Step 0, confirm file exists with a read-back check and surface a warning if missing

---

*Design docs:*
*  V2: `~/.gstack/projects/ai-learning/kiba-main-design-20260405-082226.md`*
*  V3: `~/.gstack/projects/ai-learning/kiba-main-design-20260405-232236.md`*
*Test plan: `~/.gstack/projects/ai-learning/kiba-main-eng-review-test-plan-20260405-084353.md`*
*Skill version: V3 — dynamic day summaries (framed), learner profile + calibration quiz, per-day HTML files, quiz reveal, richer examples, OpenClaw quiz mode*
