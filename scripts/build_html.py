#!/usr/bin/env python3
"""
build_html.py — deterministic HTML builder for the AI Learning skill.

Reads a single curriculum content file (curriculum.json) produced by the skill in
Step 4/5 and emits, with identical structure every run:

  - 15 per-day HTML files      {slug}-day-01.html ... day-15.html
  - manifest.json              {slug}-manifest.json   (scheduler index)
  - active-manifest.json       explicit active-curriculum pointer
  - quiz tracker (markdown)    quiz-{slug}-{timestamp}.md

The model writes prose ONCE as JSON; this script guarantees the canonical CSS shell,
email-safe (JS-free, always-open answers) quiz blocks, dark-mode-aware curriculum map,
and the exact section markers the delivery quality gate checks for. No third-party deps.

NOTE: This file is the authoritative copy embedded in SKILL.md (Step 5). The copy in
scripts/ is a tested mirror — keep the two in sync.

Usage:
    python3 build_html.py [curriculum.json] [output_dir]
Defaults: curriculum.json in CWD; output_dir = the JSON file's directory.
"""

import sys
import os
import re
import json
import html


# --------------------------------------------------------------------------- #
# Canonical CSS — single source of truth (mirrors SKILL.md Step 5 CSS block).
# --------------------------------------------------------------------------- #
CSS = """*, *::before, *::after { box-sizing: border-box; }
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
hr { border: none; border-top: 1px solid #e5e7eb; margin: 2em 0; }
ul, ol { padding-left: 1.5em; } li { margin-bottom: 0.3em; }
nav#top-nav {
  position: sticky; top: 0; background: #fff; border-bottom: 2px solid #e5e7eb;
  padding: 8px 0; display: flex; gap: 12px; flex-wrap: wrap; z-index: 100; margin-bottom: 24px;
}
nav#top-nav a { text-decoration: none; font-size: 0.85em; font-weight: 600; color: #374151; white-space: nowrap; }
nav#top-nav a:hover { color: #2563eb; }
/* Day summary */
.day-summary { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 14px 18px; margin-bottom: 24px; }
.day-summary strong { font-size: 1.1em; display: block; margin-bottom: 6px; }
.session-insight { font-size: 0.97em; line-height: 1.6; color: #374151; margin: 8px 0 12px 0; padding: 10px 14px; background: rgba(255,255,255,0.6); border-left: 3px solid #2563eb; border-radius: 0 6px 6px 0; }
/* Quiz — questions block */
#quiz-section { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 16px; margin: 24px 0; }
.question { margin-bottom: 20px; }
.question:last-of-type { margin-bottom: 0; }
/* Divider between questions and answers */
.answer-divider { text-align: center; margin: 8px 0 0; padding: 10px 0 0; border-top: 2px dashed #bae6fd; font-size: 0.85em; color: #6b7280; font-style: italic; }
/* Answers — grouped block (email-safe: always open, no JS needed) */
details.answers-block { border: 1px solid #86efac; border-radius: 8px; margin: 24px 0; overflow: hidden; }
details.answers-block summary { cursor: pointer; padding: 12px 16px; background: #dcfce7; color: #166534; font-weight: 700; font-size: 1em; list-style: none; }
details.answers-block summary::-webkit-details-marker { display: none; }
details.answers-block summary::before { content: "\\25B6 "; font-size: 0.75em; }
details.answers-block[open] summary::before { content: "\\25BC "; }
.answers-body { background: #f0fdf4; padding: 16px; border-top: 1px solid #86efac; }
.answer-item { margin-bottom: 16px; }
.answer-item:last-child { margin-bottom: 0; }
.answer-item p { margin: 4px 0; font-size: 0.95em; color: #14532d; }
/* Complete banner (day 15) */
.complete-banner { background: #f0fdf4; border: 2px solid #4ade80; border-radius: 8px; padding: 20px; margin: 24px 0; text-align: center; font-size: 1.1em; }
/* Coming up next */
.coming-next { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #6366f1; border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 24px 0; }
.coming-next strong { display: block; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.05em; color: #6366f1; margin-bottom: 4px; }
.coming-next p { margin: 0; color: #374151; font-size: 0.97em; }
/* Curriculum map — current-module highlight (theme-aware; no inline colors) */
tr.current-module { background: #dbeafe; font-weight: 600; }
tr.current-module td { color: #1e3a8a; }
.module-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #2563eb; margin-right: 6px; vertical-align: middle; }
@media (prefers-color-scheme: dark) {
  body { color: #e5e7eb; background: #111827; }
  h2 { border-color: #374151; }
  blockquote { border-color: #374151; color: #9ca3af; background: #1f2937; }
  th, td { border-color: #374151; } th { background: #1f2937; }
  pre, code { background: #1f2937; }
  hr { border-color: #374151; }
  nav#top-nav { background: #111827; border-color: #374151; }
  nav#top-nav a { color: #9ca3af; }
  a { color: #60a5fa; } a:visited { color: #a78bfa; }
  .day-summary { background: #1e3a5f; border-color: #3b82f6; }
  .session-insight { color: #d1d5db; background: rgba(0,0,0,0.2); border-left-color: #3b82f6; }
  #quiz-section { background: #1e3a5f; border-color: #3b82f6; }
  .answer-divider { border-color: #3b82f6; color: #9ca3af; }
  details.answers-block { border-color: #4ade80; }
  details.answers-block summary { background: #14532d; color: #bbf7d0; }
  .answers-body { background: #052e16; border-color: #4ade80; }
  .answer-item p { color: #86efac; }
  .complete-banner { background: #14532d; border-color: #4ade80; }
  .coming-next { background: #1e1b4b; border-color: #374151; border-left-color: #818cf8; }
  .coming-next strong { color: #818cf8; }
  .coming-next p { color: #d1d5db; }
  tr.current-module { background: #1e3a5f; }
  tr.current-module td { color: #dbeafe; }
  .module-dot { background: #60a5fa; }
}
@media print { nav#top-nav { display: none; } body { font-size: 12pt; max-width: 100%; padding: 0; } a { color: #000; } }
@media (max-width: 480px) { body { font-size: 16px; padding: 12px; } h1 { font-size: 1.5em; } table { font-size: 0.8em; } }"""


