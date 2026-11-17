"""Private synthetic training lab: no cross-tenant, payment or SMTP side effects."""
from __future__ import annotations

import asyncio
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from httpx import ASGITransport,AsyncClient
from noetfield_governance.api import app

HTML=Path(__file__).resolve().parents[2] / "services/governance/noetfield_governance/private_commercial_scenario_lab.html"


def test_training_lab_contains_two_separate_fictional_workflows_and_documents():
    body=HTML.read_text()
    for text in (
      "HarborBridge Private Credit Ltd. (fictional)",
      "Northshore Service Operations Ltd. (fictional)",
      "7816 Windsor Street",
      "Vancouver, BC V5X 4A8",
      'id="choose-rwa"', 'id="choose-company"',
      'id="case-fields"', 'id="technical-fields"',
      'id="stages"', 'id="doc-preview"', 'id="download-case"',
      "Statement of Work","Checkout example","WorkPacket contract",
      "Verifier receipt","Customer acceptance","Follow-up / renewal",
      "DEMO-NOT-A-STRIPE-EVENT",
      "false","SYNTHETIC · TRAINING ONLY",
    ):
        assert text in body, text


def test_training_page_never_stores_or_submits_real_actions():
    body=HTML.read_text()
    assert "localStorage" not in body
    assert "sessionStorage" not in body
    assert 'fetch(' not in body
    assert "XMLHttpRequest" not in body
    assert "sendBeacon" not in body
    assert "cs_live_" not in body
    assert "window.location.assign" not in body
    assert "content=" + '"noindex,nofollow,noarchive"' in body
    assert "FICTIONAL" in body


def test_inline_simulator_javascript_parses_with_node():
    body=HTML.read_text()
    scripts=re.findall(r"<script>([\s\S]*?)</script>",body)
    assert len(scripts)==1
    with NamedTemporaryFile(mode="w",suffix=".js") as file:
        file.write(scripts[0]);file.flush()
        subprocess.run(["node","--check",file.name],check=True,capture_output=True,text=True)


def test_private_lab_denies_guest_and_is_strictly_noindex():
    async def exercise():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            guest=await client.get("/api/corporate-crm/scenario-lab")
            assert guest.status_code in (403,503)
            with patch("noetfield_governance.api._require_connect_desk_operator",return_value=None):
                authorized=await client.get("/api/corporate-crm/scenario-lab")
                assert authorized.status_code==200
                assert "noindex" in authorized.headers["x-robots-tag"]
                assert "no-store" in authorized.headers["cache-control"]
                assert "frame-ancestors" in authorized.headers["content-security-policy"]
                assert "HarborBridge" in authorized.text
    asyncio.run(exercise())


def test_existing_crm_has_real_navigation_to_demo_and_no_data_mix():
    root=HTML.parent
    crm=(root/"private_corporate_crm.html").read_text()
    assert '<a href="/api/corporate-crm/scenario-lab">' in crm
    assert "HarborBridge" not in crm
    assert "Northshore Service Operations" not in crm
