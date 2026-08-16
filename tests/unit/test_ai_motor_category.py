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
    "A Noetfield Motor runs only the work that was already allowed, and writes down what happened. "
    "Models and helpers can suggest the next step. Policy, identity, and budget decide whether that "
    "step is permitted. The Motor applies the permitted step. A separate check judges the result. "
    "Someone else decides what gets accepted."
)
MOTORS_JSON_LD_SNIPPET = (
    "Models can suggest work. Something else has to allow it. The Motor only runs what was allowed, "
    "writes down what happened, and does not mark its own homework."
)
MOTORS_DISTINCTION_LINE = (
    "The Motor runs inside a surrounding stack."
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
    assert "A separate check judges the result" in text
    assert (
        "A specialized skill such as search, scoring, planning, classification, or generation."
    ) in text
    assert (
        "A named way to do one kind of job, with rules for when to stop."
    ) in text
    for component in ("Model", "AI Engine", "Agent", "Workflow", "Tool", "Policy", "Human", "Runway", "AI Motor"):
        assert f"<span>{component}</span>" in text
    for forbidden in (
        "Tesla",
        "Tesla-class",
        "governs and executes the whole system",
        "Motor verifies, escalates",
        "decides what can continue",
        "Action Contracts",
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
    assert "Someone else decides what gets accepted" in text


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
    assert '<a href="/assurance/" aria-current="page">' in motors
    assert "Motor &amp; Custom Workflow" not in motors
    assert (
        'property="og:image" content="https://www.noetfield.com/assets/social/featured-motors-enterprise-v1.png"'
        in motors
    )
    assert 'og:title" content="AI Motors — How a run is allowed"' in motors
    blocks = json_ld(MOTORS)
    webpages = [block for block in blocks if block.get("@type") == "WebPage"]
    assert any(
        block.get("name") == "AI Motors — How a run is allowed"
        for block in webpages
    )
    assert "AI Motor" in motors
    assert MOTORS_JSON_LD_SNIPPET in motors


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