# --------------------------------------------------------------------------- #
# Minimal, dependency-free markdown rendering (only the subset the skill uses).
# --------------------------------------------------------------------------- #
def esc(text):
    return html.escape("" if text is None else str(text), quote=True)


def inline_md(text):
    """Render inline markdown to HTML. Escapes first, then applies a safe subset:
    `code`, [label](url), **bold**, *italic*. URLs are restricted to http(s)/mailto."""
    if text is None:
        return ""
    out = esc(text)

    # Code spans first — protect their contents from further substitution.
    code_store = []

    def _stash_code(m):
        code_store.append(m.group(1))
        return "\x00CODE%d\x00" % (len(code_store) - 1)

    out = re.sub(r"`([^`]+)`", _stash_code, out)

    # Links [label](url) — only allow safe schemes; label may contain bold/italic later.
    def _link(m):
        label, url = m.group(1), m.group(2)
        if not re.match(r"^(https?:|mailto:)", url, re.IGNORECASE):
            return m.group(0)
        return '<a href="%s">%s</a>' % (esc(url), label)

    # NOTE: label/url are already HTML-escaped (esc ran on the whole string).
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", _link, out)

    # Bold then italic.
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", out)

    # Restore code spans.
    for i, c in enumerate(code_store):
        out = out.replace("\x00CODE%d\x00" % i, "<code>%s</code>" % c)
    return out


