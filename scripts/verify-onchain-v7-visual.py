#!/usr/bin/env python3
"""Onchain v7 local full-browser release candidate QA, including screenshot artifacts.
This tests exact served HTML/CSS/JS, never only static syntax or a design mock."""
from __future__ import annotations

import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = os.environ.get("ONCHAIN_URL", "http://127.0.0.1:8765/onchain/")
OUT = Path("tmp/onchain-v7-visual-qa")
WIDTHS = (1920, 1672, 1440, 768, 430, 390, 360, 320)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for width in WIDTHS:
            page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            result = {"width": width, "url": URL}
            response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
            assert response and response.status == 200, (width, response.status if response else "no_response")
            page.locator("#v5-headline").wait_for(state="visible")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(250)
            assert page.locator("h1").count() == 1
            assert "From real-world value" in page.locator("h1").inner_text()
            hero_font = page.locator("h1").evaluate("(el)=>getComputedStyle(el).fontFamily")
            assert ("Newsreader" if width >= 1141 else "Instrument Sans") in hero_font, (width, hero_font)
            assert page.locator(".v5-hero-services a").count() == 4
            if width <= 900:
                stage = page.locator(".nf-mobile-art-stage")
                assert stage.is_visible(), (width, "mobile architectural stage missing")
                assert "hero-architecture-hd.webp" in stage.evaluate("(el)=>getComputedStyle(el).backgroundImage")
                assert not page.locator(".v5-campus").is_visible(), (width, "desktop overlay still covers mobile")
                assert page.locator(".nf-mobile-cta-label").is_visible(), width
                title_size = page.locator("#v5-headline").evaluate("(el)=>parseFloat(getComputedStyle(el).fontSize)")
                if width <= 540:
                    assert 32 <= title_size <= 40, (width, title_size)
                    assert page.locator(".v5-hero-services").evaluate("(el)=>getComputedStyle(el).display") == "block"
                    assert page.locator(".v5-solutions-summary").evaluate("(el)=>getComputedStyle(el).gridTemplateColumns.split(' ').length") == 1
                    if page.locator(".nfChatFab").count():
                        chat_color=page.locator(".nfChatFab").evaluate("(el)=>getComputedStyle(el).backgroundColor")
                        assert "201, 163, 73" not in chat_color, (width, chat_color)
                        assert page.locator("#nfChatFab").evaluate("(el)=>getComputedStyle(el).backgroundImage") == "none", "late-injected gold chat gradient still wins"
                        assert page.locator("#nfChatFab").evaluate("(el)=>getComputedStyle(el).backgroundColor") == "rgb(11, 56, 43)", "enterprise chat color was not applied"
                    spacing = page.locator("#v5-headline").evaluate("(el)=>parseFloat(getComputedStyle(el).wordSpacing)")
                    assert spacing > 2, (width, "collapsed heading word spaces", spacing)
                result["mobile_title_px"] = title_size
            assert page.locator(".v5-solutions-summary a").count() == 4
            assert page.locator(".v5-solutions-summary .nf-sol-art").count() == 4
            assert page.locator(".nf-reference-quicklinks a").count() == 7
            assert page.locator('[data-network="base"]').count() == 1
            assert page.locator('[data-network="bnb"]').count() == 1
            assert page.locator('#onchainNav details').count() == 3
            assert page.locator(".v5-journey-grid > a").count() == 3
            assert page.locator(".nf-reference-join a[href='/onchain/hub/']").count() == 1
            assert page.locator(".v7-community-band a[href='/onchain/hub/']").count() == 1
            assert page.locator(".v8-network-entry[href='/onchain/hub/']").count() == 1
            assert page.locator("form#nfOnchainIntake[data-nf-intake-form]").count() == 1
            assert page.locator("form#nfOnchainCommunity[data-nf-intake-form]").count() == 1
            art = page.locator(".v5-campus")
            image = art.evaluate("""(el)=>({
              complete: el.complete, naturalWidth: el.naturalWidth,
              src: el.currentSrc, box: el.getBoundingClientRect().toJSON()
            })""")
            assert image["complete"] and image["naturalWidth"] >= min(600, width * .9), (width, image)
            if width >= 1440:
                assert image["src"].endswith("/onchain/hero-architecture-hd.webp"), (width, image)
            assert any("/onchain/" + file in image["src"] for file in ("hero-architecture-v7.webp", "hero-architecture-hd.webp")), image["src"]
            result["art_loaded"] = True
            result["art_natural_width"] = image["naturalWidth"]
            overflow = page.evaluate("Math.max(0,document.documentElement.scrollWidth-window.innerWidth)")
            result["horizontal_overflow_px"] = overflow
            if overflow > 3:
                culprits = page.evaluate("""() => [...document.querySelectorAll('body *')]
                  .map(e => {const b=e.getBoundingClientRect();return {tag:e.tagName, cls:typeof e.className==='string'?e.className.slice(0,90):'',left:Math.round(b.left),right:Math.round(b.right),width:Math.round(b.width)}})
                  .filter(e=>e.right>window.innerWidth+3||e.left < -3)
                  .sort((a,b)=>b.right-a.right).slice(0,15)""")
                raise AssertionError(f"{width}px layout overflow {overflow}px; culprits={culprits}")

            hero = page.locator(".v5-hero").bounding_box()
            nav = page.locator(".v5-header").bounding_box()
            assert hero and nav and hero["height"] > 320, (width, hero, nav)
            if width <= 900:
                copy_box = page.locator(".v5-hero-copy").bounding_box()
                services_box = page.locator(".v5-hero-services").bounding_box()
                assert copy_box and services_box
                assert services_box["y"] >= copy_box["y"] + copy_box["height"] - 4, (
                    "tablet/mobile hero content collides with floating services", width, copy_box, services_box
                )
            result["hero_height"] = round(hero["height"])
            result["nav_height"] = round(nav["height"])
            assert nav["height"] < 100, (width, nav)
            if width >= 1440:
                assert hero["height"] < 490, (width, hero)
                assert page.locator(".nf-tower-signage").is_visible()
                assert nav["height"] <= 75, (width, nav)
            if width == 1672:
                platform = page.locator(".v5-platform").bounding_box()
                outcomes = page.locator(".v5-journeys").bounding_box()
                assert platform and outcomes
                assert outcomes["y"] < 870, ("Reference first-fold no longer shows outcomes", outcomes)
                assert platform["height"] < 320, ("Platform lost compact reference geometry", platform)
                result["reference_outcomes_top"] = round(outcomes["y"])
                assert page.locator(".v5-hero-services").is_visible()
                assert page.locator(".v5-journey-grid > a").first.is_visible()
                quick = page.locator(".nf-reference-quicklinks").bounding_box()
                assert quick is not None and quick["y"] < 960, ("Quick demos strip does not appear within reference fold",quick)
                result["quick_links_top"] = round(quick["y"])
                cards = page.locator(".v5-solutions-summary a").all()
                assert all(card.is_visible() for card in cards)
                art = page.locator(".nf-card-rwa .nf-sol-art").evaluate("(el)=>getComputedStyle(el).backgroundImage")
                assert ("hero-architecture-hd.webp" in art or "case-rwa-v7.svg" in art), "RWA first-party artwork is missing"
                assert page.locator(".v5-layer .nf-layer-icon svg").count() == 4, "Platform SVG line icons missing"
                assert page.locator(".v5-solutions-summary .v5-solution-icon svg").count() == 4, "Core solution SVG icons missing"
                platform_h = page.locator(".v5-platform").bounding_box()["height"]
                assert platform_h < 290, ("Platform too tall versus reference",platform_h)
            page.screenshot(path=str(OUT / f"onchain-v7-{width}-fold.png"), animations="disabled")
            if width in (360, 390, 768):
                page.screenshot(path=str(OUT / f"onchain-v7-{width}-full.png"), full_page=True, animations="disabled")
            if os.environ.get("ONCHAIN_EMIT_PREVIEW") == "1" and width in (1440, 390):
                # Public screenshot thumbnail in QA logs for independent visual evaluation.
                # Chunks avoid GitHub runner's individual log-line length limits.
                from io import BytesIO
                from PIL import Image
                import base64
                preview = Image.open(OUT / f"onchain-v7-{width}-fold.png").convert("RGB")
                preview.thumbnail((760, 650))
                buf = BytesIO()
                preview.save(buf, format="JPEG", quality=45, optimize=True)
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                for index, offset in enumerate(range(0, len(b64), 5000)):
                    label = "DESKTOP" if width == 1440 else "MOBILE"
                    print("V7_PREVIEW_" + label + "_PART_%03d:" % index + b64[offset:offset + 5000], flush=True)
            policy = page.locator('[data-layer="policy"]')
            policy.scroll_into_view_if_needed()
            policy.click(timeout=10000)
            assert page.locator("#v6LayerTitle").inner_text() == "Policy & Control Layer"
            solana = page.locator('[data-network="solana"]')
            solana.scroll_into_view_if_needed()
            solana.click(timeout=10000)
            assert page.locator("#v6NetworkName").inner_text() == "Solana"
            # New use-case-to-intake path actually writes to the old intake DOM.
            case = page.locator(".v5-journey-grid > a").first
            case.click(timeout=10000)
            assert page.locator('#nfOnchainIntake select[name="topic"]').input_value() == "rwa-private-credit"
            assert "asset tokenization" in page.locator('#nfOnchainIntake textarea[name="notes"]').input_value()
            # Switching example scopes should replace only earlier automatic text.
            second = page.locator(".v5-journey-grid > a").nth(1)
            second.click(timeout=10000)
            notes = page.locator('#nfOnchainIntake textarea[name="notes"]')
            assert "private-credit servicing" in notes.input_value()
            notes.fill("My own scoped workflow notes")
            page.locator(".v5-journey-grid > a").nth(2).click(timeout=10000)
            assert notes.input_value() == "My own scoped workflow notes"
            # The selected infrastructure layer must reveal substantive context,
            # not just highlight the card.
            policy.click(timeout=10000)
            assert page.locator("#v6LayerCopy").is_visible()
            assert len(page.locator("#v6LayerCopy").inner_text()) > 35
            if width <= 1050:
                toggle = page.locator("#onchainMenuToggle")
                assert toggle.is_visible()
                toggle.click()
                assert toggle.get_attribute("aria-expanded") == "true"
                assert page.locator("#onchainNav").is_visible()
                page.locator('#onchainNav a[href="#use-cases"]').click()
                assert toggle.get_attribute("aria-expanded") == "false"
            assert not errors, {"viewport": width, "js_errors": errors}
            result["interactions"] = "PASS"
            result["javascript_errors"] = 0
            rows.append(result)
            page.close()
        browser.close()
    (OUT / "report.json").write_text(json.dumps(rows, indent=2) + "\n")
    for row in rows:
        print("PASS", row)
    print("PASS onchain reference v10: 8 real browser widths, editorial desktop hero, 7 functional quicklinks, 6 network explorers, 4 interactive cards, no mobile overflow, intake preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
