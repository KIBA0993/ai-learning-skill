# AI Learning Skill — Product-Centric Curriculum Generator

**What this skill does:** You give it a real AI product you care about (e.g., "Cursor",
"Perplexity", "Notion AI") and your job function. It reverse-engineers the product's
tech stack, researches the competitive landscape and role responsibilities, then
generates a structured 15-session learning curriculum tailored to your role — with
quizzes after every session.

**Time to run:** ~3-5 minutes. Output: a ready-to-read markdown curriculum file.

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
- Quiz results: `quiz-{PRODUCT_SLUG}-{ROLE_SLUG}-{TIMESTAMP}.md`

Tell the user:
> "Got it. Generating your **{PRODUCT} curriculum for {ROLE}**.
> I'll research the product, then build your 15-session learning plan.
> This takes 3–5 minutes — sit tight."

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

**For each qualifying source, record:**
- Title, URL, platform, estimated read/watch time, one-line summary of its value

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
- Product Manager: `"{technology}" explained product manager non-technical use case`
- Software Engineer: `"{technology}" implementation tutorial code example python`
- UX Designer: `"{technology}" user experience design patterns interaction`
- Operations / Program Manager: `"{technology}" deployment monitoring production operations`
- Data Analyst: `"{technology}" metrics evaluation business impact measurement`

**Plus a general search for each technology:**
`"{technology}" explained {current year}`

Apply quality filter to results. Note which technologies have good external sources
vs. which need model knowledge supplementation.

---

### Layer 3: Job Function Role Content (run once)

**Goal:** Understand what {ROLE} actually does at an AI product company in the
same category as {PRODUCT}.

Run these 3 searches:
```
"{product category}" "{ROLE}" responsibilities AI 2024 2025
"{ROLE}" working with AI engineers collaboration workflow
"{PRODUCT}" "{ROLE}" (may be sparse — supplement with model knowledge)
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

## Step 4: Generate the Curriculum

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

### Session Template

Use this exact format for EVERY session block:

```markdown
### Session {N}: {Title} ⏱ {X} min

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
{2-3 sentences connecting this concept to what a {ROLE} actually does with it.
Be concrete: what decision would you make, what would you measure, what would
you design, based on understanding this?}

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
- Sources: Layer 1 + Layer 2 results for the primary technology
- Quiz: Q1 focuses on understanding what this technology does vs. alternatives; Q3 open-ended on applying this to role

**Session 2: Supporting AI Systems** ⏱ 20 min
- Focus: Secondary technologies (RAG, agents, fine-tuning, local inference, etc.)
- Sources: Layer 2 results for supporting technologies
- Quiz: Q1 focuses on when to use each technology; Q3 on role-specific application

**Session 3: How the AI Stack Fits Together** ⏱ 15 min
- Focus: How the technologies interact at a system level; latency, cost, reliability tradeoffs
- Sources: System design posts, engineering blogs from Layer 1+2
- Quiz: Q1 focuses on a tradeoff scenario; Q3 on explaining the stack to a stakeholder / debugging a system issue / designing a flow (per role)

---

#### Module 2: Competitive Landscape — Learning Days 4–5

*Theme: Where does {PRODUCT} sit in the market, and why?*

**Session 4: Market Position** ⏱ 20 min
- Focus: Who are the main competitors, how does {PRODUCT} differentiate, what's the moat
- Sources: Layer 4 competitive search results
- Quiz: Q1 focuses on competitive strategy; Q3 on role-specific competitive analysis

**Session 5: User Perspective & Gaps** ⏱ 20 min
- Focus: What users love and complain about; where the product is winning and losing
- Sources: Layer 4 user feedback results; product reviews
- Quiz: Q1 focuses on interpreting user feedback; Q3 on what to do about a specific gap

---

#### Module 3: Your Role at This Type of Product — Learning Days 6–8

*Theme: What does a {ROLE} actually do at an AI product like {PRODUCT}?*

**Session 6: Core Responsibilities** ⏱ 20 min
- Focus: Day-to-day responsibilities of a {ROLE} at an AI product company
- Sources: Layer 3 role content results
- Quiz: Role lens strongly applied — questions about real decisions this role makes

**Session 7: Cross-Functional Collaboration** ⏱ 20 min
- Focus: How {ROLE} works with ML engineers, designers, PMs, data scientists
- Sources: Layer 3 results on collaboration; model knowledge on common workflows
- Quiz: Q1 scenario on a cross-team decision; Q3 on navigating a real collaboration challenge

