# AI Learning Skill

An agent skill for **Cursor**, **Claude Code**, and other Claude-powered tools. It turns a product you care about into a **15-day, role-specific AI learning path** you can actually finish—mobile-friendly HTML, quizzes, and optional daily email delivery.

---

## 1. What is AI Learning (this skill)?

**AI Learning** here means: a structured curriculum that teaches you how a *real* AI product works—its stack, competitors, and how your job function fits—using **live research**, **curated sources**, and **daily-sized sessions** (about 15–20 minutes each).

You choose:

- A **product** (e.g. Cursor, Notion AI, an internal or niche tool)
- A **job function** (PM, engineer, UX, ops, analyst)

The skill produces materials grounded in that product—not a generic “intro to AI” course.

---

## 2. Highlights

| Feature | What you get |
|--------|----------------|
| **Product-anchored curriculum** | Tech stack + competitive snapshot tied to *your* product |
| **15 per-day HTML sessions** | One file per day; readable on phone or desktop |
| **Role-tuned depth** | Vocabulary, density, and examples adapt to PM / engineer / UX / ops / analyst |
| **Learner profile + calibration** | Short questionnaire + quiz to tune “how deep” the content goes |
| **Quizzes** | Multiple-choice + open-ended prompts with model answers |
| **Dynamic day summaries** | Each day’s “what today is about” reflects real session content |
| **Curriculum map** | Table of modules with Focus lines derived from your session goals |
| **“Coming up next”** | Preview of the next day at the bottom of each HTML page |
| **Source diversity** | Prioritizes neutral / third-party sources; product docs used sparingly; enough sources to *learn*, not a fixed count |
| **Manifest + optional email** | `manifest.json` drives which day to open; macOS users can set up **daily SMTP email** (see `SKILL.md` Step 5.5) |
| **Preferences you can change** | Full profile or delivery-only updates without regenerating everything by hand |

Outputs are written under **`~/.gstack/learning/`** on your machine (**`~` = your home folder**, e.g. `/Users/you` on macOS — **not** the filesystem root `/`). Nothing is required inside this git repo besides `SKILL.md`.

---

## 3. Quick start (install)

1. **Clone or copy this repository** (this folder contains `SKILL.md`, the skill definition).

2. **Install the skill where your agent looks for skills**, for example:
   - Cursor: add or symlink so the skill is available (e.g. `~/.agents/skills/ai-learning/SKILL.md` or attach `SKILL.md` per chat—see your product’s skill docs).
   - Claude Code / similar: follow your tool’s “project skill” or “import SKILL.md” workflow.

3. **Output folder:** You usually **do not need** to create anything manually. On first run the skill runs `mkdir -p ~/.gstack/learning`. If your home directory cannot create that path (permissions, corporate policy), the skill **falls back to the current working directory** and should tell you where files were written.

4. **Open a new chat** and attach or invoke the skill (see §4).

5. **First run**: answer the profile questions (AI level, calibration, daily minutes, format, **delivery email & time** if you want email later). Then pick role and product when prompted.

6. **After generation**, open the printed paths under `~/.gstack/learning/` (e.g. `*-day-01.html`). For **daily email** on macOS, follow the **Step 5.5** block in `SKILL.md`: create `~/.gstack/learning/.smtp-config.json` with **your** mail provider’s SMTP settings (use an **app password** for Gmail—never commit that file).

---

## 4. How to run the skill & change preferences

### Trigger phrases (for you and for skill routing)

Exact wording is **not** required — same intent is enough. The canonical list also lives at the top of **`SKILL.md`** under *When to use this skill*.

**Start a curriculum**

| Example says… | … |
|----------------|---|
| "Run / use the **AI Learning skill**" | Starts from Step 0 |
| "**Generate** my AI learning **curriculum**" | Same |
| "**Build a 15-day** learning plan for **{product}** as a **{role}**" | Same (product + role in one line) |
| Attach **`@SKILL.md`** + "generate curriculum for **{product}**" | Same |

**Preferences**

| Intent | Example phrases |
|--------|------------------|
| Change everything (level, time, format, delivery) | `update my profile`, `change my preferences` |
| Email or daily send time only | `update delivery`, `change delivery email`, `change delivery time`, `update email`, `change my delivery` |

### Run / generate a curriculum

- In Cursor: attach **`SKILL.md`** (e.g. `@` file) and use a **trigger phrase** above or ask to generate a curriculum for a product + role.
- In any Claude UI: paste or attach the full **`SKILL.md`** and follow the steps from the top.

Typical flow: **Step 0 (profile)** → **Step 1 (role)** → **product name** → research & generation → files under `~/.gstack/learning/` (or the fallback directory if creation failed).

### Change preferences

| What you want | What to say (examples) |
|----------------|-------------------------|
| Full profile (AI level, time, format, **and** delivery) | `update my profile` or `change my preferences` |
| **Only** email or daily send time | `update delivery`, `change delivery email`, `change delivery time`, `update email`, `change my delivery` |

The skill updates **`~/.gstack/learning/.user-profile.json`** (local file). It does **not** store SMTP passwords in the profile—those belong only in **`~/.gstack/learning/.smtp-config.json`**, which you should **never** commit to git.

---

## 5. Usage

### Who it’s for

- **ICs and leads** who need to ramp on a specific AI product fast.
- **Builders** who learn better from a structured arc than from random bookmarks.
- **Teams** who want a **shared vocabulary** around one product’s AI stack.

### What “good” looks like

- You finish **Day 1** in one sitting and know what Days 2–3 cover.
- You can explain the product’s **tech stack** and **one real competitor tradeoff** to a colleague.
- Quizzes surface gaps; you revisit sources or ask follow-up questions in the same chat.

### Privacy & safety

- **No API keys** belong in this repo. Research uses normal web tools as described in `SKILL.md`.
- Treat **`.smtp-config.json`** like a secret: local-only, strong app passwords, not shared.


---

## Output layout (typical)

Under `~/.gstack/learning/` (exact names depend on product/role slug):

- `*-day-01.html` … `*-day-15.html` — daily sessions  
- `*-manifest.json` — scheduler / delivery index  
- Optional: `*.md` curriculum reference, quiz tracker

---

## License

MIT — free to use, modify, and share.
