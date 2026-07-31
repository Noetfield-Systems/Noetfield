"""NF-WEB-MOTOR-CATEGORY-001 category, claims, and presentation contracts."""

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / "index.html"
MOTORS = ROOT / "motors" / "index.html"
CSS = ROOT / "assets" / "noetfield-corporate-v1.css"
METADATA = ROOT / "data" / "noetfield-social-preview-v2.json"

MOTORS_DEFINITION = (
    "A Noetfield Motor executes authorized Action Contracts inside a durable governed runtime. "
    "The Brain and agent harness reason, assemble context, and propose work. The Kernel control plane "
    "resolves policy, authority, budget, and state. Motor applies the permitted effect and records "
    "evidence. A separate Verifier judges the result. Promotion authority remains outside Motor."
)
MOTORS_JSON_LD_SNIPPET = (
    "A Noetfield Motor deterministically executes authorized Action Contracts inside a durable "
    "governed runtime."
)
MOTORS_DISTINCTION_LINE = (
    "Motor executes within a surrounding stack."
)
MOTORS_MEMORABLE_LINE = "Models generate. Agents participate. Motors operate."


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def visible_text(path: Path) -> str:
    return unescape(read(path))


def json_ld(path: Path) -> list[dict[str, object]]:
    blocks = re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        read(path),
        flags=re.DOTALL,
    )
    return [json.loads(block) for block in blocks]


def test_homepage_introduces_the_category_before_other_sections() -> None:
    text = visible_text(HOME)
    hero = text.index('id="hero-title"')
    walkthrough = text.index('id="walk-title"')
    evidence = text.index('id="ev-title"')
    assert hero < walkthrough < evidence
    assert "AI Motors provide the governed execution layer behind the product." in text
    assert '<a href="/system/">' in text
    assert '<a href="/applications/">' in text
    assert "/assets/noetfield-home-v2.css" in text


def test_homepage_mental_model_does_not_put_ai_before_the_motor() -> None:
    text = visible_text(HOME)
    assert "Capable AI is not the same as accountable execution." in text
    assert "Authorized goal" in text
    assert "Bounded execution" in text
    for forbidden in (
        "AI decides",
        "Motor verifies its own",
        "Verified operational outcome",
        "Motors govern execution",
        "SourceB",
    ):
        assert forbidden not in text


def test_motors_page_uses_the_canonical_definition_and_role_hierarchy() -> None:
    text = visible_text(MOTORS)
    assert MOTORS_DEFINITION in text
    assert MOTORS_DISTINCTION_LINE in text
    assert MOTORS_MEMORABLE_LINE in text
    assert text.count(MOTORS_MEMORABLE_LINE) == 1
    assert "independent verifier judges the result" in text
    assert (
        "Provides a specialized intelligence or decision capability—such as "
        "inference, retrieval, rules, scoring, planning, classification, or generation."
    ) in text
    assert (
        "A versioned execution path for a defined class of outcome, including its "
        "input contract, authority requirements, acceptance criteria, verification, "
        "repair limits, stop conditions, and receipt."
    ) in text
    for component in ("Model", "AI Engine", "Agent", "Workflow", "Tool", "Policy", "Human", "Runway", "AI Motor"):
        assert f"<span>{component}</span>" in text
    for forbidden in (
        "Tesla",
        "Tesla-class",
        "governs and executes the whole system",
        "Motor verifies, escalates",
        "decides what can continue",
    ):
        assert forbidden not in text
    assert text.count("<h1") == 1


