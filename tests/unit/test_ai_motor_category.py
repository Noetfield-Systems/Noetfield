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

CANONICAL_DEFINITION = (
    "An AI Motor is the governed execution vehicle. AI engines are the intelligence "
    "power units inside it. One Motor may run many engines; they are not the same thing."
)
JSON_LD_DEFINITION = (
    "An AI Motor is the governed execution vehicle that turns intent into verified "
    "outcomes. AI engines are intelligence power units inside the Motor — many engines "
    "can serve one Motor."
)
MEMORABLE_LINE = "Engines think. Models generate. Agents participate. Motors operate."


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


def test_homepage_introduces_the_category_before_the_portfolio() -> None:
    text = visible_text(HOME)
    motor_section = text.index('id="ai-motors"')
    portfolio_section = text.index('id="capabilities"')
    assert motor_section < portfolio_section
    assert "Noetfield builds AI Motors: governed execution systems" in text
    assert MEMORABLE_LINE in text
    assert text.count(f'<p class="nf-motor-manifesto">{MEMORABLE_LINE}</p>') == 1
    for component in ("AI engine", "Agent", "Workflow", "Automation", "AI Motor"):
        assert f"<span>{component}</span>" in text
    assert 'href="/motors/">Explore AI Motors' in text


def test_homepage_mental_model_does_not_put_ai_before_the_motor() -> None:
    text = visible_text(HOME)
    assert "Event or human intent" in text
    assert "Verified operational outcome" in text
    assert "governed execution runtime around intelligence" in text
    for forbidden in (
        "AI decides",
        "Motor executes",
        'AI capability</span><i aria-hidden="true">→</i><strong>Governed execution',
    ):
        assert forbidden not in text


def test_motors_page_uses_the_canonical_definition_and_role_hierarchy() -> None:
    text = visible_text(MOTORS)
    assert CANONICAL_DEFINITION in text
    assert JSON_LD_DEFINITION in text
    assert (
        "One Motor. Many engines. Engines think and draft. Agents take bounded tasks. "
        "Workflows are paths. The Motor advances, verifies, escalates and records."
    ) in text
    assert MEMORABLE_LINE in text
    assert text.count(MEMORABLE_LINE) == 1
    assert "One Motor. Many engines." in text
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
        "Policy",
        "Knowledge",
        "Authority",
        "Budget",
        "Execution orchestration",
        "Engines · Agents · Tools · Workflows",
        "Bounded execution environment",
        "Build · Act",
        "Verify · Repair",
        "Approve · Escalate",
        "Recover · Safe stop",
        "Promote and record evidence",
        "Verified operational outcome",
    )
    positions = [text.index(item) for item in required_in_order]
    assert positions == sorted(positions)
    assert 'id="architecture-description"' in text
    assert "Text equivalent:" in text


def test_motors_components_cover_control_execution_and_recovery() -> None:
    text = visible_text(MOTORS)
    for heading in (
        "Event intake",
        "Normalization & deduplication",
        "Policy & authority",
        "Knowledge & context",
        "Engine & agent orchestration",
        "Tool execution",
        "Cost & execution controls",
        "Bounded sandbox",
        "Verification & repair",
        "Escalation & human authority",
        "Recovery",
        "Promotion & evidence",
    ):
        assert f"<h3>{heading}</h3>" in text


def test_reference_lifecycle_and_failure_responses_are_complete() -> None:
    text = visible_text(MOTORS)
    lifecycle = (
        "Event",
        "Authenticate",
        "Normalize",
        "Resolve policy & authority",
        "Assemble knowledge & context",
        "Plan bounded execution",
        "Execute",
        "Verify",
        "Repair or escalate",
        "Approve & promote",
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
        "Verification",
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
    metadata = json.loads(read(METADATA))
    assert '<a href="/motors/">AI Motors</a>' in home
    assert '<a href="/motors/" aria-current="page">AI Motors</a>' in motors
    assert "Motor &amp; Custom Workflow" not in motors
    assert metadata["metadata_overrides"]["/"]["title"] == (
        "Noetfield Systems Inc. — AI Motors & Governed Execution"
    )
    assert metadata["metadata_overrides"]["/motors/"]["title"] == (
        "AI Motors for Governed Execution — Noetfield Systems"
    )
    assert (
        'property="og:image" content="https://www.noetfield.com/assets/social/noetfield-motors-v2.png"'
        in motors
    )
    defined_terms = [
        block["about"] for block in json_ld(MOTORS) if isinstance(block.get("about"), dict)
    ]
    assert any(term.get("name") == "AI Motor" for term in defined_terms)
    assert any(term.get("description") == JSON_LD_DEFINITION for term in defined_terms)


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