def block_md(text):
    """Render a block of markdown (paragraphs, lists, headings, code fences,
    blockquotes) to HTML. Used for optional freeform session body_md."""
    if not text or not str(text).strip():
        return ""
    lines = str(text).replace("\r\n", "\n").split("\n")
    html_parts = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        if stripped.startswith("```"):
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            html_parts.append("<pre><code>%s</code></pre>" % esc("\n".join(code_lines)))
            continue

        # Blank line
        if not stripped:
            i += 1
            continue

        # Heading
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            html_parts.append("<h%d>%s</h%d>" % (level, inline_md(m.group(2)), level))
            i += 1
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append("<li>%s</li>" % inline_md(re.sub(r"^[-*]\s+", "", lines[i].strip())))
                i += 1
            html_parts.append("<ul>%s</ul>" % "".join(items))
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append("<li>%s</li>" % inline_md(re.sub(r"^\d+\.\s+", "", lines[i].strip())))
                i += 1
            html_parts.append("<ol>%s</ol>" % "".join(items))
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            html_parts.append("<blockquote>%s</blockquote>" % inline_md(" ".join(quote_lines)))
            continue

        # Paragraph (gather until blank line)
        para = [stripped]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|[-*]\s|\d+\.\s|>|```)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        html_parts.append("<p>%s</p>" % inline_md(" ".join(para)))
    return "\n".join(html_parts)


# --------------------------------------------------------------------------- #
# Component renderers
# --------------------------------------------------------------------------- #
def render_curriculum_map(modules, current_day):
    rows = []
    for mod in modules:
        rng = mod.get("day_range", [0, 0])
        lo, hi = rng[0], rng[1]
        is_current = lo <= current_day <= hi
        days_label = "%d–%d" % (lo, hi) if lo != hi else str(lo)
        focus = inline_md(mod.get("focus", ""))
        title = "Module %s: %s" % (esc(mod.get("number", "")), esc(mod.get("title", "")))
        if is_current:
            rows.append(
                '  <tr class="current-module">\n'
                '    <td><span class="module-dot"></span>%s</td>\n'
                '    <td style="white-space:nowrap;">%s</td>\n'
                '    <td>%s</td>\n'
                '  </tr>' % (title, days_label, focus)
            )
        else:
            rows.append(
                '  <tr><td>%s</td><td style="white-space:nowrap;">%s</td><td>%s</td></tr>'
                % (title, days_label, focus)
            )
    return (
        '<table style="font-size:.82em;margin:0 0 20px 0;">\n'
        '<thead><tr><th>Module</th><th>Days</th><th>Focus</th></tr></thead>\n'
        '<tbody>\n%s\n</tbody>\n</table>' % "\n".join(rows)
    )


def render_table(headers, rows):
    thead = "".join("<th>%s</th>" % inline_md(h) for h in headers)
    body = []
    for r in rows:
        body.append("<tr>%s</tr>" % "".join("<td>%s</td>" % inline_md(c) for c in r))
    return "<table>\n<thead><tr>%s</tr></thead>\n<tbody>\n%s\n</tbody>\n</table>" % (
        thead, "\n".join(body))


def render_day01_header(c):
    parts = ['<div class="curriculum-header">']
    parts.append("  <h1>%s — AI Learning Curriculum for %s</h1>"
                 % (esc(c["product"]), esc(c["role"])))
    parts.append('  <p>Generated: %s &nbsp;·&nbsp; 13 sessions + capstone &nbsp;·&nbsp; ~7–10 hours</p>'
                 % esc(c.get("generated_date", c.get("generated", ""))))
    parts.append("  <hr>")
    if c.get("why_product"):
        parts.append("  <h2>Why %s?</h2>" % esc(c["product"]))
        parts.append("  <p>%s</p>" % inline_md(c["why_product"]))
    if c.get("tech_stack"):
        parts.append("  <h2>Tech Stack at a Glance</h2>")
        rows = [[t.get("tech", ""), t.get("confidence", ""), t.get("role_in_product", "")]
                for t in c["tech_stack"]]
        parts.append(render_table(["Technology", "Confidence", "What it does in %s" % c["product"]], rows))
    comp = c.get("competitive")
    if comp and comp.get("rows"):
        parts.append("  <h2>Competitive Snapshot</h2>")
        headers = [""] + [c["product"]] + list(comp.get("competitors", []))
        rows = [[row.get("label", "")] + [row.get("product", "")] + list(row.get("values", []))
                for row in comp["rows"]]
        parts.append(render_table(headers, rows))
        if comp.get("source"):
            parts.append("  <p><em>Source: %s</em></p>" % inline_md(comp["source"]))
    parts.append("  <hr>")
    parts.append("</div>")
    return "\n".join(parts)


def render_day_summary(session):
    parts = ['<div class="day-summary">']
    parts.append("  <strong>Day %s of 15 — %s ⏱ %s min</strong>"
                 % (session["day"], esc(session["title"]), esc(session.get("minutes", ""))))
    if session.get("insight"):
        parts.append('  <div class="session-insight">%s</div>' % inline_md(session["insight"]))
    kcs = session.get("key_concepts") or []
    if kcs:
        parts.append("  <p><em>Key concepts:</em></p>")
        parts.append("  <ul>")
        for kc in kcs:
            parts.append("    <li><strong>%s:</strong> %s</li>"
                         % (inline_md(kc.get("name", "")), inline_md(kc.get("definition", ""))))
        parts.append("  </ul>")
    parts.append("</div>")
    return "\n".join(parts)


def render_sources(session):
    srcs = session.get("sources") or []
    parts = ["<h3>Sources</h3>"]
    if srcs:
        parts.append("<ul>")
        for s in srcs:
            meta = " — ".join(
                x for x in [esc(s.get("platform", "")),
                            ("%s min" % esc(s["minutes"])) if s.get("minutes") else ""]
                if x)
            label = inline_md(s.get("title", s.get("url", "source")))
            url = s.get("url", "")
            if url and re.match(r"^https?:", url, re.IGNORECASE):
                link = '<a href="%s">%s</a>' % (esc(url), label)
            else:
                link = label
            summ = (" — %s" % inline_md(s["summary"])) if s.get("summary") else ""
            tail = (" (%s)" % meta) if meta else ""
            parts.append("  <li>%s%s%s</li>" % (link, tail, summ))
        parts.append("</ul>")
    if session.get("model_knowledge_note"):
        parts.append("<blockquote><strong>[Model Knowledge]</strong> %s <em>— generated "
                     "from model training data, not a verified external source</em></blockquote>"
                     % inline_md(session["model_knowledge_note"]))
    return "\n".join(parts)


def render_applies(session):
    a = session.get("applies")
    if not a:
        return ""
    parts = ["<h3>How this applies to you as a %s</h3>" % esc(session.get("role_name", ""))]
    parts.append("<h4>Current state (without %s):</h4>" % esc(session.get("product_name", "")))
    if a.get("before_scenario"):
        parts.append("<p><em>%s</em></p>" % inline_md(a["before_scenario"]))
    steps = a.get("before_steps") or []
    if steps:
        parts.append("<ol>")
        for st in steps:
            tag = (" <code>[%s]</code>" % esc(st["tag"])) if st.get("tag") else ""
            mins = (" — ~%s min" % esc(st["minutes"])) if st.get("minutes") else ""
            parts.append("  <li>%s%s%s</li>" % (inline_md(st.get("text", "")), mins, tag))
        parts.append("</ol>")
    if a.get("before_total"):
        parts.append("<p><em>Total: %s</em></p>" % inline_md(a["before_total"]))
    if a.get("with_product"):
        parts.append("<h4>With %s:</h4>" % esc(session.get("product_name", "")))
        parts.append("<p>%s</p>" % inline_md(a["with_product"]))
    if a.get("role_takeaway"):
        parts.append("<h4>What this means for you as %s:</h4>" % esc(session.get("role_name", "")))
        parts.append("<p>%s</p>" % inline_md(a["role_takeaway"]))
    return "\n".join(parts)


def render_mc_question(idx, q, label="Q"):
    opts = "".join("<li>%s</li>" % inline_md(o) for o in q.get("options", []))
    return (
        '  <div class="question">\n'
        '    <p><strong>%s%d:</strong> %s</p>\n'
        '    <ul>%s</ul>\n'
        '  </div>' % (label, idx, inline_md(q.get("stem", "")), opts)
    )


def render_quiz_section(session):
    quiz = session.get("quiz") or {}
    parts = ['<div id="quiz-section">']
    parts.append('  <h4>\U0001F4CB Session %s Quiz</h4>' % session.get("session_number", session["day"]))
    parts.append('  <p style="font-size:0.9em;color:#6b7280;margin-top:0;">Read all questions, '
                 'then scroll down to check your answers.</p>')
    q1, q2, q3 = quiz.get("q1"), quiz.get("q2"), quiz.get("q3")
    if q1:
        parts.append(render_mc_question(1, q1))
    if q2:
        parts.append(render_mc_question(2, q2))
    if q3:
        parts.append(
            '  <div class="question">\n'
            '    <p><strong>Q3 (open-ended):</strong> %s</p>\n'
            '    <p style="font-size:0.9em;color:#6b7280;font-style:italic;">Reflect before '
            'scrolling to the answers below.</p>\n'
            '  </div>' % inline_md(q3.get("prompt", "")))
    parts.append('  <div class="answer-divider">↓ &nbsp; Answers below &nbsp; ↓</div>')
    parts.append('</div>')

    # Answers block (email-safe: always open, no JS)
    parts.append('<details class="answers-block" open>')
    parts.append('  <summary>✅ Session %s Quiz Answers</summary>'
                 % session.get("session_number", session["day"]))
    parts.append('  <div class="answers-body">')
    if q1:
        parts.append('    <div class="answer-item"><p><strong>Q1 — Correct: %s</strong></p><p>%s</p></div>'
                     % (esc(q1.get("correct", "")), inline_md(q1.get("explanation", ""))))
    if q2:
        parts.append('    <div class="answer-item"><p><strong>Q2 — Correct: %s</strong></p><p>%s</p></div>'
                     % (esc(q2.get("correct", "")), inline_md(q2.get("explanation", ""))))
    if q3:
        parts.append('    <div class="answer-item"><p><strong>Q3 — Model answer:</strong></p><p>%s</p></div>'
                     % inline_md(q3.get("model_answer", "")))
    parts.append('  </div>')
    parts.append('</details>')
    return "\n".join(parts)


def render_coming_next(next_session):
    if not next_session:
        return ""
    return (
        '<div class="coming-next">\n'
        '  <strong>Coming up next</strong>\n'
        '  <p>Day %s — %s<br>\n'
        '  <span style="font-size:0.9em;color:#6b7280;">%s</span></p>\n'
        '</div>' % (next_session["day"], inline_md(next_session["title"]),
                    inline_md(next_session.get("what_learn", "")))
    )


def render_capstone_mc(session):
    parts = ['<div class="day-summary">']
    parts.append('  <strong>Day 14 of 15 — Capstone Quiz ⏱ %s min</strong>'
                 % esc(session.get("minutes", 20)))
    parts.append('  <p><em>Spans all 5 modules. Work through these without looking back at the '
                 'curriculum.</em></p>')
    parts.append('</div>')
    parts.append('<div id="quiz-section">')
    parts.append('  <h4>\U0001F4CB Capstone Quiz — Multiple Choice</h4>')
    parts.append('  <p style="font-size:0.9em;color:#6b7280;margin-top:0;">Answer all 5 questions, '
                 'then scroll down to check your answers.</p>')
    qs = session.get("questions", [])
    for idx, q in enumerate(qs, 1):
        parts.append(render_mc_question(idx, q))
    parts.append('  <div class="answer-divider">↓ &nbsp; Answers below &nbsp; ↓</div>')
    parts.append('</div>')
    parts.append('<details class="answers-block" open>')
    parts.append('  <summary>✅ Capstone MC Answers</summary>')
    parts.append('  <div class="answers-body">')
    for idx, q in enumerate(qs, 1):
        parts.append('    <div class="answer-item"><p><strong>Q%d — Correct: %s</strong></p><p>%s</p></div>'
                     % (idx, esc(q.get("correct", "")), inline_md(q.get("explanation", ""))))
    parts.append('    <p style="margin-top:16px;font-style:italic;color:#166534;">Open-ended '
                 'questions are in Day 15 →</p>')
    parts.append('  </div>')
    parts.append('</details>')
    return "\n".join(parts)


def render_capstone_oe(session):
    parts = ['<div class="day-summary">']
    parts.append('  <strong>Day 15 of 15 — Capstone: Open-Ended Questions ⏱ %s min</strong>'
                 % esc(session.get("minutes", 15)))
    parts.append('  <p><em>Two synthesis questions. Write your answers on paper or in a notes app, '
                 'then scroll down for model answers.</em></p>')
    parts.append('</div>')
    parts.append('<div id="quiz-section">')
    parts.append('  <h4>\U0001F4CB Capstone Quiz — Open-Ended</h4>')
    parts.append('  <p style="font-size:0.9em;color:#6b7280;margin-top:0;">Write your answers before '
                 'scrolling to the model answers below.</p>')
    qs = session.get("questions", [])
    for idx, q in enumerate(qs, 1):
        parts.append('  <div class="question"><p><strong>OE%d:</strong> %s</p></div>'
                     % (idx, inline_md(q.get("prompt", ""))))
    parts.append('  <div class="answer-divider">↓ &nbsp; Model answers below &nbsp; ↓</div>')
    parts.append('</div>')
    parts.append('<details class="answers-block" open>')
    parts.append('  <summary>✅ Capstone Open-Ended Model Answers</summary>')
    parts.append('  <div class="answers-body">')
    for idx, q in enumerate(qs, 1):
        parts.append('    <div class="answer-item"><p><strong>OE%d — Model answer:</strong></p><p>%s</p></div>'
                     % (idx, inline_md(q.get("model_answer", ""))))
    parts.append('  </div>')
    parts.append('</details>')
    parts.append('<div class="complete-banner">')
    parts.append('  \U0001F389 <strong>Course complete!</strong><br>')
    parts.append('  You’ve finished all 15 days of your %s curriculum as a %s.<br>'
                 % (esc(session.get("product_name", "")), esc(session.get("role_name", ""))))
    parts.append('  <small>Review your weak areas in the quiz tracker, then revisit those sessions.</small>')
    parts.append('</div>')
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Page assembly
# --------------------------------------------------------------------------- #
def html_shell(product, day, title, body):
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>%s — Day %s of 15 — %s</title>\n"
        "<style>\n%s\n</style>\n</head>\n<body>\n"
        '<header style="border-bottom:2px solid #e5e7eb;padding:10px 0;margin-bottom:20px;'
        'font-size:0.9em;color:#6b7280;">\n'
        "  %s Learning &nbsp;·&nbsp; <strong>Day %s of 15</strong>\n</header>\n"
        "<main>\n%s\n</main>\n</body>\n</html>\n"
        % (esc(product), day, esc(title), CSS, esc(product), day, body)
    )


def build_day_html(c, session, modules, next_session):
    day = session["day"]
    product = c["product"]
    kind = session.get("capstone")

    body_parts = []
    # Curriculum map appears on every day, above the day-summary box.
    body_parts.append(render_curriculum_map(modules, day))

    if day == 1 and kind is None:
        body_parts.append(render_day01_header(c))

    if kind == "mc":
        body_parts.append(render_capstone_mc(session))
        body_parts.append(render_coming_next(next_session))
        return html_shell(product, day, session.get("title", "Capstone Quiz"), "\n".join(body_parts))
    if kind == "oe":
        body_parts.append(render_capstone_oe(session))
        # No "coming next" on day 15 — the complete banner replaces it.
        return html_shell(product, day, session.get("title", "Capstone"), "\n".join(body_parts))

    # Regular learning day
    body_parts.append(render_day_summary(session))
    if session.get("body_md"):
        body_parts.append(block_md(session["body_md"]))
    body_parts.append(render_sources(session))
    body_parts.append(render_applies(session))
    body_parts.append(render_quiz_section(session))
    body_parts.append(render_coming_next(next_session))
    return html_shell(product, day, session["title"], "\n".join(body_parts))


def quiz_tracker_md(c):
    lines = ["# Quiz Tracker — %s (%s)" % (c["product"], c["role"]),
             "Started: %s" % c.get("generated_date", c.get("generated", "")),
             "",
             "## Instructions",
             "After completing each session quiz, record your results here.",
             "For MC questions: mark ✅ correct or ❌ incorrect.",
             "For open-ended questions: rate your answer 1-5 and note what you missed.",
             "",
             "## Session Results",
             "",
             "| Session | Q1 MC | Q2 MC | Q3 Open-ended | Notes |",
             "|---------|-------|-------|---------------|-------|"]
    for i in range(1, 14):
        lines.append("| Session %d | | | /5 | |" % i)
    for i in range(1, 6):
        lines.append("| Capstone MC %d | | | — | |" % i)
    for i in range(1, 3):
        lines.append("| Capstone OE %d | — | — | /5 | |" % i)
    lines += ["",
              "## Weak Areas (fill in after capstone)",
              "{Topics where you got MC wrong or rated open-ended < 3}",
              "",
              "## Next: What to Review",
              "{Sessions to re-read before moving to the next curriculum}",
              ""]
    return "\n".join(lines)


def curriculum_md(c):
    """Human-readable full study guide (markdown), generated from the same JSON so it can
    never drift from the HTML. Mirrors the Step 4 document structure."""
    L = []
    L.append("# %s — AI Learning Curriculum for %s" % (c["product"], c["role"]))
    L.append("")
    L.append("**Generated:** %s  " % c.get("generated_date", c.get("generated", "")))
    L.append("**Product:** %s  " % c["product"])
    L.append("**Your role:** %s  " % c["role"])
    L.append("**Total learning time:** ~7–10 hours across 15 days (15–20 min each)  ")
    L.append("**Sessions:** 13 learning sessions across 5 modules + capstone on Days 14–15")
    L.append("")
    if c.get("banner") == "limited_sources":
        L.append("> ⚠️ **LIMITED EXTERNAL SOURCES** — some sections use **[Model Knowledge]**; cross-check key claims.")
        L.append("")
    elif c.get("banner") == "no_search":
        L.append("> ⚠️ **NO LIVE WEB SEARCH** — generated from model training data only; verify currency.")
        L.append("")
    L.append("---")
    L.append("")
    if c.get("why_product"):
        L.append("## Why %s?" % c["product"])
        L.append("")
        L.append(c["why_product"])
        L.append("")
    if c.get("tech_stack"):
        L.append("## Tech Stack at a Glance")
        L.append("")
        L.append("| Technology | Confidence | What it does in %s |" % c["product"])
        L.append("|---|---|---|")
        for t in c["tech_stack"]:
            L.append("| %s | %s | %s |" % (t.get("tech", ""), t.get("confidence", ""), t.get("role_in_product", "")))
        L.append("")
    comp = c.get("competitive")
    if comp and comp.get("rows"):
        L.append("## Competitive Snapshot")
        L.append("")
        header = ["", c["product"]] + list(comp.get("competitors", []))
        L.append("| " + " | ".join(header) + " |")
        L.append("|" + "---|" * len(header))
        for row in comp["rows"]:
            cells = [row.get("label", ""), row.get("product", "")] + list(row.get("values", []))
            L.append("| " + " | ".join(str(x) for x in cells) + " |")
        if comp.get("source"):
            L.append("")
            L.append("*Source: %s*" % comp["source"])
        L.append("")
    L.append("---")
    L.append("")
    for s in c["sessions"]:
        kind = s.get("capstone")
        if kind == "mc":
            L.append("## Capstone Quiz — Multiple Choice (Day 14)")
            L.append("")
            for i, q in enumerate(s.get("questions", []), 1):
                L.append("**Q%d:** %s" % (i, q.get("stem", "")))
                for o in q.get("options", []):
                    L.append("- %s" % o)
                L.append("")
                L.append("<details><summary>Show Answer</summary>")
                L.append("")
                L.append("**Correct: %s** — %s" % (q.get("correct", ""), q.get("explanation", "")))
                L.append("")
                L.append("</details>")
                L.append("")
            continue
        if kind == "oe":
            L.append("## Capstone Quiz — Open-Ended (Day 15)")
            L.append("")
            for i, q in enumerate(s.get("questions", []), 1):
                L.append("**OE%d:** %s" % (i, q.get("prompt", "")))
                L.append("")
                L.append("<details><summary>Model answer</summary>")
                L.append("")
                L.append(q.get("model_answer", ""))
                L.append("")
                L.append("</details>")
                L.append("")
            continue

        L.append("## Session %s: %s ⏱ %s min" % (s.get("session_number", s["day"]), s["title"], s.get("minutes", "")))
        L.append("")
        if s.get("insight"):
            L.append("**Day summary insight:** %s" % s["insight"])
            L.append("")
        if s.get("what_learn"):
            L.append("**What you'll learn:** %s" % s["what_learn"])
            L.append("")
        if s.get("key_concepts"):
            L.append("**Key concepts:**")
            for kc in s["key_concepts"]:
                L.append("- **%s:** %s" % (kc.get("name", ""), kc.get("definition", "")))
            L.append("")
        if s.get("sources"):
            L.append("**Sources:**")
            for src in s["sources"]:
                meta = ", ".join(x for x in [src.get("platform", ""),
                                             ("%s min" % src["minutes"]) if src.get("minutes") else ""] if x)
                L.append("- [%s](%s)%s%s" % (src.get("title", src.get("url", "source")), src.get("url", ""),
                                             (" — %s" % meta) if meta else "",
                                             (" — %s" % src["summary"]) if src.get("summary") else ""))
            L.append("")
        if s.get("model_knowledge_note"):
            L.append("> **[Model Knowledge]** %s" % s["model_knowledge_note"])
            L.append("")
        if s.get("body_md"):
            L.append(s["body_md"])
            L.append("")
        a = s.get("applies")
        if a:
            L.append("**How this applies to you as a %s:**" % c["role"])
            L.append("")
            if a.get("before_scenario"):
                L.append("*Current state (without %s):* %s" % (c["product"], a["before_scenario"]))
            for i, st in enumerate(a.get("before_steps", []), 1):
                tag = (" `[%s]`" % st["tag"]) if st.get("tag") else ""
                mins = (" — ~%s min" % st["minutes"]) if st.get("minutes") else ""
                L.append("%d. %s%s%s" % (i, st.get("text", ""), mins, tag))
            if a.get("before_total"):
                L.append("*Total: %s*" % a["before_total"])
            if a.get("with_product"):
                L.append("")
                L.append("**With %s:** %s" % (c["product"], a["with_product"]))
            if a.get("role_takeaway"):
                L.append("")
                L.append("**What this means for you as %s:** %s" % (c["role"], a["role_takeaway"]))
            L.append("")
        quiz = s.get("quiz") or {}
        L.append("### ✅ Session %s Quiz" % s.get("session_number", s["day"]))
        L.append("")
        for qk, qlabel in (("q1", "Q1 (Multiple Choice)"), ("q2", "Q2 (Multiple Choice)")):
            q = quiz.get(qk)
            if not q:
                continue
            L.append("**%s:** %s" % (qlabel, q.get("stem", "")))
            for o in q.get("options", []):
                L.append("- %s" % o)
            L.append("")
            L.append("<details><summary>Show Answer</summary>")
            L.append("")
            L.append("**Correct: %s** — %s" % (q.get("correct", ""), q.get("explanation", "")))
            L.append("")
            L.append("</details>")
            L.append("")
        q3 = quiz.get("q3")
        if q3:
            L.append("**Q3 (Open-ended):** %s" % q3.get("prompt", ""))
            L.append("")
            L.append("<details><summary>Model answer for self-comparison</summary>")
            L.append("")
            L.append(q3.get("model_answer", ""))
            L.append("")
            L.append("</details>")
            L.append("")
        L.append("---")
        L.append("")
    return "\n".join(L)


def main():
    json_path = sys.argv[1] if len(sys.argv) > 1 else "curriculum.json"
    if not os.path.exists(json_path):
        sys.exit("build_html.py: curriculum file not found: %s" % json_path)
    out_dir = sys.argv[2] if len(sys.argv) > 2 else (os.path.dirname(os.path.abspath(json_path)) or ".")
    os.makedirs(out_dir, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        c = json.load(f)

    for key in ("product", "role", "product_slug", "role_slug", "sessions"):
        if key not in c:
            sys.exit("build_html.py: curriculum.json missing required key: %s" % key)

    slug = "%s-%s" % (c["product_slug"], c["role_slug"])
    modules = c.get("modules", [])
    sessions = c["sessions"]
    by_day = {s["day"]: s for s in sessions}

    # Inject product/role names into each session so component renderers can use them.
    for s in sessions:
        s.setdefault("product_name", c["product"])
        s.setdefault("role_name", c["role"])

    written = []
    manifest_days = []
    for day in range(1, 16):
        s = by_day.get(day)
        if s is None:
            sys.exit("build_html.py: curriculum.json missing session for day %d" % day)
        next_session = by_day.get(day + 1)
        page = build_day_html(c, s, modules, next_session)
        fname = "%s-day-%02d.html" % (slug, day)
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(page)
        written.append(fname)
        # Manifest session label
        if s.get("capstone") == "mc":
            label = "Capstone Quiz Part 1 (MC)"
        elif s.get("capstone") == "oe":
            label = "Capstone Quiz Part 2 (OE + Complete)"
        else:
            label = "Session %s: %s" % (s.get("session_number", day), s["title"])
        manifest_days.append({"day": day, "file": fname, "session": label})

    # manifest.json
    manifest = {
        "product": c["product"],
        "role": c["role"],
        "generated": c.get("generated", ""),
        "start_date": c.get("start_date", ""),
        "total_days": 15,
        "days": manifest_days,
    }
    manifest_name = "%s-manifest.json" % slug
    with open(os.path.join(out_dir, manifest_name), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # active-manifest.json pointer
    with open(os.path.join(out_dir, "active-manifest.json"), "w", encoding="utf-8") as f:
        json.dump({
            "manifest": manifest_name,
            "updated": c.get("generated", ""),
            "note": "Explicit active curriculum for deliver.py; prevents newest-manifest accidents.",
        }, f, indent=2, ensure_ascii=False)

    # quiz tracker (markdown)
    ts = c.get("timestamp", "")
    tracker_name = ("quiz-%s-%s.md" % (slug, ts)) if ts else ("quiz-%s.md" % slug)
    with open(os.path.join(out_dir, tracker_name), "w", encoding="utf-8") as f:
        f.write(quiz_tracker_md(c))

    # curriculum.md — human-readable study guide, generated from the same JSON.
    curriculum_name = "%s-curriculum.md" % slug
    with open(os.path.join(out_dir, curriculum_name), "w", encoding="utf-8") as f:
        f.write(curriculum_md(c))

    print("build_html.py: wrote %d day files + %s + active-manifest.json + %s + %s"
          % (len(written), manifest_name, tracker_name, curriculum_name))
    print("Output dir: %s" % out_dir)


if __name__ == "__main__":
    main()
