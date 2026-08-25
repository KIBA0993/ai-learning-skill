#!/usr/bin/env python3
"""
test_build.py — P0 enforcement tests for build_html.py.

Verifies that the deterministic builder:
  * still builds a legacy curriculum (no mechanism_map) with a warning,
  * builds a valid mechanism-first curriculum cleanly, and
  * REFUSES (non-zero exit) each P0 violation: a Terms/legal/pricing/home page or
    role=excluded_type assigned as a learner source, a missing Day 1 trace, a
    'confirmed' mechanism claim with no evidence URL, and a wrong mechanism_map size.

Also writes the valid mechanism-first curriculum to
scripts/fixtures/sample-curriculum-mechanism.json as a reference example.

Run:  python3 scripts/test_build.py      (exit 0 = all passed)
"""

import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BUILDER = os.path.join(HERE, "build_html.py")
LEGACY_FIXTURE = os.path.join(HERE, "fixtures", "sample-curriculum.json")
MECH_FIXTURE = os.path.join(HERE, "fixtures", "sample-curriculum-mechanism.json")


def run_builder(curriculum):
    """Write curriculum to a temp dir, run the builder, return (returncode, stdout+stderr)."""
    d = tempfile.mkdtemp()
    path = os.path.join(d, "curriculum.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(curriculum, f)
    proc = subprocess.run([sys.executable, BUILDER, path, d],
                          capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr), d


def make_mechanism_curriculum():
    """Build a valid mechanism-first curriculum by enriching the legacy fixture."""
    with open(LEGACY_FIXTURE, "r", encoding="utf-8") as f:
        c = json.load(f)
    c["product"] = "Polsia"
    c["product_slug"] = "polsia"

    c["mechanism_map"] = [
        {
            "id": "m1",
            "learner_question": "How does a request become a deployed website with no human team?",
            "product_promise": "Turns a plain-language goal into a live, hosted service.",
            "observable_behavior": "You describe a product; a working URL appears with code in a repo.",
            "mechanism": "A planner decomposes the goal into a task backlog; an approval/autonomy "
                         "gate promotes a task; a specialist agent works in a sandbox producing "
                         "code + tests; a repo is created/updated; database and hosting are "
                         "provisioned via authorized APIs; deployment yields a provider URL; "
                         "logs and outcomes feed the next planning cycle.",
            "traditional_counterfactual": "A PM writes a spec, eng builds, DevOps provisions and "
                                          "deploys — four handoffs across days.",
            "autonomy_boundary": "Provider subdomains deploy automatically via pre-authorized "
                                 "accounts; custom domains, budget, and high-risk actions stay "
                                 "human-gated.",
            "failure_mode": "A task can fail in the sandbox or at deploy; the system should surface "
                            "the failure and hold the affected task rather than ship a broken build.",
            "evidence": {
                "urls": ["https://github.com/AI-Builder-Club/open-polsia/blob/main/docs/architecture.md"],
                "note": "Public reference-implementation analogue (planner, queue, sandbox, GitHub, "
                        "Neon Postgres, Render, public URL) — not proof of the private stack.",
                "confidence": "inferred",
            },
        },
        {
            "id": "m2",
            "learner_question": "What keeps an autonomous agent from taking unsafe actions?",
            "product_promise": "Automation acts only through pre-authorized accounts and policies.",
            "observable_behavior": "Tasks pause at an approval gate before high-risk steps.",
            "mechanism": "Credentials, budgets, and permissions are scoped per integration; the "
                         "autonomy gate promotes only tasks within policy.",
            "traditional_counterfactual": "An engineer manually holds credentials and runs each "
                                          "privileged step by hand.",
            "autonomy_boundary": "Routine actions are automated; anything touching money, custom "
                                 "domains, or production data requires explicit approval.",
            "failure_mode": "An over-broad credential scope could let an agent act beyond intent; "
                            "policy scoping is the control.",
            "evidence": {
                "urls": ["https://www.anthropic.com/engineering/building-effective-agents"],
                "note": "Canonical treatment of agent guardrails and human intervention.",
                "confidence": "inferred",
            },
        },
        {
            "id": "m3",
            "learner_question": "Is end-to-end autonomy actually reliable enough to trust?",
            "product_promise": "The loop improves each cycle from tests, logs, and outcomes.",
            "observable_behavior": "Failed tasks are retried or flagged; successful ones inform planning.",
            "mechanism": "Test results, logs, and analytics are fed back into the next planning cycle.",
            "traditional_counterfactual": "A team manually reviews CI and postmortems between releases.",
            "autonomy_boundary": "The feedback loop is automated; the decision to trust it for "
                                 "high-stakes launches remains human.",
            "failure_mode": "Silent quality regressions if evaluation signals are weak.",
            "evidence": {
                "urls": [],
                "note": "No independent benchmark of reliability located for this early-stage product.",
                "confidence": "unknown",
            },
            "high_impact": True,
        },
    ]

    # Enrich Days 1–5 with the lesson contract; tag their sources with roles.
    contracts = {
        1: {
            "artifact": "A provider URL plus a Git repository of generated code and tests.",
            "counterfactual": "Spec → build → deploy across a PM, an engineer, and DevOps.",
            "autonomy_boundary": "Subdomain deploys auto-run; custom domains stay human-gated.",
            "role_decision": "Decide which task types you pre-authorize vs. gate for approval.",
        },
        2: {
            "artifact": "The task backlog the planner produces from a goal.",
            "counterfactual": "A PM hand-writes tickets and assigns owners.",
            "autonomy_boundary": "The planner drafts tasks; promotion past the gate is controlled.",
            "role_decision": "Choose the promotion criteria for the autonomy gate.",
        },
        3: {
            "artifact": "An approval record on a gated task.",
            "counterfactual": "A lead manually reviews and green-lights risky changes.",
            "autonomy_boundary": "Low-risk tasks auto-promote; high-risk ones require sign-off.",
            "role_decision": "Define which actions always require a human approver.",
        },
        4: {
            "artifact": "A deployment log with latency/cost figures.",
            "counterfactual": "DevOps provisions infra and tunes it by hand.",
            "autonomy_boundary": "Provisioning is automated within budget scopes you set.",
            "role_decision": "Set the cost/latency budget the automation must respect.",
        },
        5: {
            "artifact": "A side-by-side of two agentic products on the same task.",
            "counterfactual": "Analysts compile a manual competitive teardown.",
            "autonomy_boundary": "Comparison is drawn from observable behavior, not private stacks.",
            "role_decision": "Pick the mechanism-level axis that actually differentiates them.",
        },
    }
    by_day = {s["day"]: s for s in c["sessions"]}
    for day, fields in contracts.items():
        s = by_day[day]
        s.update(fields)
        # Tag existing sources with roles; the arXiv paper backs the mechanism, MDN is independent.
        srcs = s.get("sources") or []
        if len(srcs) >= 1:
            srcs[0]["role"] = "mechanism_evidence"
            srcs[0]["supports_claim"] = "m1"
            srcs[0]["why_it_matters"] = "Explains the underlying architecture pattern."
            srcs[0]["reading_order"] = 1
        if len(srcs) >= 2:
            srcs[1]["role"] = "independent_validation"
            srcs[1]["supports_claim"] = "m3"
            srcs[1]["why_it_matters"] = "Independent reference, not the vendor's own framing."
            srcs[1]["reading_order"] = 2

    # Day 1 contract additions.
    d1 = by_day[1]
    d1["end_to_end_trace"] = [
        "You give Polsia a company brief and constraints.",
        "The planner turns the goal into a suggested task backlog.",
        "An approval/autonomy gate promotes a task.",
        "A specialist agent works in a sandbox and produces code + tests.",
        "A repository is created or updated.",
        "Database and hosting are provisioned via authorized APIs.",
        "Deployment creates a provider URL.",
        "Tests, logs, and outcomes feed the next planning cycle.",
    ]
    d1["residual_human_work"] = ("The original goal, credentials, budget, custom-domain ownership, "
                                 "and any high-risk action remain human-controlled.")
    return c


def expect(name, cond):
    status = "PASS" if cond else "FAIL"
    print("  [%s] %s" % (status, name))
    return cond


def main():
    ok = True

    print("Legacy fixture still builds (with warning):")
    rc, out, _ = run_builder(json.load(open(LEGACY_FIXTURE, encoding="utf-8")))
    ok &= expect("legacy builds (rc=0)", rc == 0)
    ok &= expect("legacy warns about missing mechanism_map", "LEGACY mode" in out)

    mech = make_mechanism_curriculum()

    print("Valid mechanism-first curriculum builds cleanly:")
    rc, out, _ = run_builder(mech)
    ok &= expect("mechanism-first builds (rc=0)", rc == 0)
    ok &= expect("runs in mechanism_first mode", "mechanism_first mode" in out)
    ok &= expect("zero errors", "0 error(s)" in out)

    print("P1: Days 1–5 lesson contract is hard-required in mechanism_first mode:")
    bad = copy.deepcopy(mech)
    del bad["sessions"][2]["artifact"]        # Day 3 loses its artifact
    rc, out, _ = run_builder(bad)
    ok &= expect("build refused (rc!=0)", rc != 0)
    ok &= expect("names Day 3 + the field", "Day 3 missing lesson-contract field 'artifact'" in out)

    print("P1: same omission is only a warning under 'standard' progression:")
    soft = copy.deepcopy(mech)
    soft["progression"] = "standard"
    del soft["sessions"][2]["artifact"]
    rc, out, _ = run_builder(soft)
    ok &= expect("standard build still succeeds (rc=0)", rc == 0)
    ok &= expect("runs in standard mode", "standard mode" in out)

    print("Violation: Terms of Service assigned as a learner source is rejected:")
    bad = copy.deepcopy(mech)
    bad["sessions"][0]["sources"].append(
        {"title": "Terms of Service", "url": "https://polsia.com/terms", "role": "context_discovery"})
    rc, out, _ = run_builder(bad)
    ok &= expect("build refused (rc!=0)", rc != 0)
    ok &= expect("names the Terms page", "Terms of Service" in out)

    print("Violation: homepage assigned as a learner source is rejected:")
    bad = copy.deepcopy(mech)
    bad["sessions"][1]["sources"].append({"title": "Polsia", "url": "https://polsia.com/"})
    rc, out, _ = run_builder(bad)
    ok &= expect("build refused (rc!=0)", rc != 0)
    ok &= expect("names the homepage", "Homepage" in out)

    print("Violation: role=excluded_type learner source is rejected:")
    bad = copy.deepcopy(mech)
    bad["sessions"][2]["sources"].append(
        {"title": "Pricing", "url": "https://polsia.com/plan-details", "role": "excluded_type"})
    rc, out, _ = run_builder(bad)
    ok &= expect("build refused (rc!=0)", rc != 0)
    ok &= expect("names excluded_type", "excluded_type" in out)

    print("Violation: Day 1 missing end_to_end_trace is rejected:")
    bad = copy.deepcopy(mech)
    del bad["sessions"][0]["end_to_end_trace"]
    rc, out, _ = run_builder(bad)
    ok &= expect("build refused (rc!=0)", rc != 0)
    ok &= expect("names the trace requirement", "end_to_end_trace" in out)

    print("Violation: 'confirmed' claim with no evidence URL is rejected:")
    bad = copy.deepcopy(mech)
    bad["mechanism_map"][0]["evidence"]["confidence"] = "confirmed"
    bad["mechanism_map"][0]["evidence"]["urls"] = []
    rc, out, _ = run_builder(bad)
    ok &= expect("build refused (rc!=0)", rc != 0)
    ok &= expect("names the confirmed-without-URL rule", "no evidence URL" in out)

    print("Violation: mechanism_map with fewer than 3 claims is rejected:")
    bad = copy.deepcopy(mech)
    bad["mechanism_map"] = bad["mechanism_map"][:2]
    rc, out, _ = run_builder(bad)
    ok &= expect("build refused (rc!=0)", rc != 0)
    ok &= expect("names the 3–5 rule", "3–5 entries" in out)

    # Write the valid mechanism-first curriculum as a reference fixture.
    with open(MECH_FIXTURE, "w", encoding="utf-8") as f:
        json.dump(mech, f, indent=2, ensure_ascii=False)
    print("Wrote reference fixture: %s" % os.path.relpath(MECH_FIXTURE, os.path.dirname(HERE)))

    print("\n%s" % ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