**Session 8: Key Metrics & Success Criteria** ⏱ 20 min
- Focus: How {ROLE} measures success for AI features; what good looks like
- Sources: Role-specific metric frameworks from Layer 3
- Quiz: Q1 on distinguishing good metrics from vanity metrics; Q3 on designing a measurement framework

---

#### Module 4: How to Build This — Learning Days 9–12

*Theme: If you were building {PRODUCT} from scratch, how would you do it?*

**Session 9: Architecture & Key Flows** ⏱ 20 min
- Focus: High-level architecture; the 2-3 most important technical flows in {PRODUCT}
- Sources: Layer 2 implementation/architecture content
- Quiz: Role-specific — PM focuses on architecture decisions; Eng on implementation; UX on user flow

**Session 10: Technology Decisions** ⏱ 20 min
- Focus: Why {PRODUCT} likely made the technology choices it did; what the alternatives were
- Sources: Layer 1+2 results on technology tradeoffs
- Quiz: Q1 on a build vs buy / make vs use scenario; Q3 on justifying a tech decision

**Session 11: Important Features & Tradeoffs** ⏱ 20 min
- Focus: The 2-3 features that define {PRODUCT}'s AI experience; the engineering/design tradeoffs behind them
- Sources: Layer 1+2 feature-level content; engineering blog posts
- Quiz: Q1 on a feature tradeoff; Q3 on designing or evaluating a feature from role perspective

---

#### Module 5: Day-in-the-Life + Capstone — Learning Days 13–15

*Theme: Putting it all together.*

**Session 12: A Day in the Life as {ROLE} at {PRODUCT}** ⏱ 20 min
- Focus: Walk through a realistic workday for a {ROLE} at a company like {PRODUCT}
- Content: Concrete scenario (morning standup → key decisions → afternoon focus work → weekly goals)
- Sources: Layer 3 day-in-the-life content; model knowledge for specifics
- Quiz: Q1 on a realistic daily decision; Q3 on prioritizing competing demands

**Session 13: Scenario Simulation** ⏱ 15 min
- Focus: A realistic challenge scenario where you apply everything learned
- Content: Example scenario: "It's Q3. {PRODUCT}'s accuracy dropped 15% after a model update.
  As {ROLE}, what do you do in the first 48 hours?"
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

---

## Step 6: Final Summary to User

Print a summary in this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {PRODUCT} AI Learning Curriculum — {ROLE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 CURRICULUM
   File: {curriculum filename}
   Path: {full path}
   Sessions: 15 (+ capstone quiz)
   Total time: ~5–6 hours across 15 days

🧠 TECH STACK IDENTIFIED
   {list each technology found, one per line, with confidence level}

📊 QUIZ TRACKER
   File: {quiz filename}
   Path: {full path}

🗺️ YOUR LEARNING PATH
   Module 1 (Days 1–3):  AI Technology Stack
   Module 2 (Days 4–5):  Competitive Landscape
   Module 3 (Days 6–8):  Your Role as {ROLE}
   Module 4 (Days 9–12): How to Build This
   Module 5 (Days 13–15): Day-in-the-Life + Capstone

💡 HOW TO USE THIS
   1. Open the curriculum file in any markdown reader
      (Obsidian, GitHub, VS Code, or any text editor)
   2. Do ONE session per day — 15–20 min
   3. Answer all 3 quiz questions before peeking at answers
   4. Log your scores in the quiz tracker
   5. After the capstone, note your weak areas and review those sessions

⚠️  SOURCE NOTES
   {If model knowledge was used: "Some sections use model knowledge — labeled [Model Knowledge]
   throughout. Cross-check technical claims before using in work decisions."}
   {If all external sources: "All content sourced from verified external resources."}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

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

## V2 Roadmap (not in scope for this skill version)

These features are planned for V2 after V1 is validated:

- **Adaptive loop:** Quiz results from one session influence next session's content emphasis
- **User profile persistence:** Track learning history, quiz performance, and pace across sessions
- **Survey-based entry:** Generate a curriculum from experience level + interests (no product needed)
- **Bilingual output:** English/Chinese or bilingual curriculum and quiz questions
- **Engineering sub-roles:** ML Engineer, MLOps, Data Engineer (separate lenses)
- **`--grade` flag:** Re-invoke to get AI feedback on open-ended answers
- **Parallel search:** Run Layers 2/3/4 concurrently for faster generation

---

*Design doc: `~/.gstack/projects/ai-learning/kiba-unknown-design-20260401-125354.md`*
*Test plan: `~/.gstack/projects/ai-learning/kiba-unknown-eng-review-test-plan-20260401-232314.md`*
*Skill version: V1 — Product-Centric Curriculum Generator*