def test_motors_architecture_preserves_governance_around_execution() -> None:
    page = visible_text(MOTORS)
    match = re.search(
        r'<figure class="nf-motor-architecture".*?</figure>',
        page,
        flags=re.DOTALL,
    )
    assert match
    text = match.group(0)
    required_in_order = (
        "Events and human intent",
        "Gateway",
        "Kernel · Policy",
        "Authority",
        "Budget",
        "Execution orchestration",
        "Models · Agents · Tools · Workflows",
        "Bounded execution environment",
        "Motor · Execute",
        "Verifier · Judge",
        "Recover · Safe stop",
        "Verifier judgment and evidence record",
        "Recorded effect with stated evidence boundary",
    )
    positions = [text.index(item) for item in required_in_order]
    assert positions == sorted(positions)
    assert 'id="architecture-description"' in text
    assert "Promotion authority remains outside Motor" in text


def test_motors_components_cover_control_execution_and_recovery() -> None:
    text = visible_text(MOTORS)
    for heading in (
        "Event intake",
        "Normalization & deduplication",
        "Kernel · policy & authority",
        "Knowledge & context",
        "Harness · model & agent routing",
        "Tool execution",
        "Cost & execution controls",
        "Bounded sandbox",
        "Verifier · judgment",
        "Escalation & human authority",
        "Recovery",
        "Evidence record",
    ):
        assert f"<h3>{heading}</h3>" in text


def test_reference_lifecycle_and_failure_responses_are_complete() -> None:
    text = visible_text(MOTORS)
    lifecycle = (
        "Event",
        "Authenticate",
        "Normalize",
        "Kernel resolves policy & authority",
        "Assemble knowledge & context",
        "Plan bounded execution",
        "Execute",
        "Verifier judges",
        "Repair or escalate",
        "Authority promotes",
        "Produce evidence receipt",
    )
    positions = [text.index(f"<strong>{step}</strong>") for step in lifecycle]
    assert positions == sorted(positions)
    for response in (
        "Continue",
        "Stop",
        "Retry",
        "Repair",
        "Isolate",
        "Escalate",
        "Recover",
        "Request approval",
    ):
        assert f"<li>{response}</li>" in text


def test_evidence_and_client_zero_copy_preserve_claim_boundaries() -> None:
    text = visible_text(MOTORS)
    for receipt_field in (
        "Trigger",
        "Scope",
        "Policy",
        "Workers",
        "Authority",
        "Verifier",
        "Outcome",
        "Evidence boundary",
    ):
        assert f"<dt>{receipt_field}</dt>" in text
    assert "internal operating model" in text
    assert "not an external customer case study" in text
    assert (
        "No external customer adoption, broad production proof or independent "
        "validation is claimed."
    ) in text
    for unsupported in (
        "fully autonomous enterprise",
        "proven at scale",
        "production-proven across clients",
        "industry-leading",
        "guaranteed compliance",
        "zero-risk automation",
    ):
        assert unsupported not in text.lower()


def test_navigation_metadata_and_structured_data_name_ai_motors() -> None:
    home = read(HOME)
    motors = read(MOTORS)
    assert '<a href="/system/">' in home
    assert '<a href="/motors/" aria-current="page">' in motors
    assert "Motor &amp; Custom Workflow" not in motors
    assert (
        'property="og:image" content="https://www.noetfield.com/assets/social/noetfield-motors-v2.png"'
        in motors
    )
    defined_terms = [
        block["about"] for block in json_ld(MOTORS) if isinstance(block.get("about"), dict)
    ]
    assert any(term.get("name") == "AI Motor" for term in defined_terms)
    assert any(MOTORS_JSON_LD_SNIPPET in str(term.get("description", "")) for term in defined_terms)


def test_motor_layout_has_narrow_width_and_reduced_motion_contracts() -> None:
    css = read(CSS)
    for selector in (
        ".nf-motor-architecture",
        ".nf-motor-component-grid",
        ".nf-motor-lifecycle",
        ".nf-motor-response-list",
    ):
        assert selector in css
    assert "@media (max-width: 760px)" in css
    assert "@media (max-width: 480px)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert (
        ".nf-motor-comparison, .nf-motor-hierarchy, .nf-motor-component-grid, "
        ".nf-motor-lifecycle, .nf-motor-use-grid { grid-template-columns: 1fr; }"
    ) in css
