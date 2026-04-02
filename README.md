# AI Learning Skill

A Cursor/Claude agent skill that generates personalized AI learning curricula anchored to real products.

## What It Does

Give it a product you care about (e.g., "Cursor", "Perplexity", "InsForge") and your job function. It will:

1. **Reverse-engineer the product's AI tech stack** using live web research
2. **Map the competitive landscape** (key competitors, differentiators, user sentiment)
3. **Generate a 15-session learning curriculum** tailored to your role
4. **Include quizzes after every session** — 2 multiple-choice (self-graded) + 1 open-ended (with model answer)
5. **Write everything to a markdown file** you can read anywhere, anytime

## Supported Job Functions

| Role | Quiz Focus |
|---|---|
| Product Manager | Business tradeoffs, stakeholder communication, metric selection |
| Software Engineer | Debugging, implementation, system design, performance |
| UX Designer | User-facing behavior, error states, trust signals, interaction patterns |
| Operations / Program Manager | Rollout planning, risk mitigation, cross-team coordination |
| Data Analyst | Metrics, data quality, evaluation methodology, bias detection |

## How to Use

### In Cursor (recommended)

1. Attach `SKILL.md` to your Cursor chat using the `@` file reference or by placing it in `~/.agents/skills/ai-learning/SKILL.md`
2. Type: `@SKILL.md generate my learning curriculum`
3. Follow the prompts (select your role → enter a product name)
4. Your curriculum is saved to `~/.gstack/learning/`

### Manually (any Claude interface)

1. Open `SKILL.md`
2. Copy the full contents into a Claude conversation
3. Follow the prompts

## Output Files

Generated files are saved to `~/.gstack/learning/` (outside this repo — personal data):

```
~/.gstack/learning/
├── {product}-{role}-curriculum.md    # Your full 15-session curriculum
└── quiz-{product}-{role}-{timestamp}.md  # Blank quiz tracker
```

## Curriculum Structure

```
{product}-{role}-curriculum.md
├── Tech Stack at a Glance
├── Competitive Snapshot
├── Module 1: AI Technology Stack (Days 1–3)
├── Module 2: Competitive Landscape (Days 4–5)
├── Module 3: Your Role at This Product Type (Days 6–8)
├── Module 4: How to Build This (Days 9–12)
└── Module 5: Day-in-the-Life + Capstone Quiz (Days 13–15)
```

Each session follows a standard template:
- **What you'll learn** — one-sentence summary
- **Key concepts** — 3 plain-English definitions
- **Sources** — linked free resources with estimated read/watch time
- **How this applies to your role** — concrete connection to your job
- **Quiz** — 2 MC (with `<details>` answer spoilers) + 1 open-ended (with model answer)

## Source Quality

The skill uses a 4-layer search strategy:
- **Layer 1** — Product intelligence (identify the tech stack)
- **Layer 2** — Technology content per identified tech × role lens
- **Layer 3** — Job function responsibilities at this type of company
- **Layer 4** — Competitive landscape

Sources are filtered for recency (< 24 months preferred), quality (concrete examples, primary sources), and session length (< 20 min target). When external sources are limited, the skill uses model knowledge — clearly labeled as `[Model Knowledge]`.

## Design & Architecture

This skill was designed using the `/office-hours` and `/plan-eng-review` gstack skills:
- Design doc: `~/.gstack/projects/ai-learning/`
- Test plan: `~/.gstack/projects/ai-learning/` (7 validation test cases)
- Eng review: CLEARED — 6 architecture issues resolved before implementation

## V1 Scope

V1 (this skill) covers:
- ✅ Product-centric curriculum generation
- ✅ 5 job functions with role-differentiated quizzes
- ✅ Model knowledge fallback for closed-source products
- ✅ Hybrid quiz format (2 MC + 1 open-ended)

## V2 Roadmap (not yet built)

- Adaptive loop (quiz results change next session's content)
- Survey-based entry (no product needed — start from experience level)
- Bilingual output (English/Chinese)
- Engineering sub-roles (ML Engineer, MLOps, Data Engineer)
- `--grade` flag for AI feedback on open-ended answers

## License

MIT — free to use, modify, and share.
