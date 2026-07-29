#!/usr/bin/env python3
"""Repair motors/index.html — Motor boundary language (work order v1)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "motors" / "index.html"

REPLACEMENTS = [
    (
        'content="What an AI Motor is, how it coordinates models, agents, tools, policy and human authority, and how it verifies, escalates, recovers and records outcomes."',
        'content="The deterministic execution layer for agentic systems. Motor executes authorized Action Contracts; the Brain and harness propose; the control plane resolves authority; a separate Verifier judges evidence."',
    ),
    (
        'content="Noetfield Custom AI Motors — systems that turn intent, policy, tools and authority into coordinated execution."',
        'content="Noetfield AI Motors — deterministic execution of authorized Action Contracts with recorded effect evidence."',
    ),
    (
        '"description": "A category guide to Noetfield AI Motors and the governed execution runtime around models, agents, tools, workflows and human authority."',
        '"description": "Noetfield Motor executes authorized Action Contracts inside a governed runtime. The Brain and harness reason and propose; the Kernel resolves policy, authority and budget; Motor records effects; a Verifier judges evidence."',
    ),
    (
        '"description": "An AI Motor is a governed execution runtime that turns authenticated events and human intent into controlled outcomes verified against defined acceptance criteria. It coordinates models, specialized engines, agents, tools, policies, organizational knowledge, versioned runways, workflows, and human authority."',
        '"description": "A Noetfield Motor deterministically executes authorized Action Contracts inside a durable governed runtime. It enforces execution invariants, deduplicates, retries within a permit, stops, recovers, and records effect evidence. It does not reason, verify, approve, or promote."',
    ),
    (
        '<div class="nf-motor-hero-card__node">Controlled outcome verified against acceptance criteria</div>',
        '<div class="nf-motor-hero-card__node">Effect evidence recorded for independent verification</div>',
    ),
    (
        '<ul aria-label="Capabilities the Motor may coordinate">',
        '<ul aria-label="Surrounding stack Motor executes within">',
    ),
    (
        '<p>A Motor owns the lifecycle from an authenticated event or human instruction to an accepted, recorded operational outcome.</p>',
        '<p>A Motor owns deterministic execution from an authorized Action Contract to recorded effect evidence. Acceptance, verification, and promotion sit outside Motor.</p>',
    ),
    (
        '<p>An AI Motor is a governed execution runtime that turns authenticated events and human intent into controlled outcomes verified against defined acceptance criteria. It coordinates models, specialized engines, agents, tools, policies, organizational knowledge, versioned runways, workflows, and human authority.</p>',
        '<p>A Noetfield Motor executes authorized Action Contracts inside a durable governed runtime. The Brain and agent harness reason, assemble context, and propose work. The Kernel control plane resolves policy, authority, budget, and state. Motor applies the permitted effect and records evidence. A separate Verifier judges the result. Promotion authority remains outside Motor.</p>',
    ),
    (
        '<article class="nf-motor-hierarchy__motor" role="listitem"><span>AI Motor</span><p>Coordinates and executes under contract—engines provide capability; the Motor verifies, escalates, recovers and records.</p></article>',
        '<article class="nf-motor-hierarchy__motor" role="listitem"><span>AI Motor</span><p>Executes authorized contracts—enforces invariants, deduplicates, retries within permit, stops, recovers, and records effects.</p></article>',
    ),
    (
        '<p><strong>A Motor may coordinate models, engines, agents, runways and workflows under one execution contract.</strong> Engines provide capability. Agents perform bounded tasks. Runways qualify outcomes. Workflows are paths. The Motor operates under contract and decides what can continue, stop, escalate, recover or be promoted.</p>',
        '<p><strong>Motor executes within a surrounding stack.</strong> The Brain and harness propose. The Kernel resolves policy and authority. Engines and agents supply bounded capability. Runways qualify outcomes. Workflows are paths. Motor applies permitted effects. A Verifier judges evidence. Promotion authority remains outside Motor.</p>',
    ),
    (
        '<div class="nf-motor-architecture__guardrails"><span>Policy</span><span>Knowledge</span><span>Authority</span><span>Budget</span></div>',
        '<div class="nf-motor-architecture__guardrails"><span>Kernel · Policy</span><span>Authority</span><span>Budget</span><span>State</span></div>',
    ),
    (
        '<div class="nf-motor-architecture__controls"><span>Build · Act</span><span>Verify · Repair</span><span>Approve · Escalate</span><span>Recover · Safe stop</span></div>',
        '<div class="nf-motor-architecture__controls"><span>Motor · Execute</span><span>Enforce invariants</span><span>Verifier · Judge</span><span>Recover · Safe stop</span></div>',
    ),
    (
        '<div class="nf-motor-architecture__stage"><strong>Promote and record evidence</strong><span>Accepted artifact or operational change · verification receipt · evidence boundary</span></div>',
        '<div class="nf-motor-architecture__stage"><strong>Verifier judgment and evidence record</strong><span>Independent verdict · execution receipt · evidence boundary · promotion outside Motor</span></div>',
    ),
    (
        '<div class="nf-motor-architecture__stage nf-motor-architecture__output"><strong>Controlled outcome verified against acceptance criteria</strong><span>Accepted, blocked, escalated or safely recovered</span></div>',
        '<div class="nf-motor-architecture__stage nf-motor-architecture__output"><strong>Recorded effect with stated evidence boundary</strong><span>Accepted, blocked, escalated, or safely recovered — per Verifier verdict</span></div>',
    ),
    (
        '<figcaption id="architecture-description">Text equivalent: an authenticated event or human instruction enters a gateway, is evaluated against policy, knowledge, authority and budget, then proceeds through bounded model, agent, tool and workflow execution. The Motor verifies, repairs, escalates or recovers before an accepted outcome is promoted and recorded.</figcaption>',
        '<figcaption id="architecture-description">Text equivalent: an authenticated event enters a gateway. The Kernel resolves policy, authority, and budget. The Brain and harness propose bounded work. Motor executes the authorized Action Contract, enforces invariants, and records effects. A separate Verifier judges evidence. Promotion authority remains outside Motor.</figcaption>',
    ),
    (
        '<article><span>03</span><h3>Policy &amp; authority</h3><p>Determines what may execute, under whose authority, within which limits and when approval is required.</p></article>',
        '<article><span>03</span><h3>Kernel · policy &amp; authority</h3><p>The control plane resolves what may execute, under whose authority, within which limits, and when human approval is required — before Motor runs.</p></article>',
    ),
    (
        '<article><span>05</span><h3>Model &amp; agent orchestration</h3><p>Selects models and coordinates agents as bounded workers, not unrestricted autonomous authorities.</p></article>',
        '<article><span>05</span><h3>Harness · model &amp; agent routing</h3><p>The Brain and harness assemble context and route bounded workers — they propose work; Motor does not reason or select goals.</p></article>',
    ),
    (
        '<article><span>09</span><h3>Verification &amp; repair</h3><p>Checks objectives, policies, tests and evidence requirements, then repairs where permitted.</p></article>',
        '<article><span>09</span><h3>Verifier · judgment</h3><p>An independent Verifier checks objectives, policies, tests, and evidence requirements. Motor may retry or recover only within an authorized permit.</p></article>',
    ),
    (
        '<article><span>12</span><h3>Promotion &amp; evidence</h3><p>Promotes accepted work and produces an inspectable record of scope, authority, checks and outcome.</p></article>',
        '<article><span>12</span><h3>Evidence record</h3><p>Motor records execution effects and returns evidence. Promotion of accepted work requires authority outside Motor.</p></article>',
    ),
    (
        '<li data-step="04"><strong>Resolve policy &amp; authority</strong><span>Determine limits and decision rights.</span></li>',
        '<li data-step="04"><strong>Kernel resolves policy &amp; authority</strong><span>Control plane determines limits and decision rights before execution.</span></li>',
    ),
    (
        '<li data-step="08"><strong>Verify</strong><span>Check result, policy, tests and evidence.</span></li>',
        '<li data-step="08"><strong>Verifier judges</strong><span>Independent check of result, policy, tests, and evidence.</span></li>',
    ),
    (
        '<li data-step="10"><strong>Approve &amp; promote</strong><span>Request human authority where required.</span></li>',
        '<li data-step="10"><strong>Authority promotes</strong><span>Human or control-plane promotion where policy requires — outside Motor.</span></li>',
    ),
    (
        '<p>A Motor may produce a machine-readable verification receipt, operational trace or execution record. The exact evidence depends on the implementation and risk boundary.</p>',
        '<p>Motor may produce a machine-readable execution receipt or operational trace of effects it applied. Verification verdicts come from a separate Verifier. The exact evidence depends on implementation and risk boundary.</p>',
    ),
    (
        '<div><dt>Verification</dt><dd>Checks performed and result</dd></div>',
        '<div><dt>Verifier</dt><dd>Independent checks and verdict</dd></div>',
    ),
    (
        '<div><dt>Outcome</dt><dd>Promoted, blocked or escalated</dd></div>',
        '<div><dt>Outcome</dt><dd>Recorded effect — promotion authority external</dd></div>',
    ),
    (
        '<li>Promote only the accepted change and produce an execution receipt.</li>',
        '<li>Record execution effects; promotion of accepted change requires authority outside Motor.</li>',
    ),
]


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS:
        if old not in text:
            raise SystemExit(f"missing expected fragment: {old[:80]}...")
        text = text.replace(old, new, 1)
    PATH.write_text(text, encoding="utf-8")
    print("repaired", PATH)


if __name__ == "__main__":
    main()
