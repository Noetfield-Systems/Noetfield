#!/usr/bin/env python3
"""Read-only live /onchain/ visual QA. Screenshots plus real interaction assertions."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

OUTPUT = Path("tmp/onchain-v6-visual-qa")
URL = os.environ.get("ONCHAIN_URL", "https://www.noetfield.com/onchain/")
VIEWPORTS = (1920, 1440, 768, 390)


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    findings: list[dict[str, object]] = []
    errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for width in VIEWPORTS:
            page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
            result: dict[str, object] = {"viewport": width, "url": URL}
            try:
                response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                result["http_status"] = response.status if response else None
                if response is None or response.status >= 400:
                    raise AssertionError(f"HTTP status {result['http_status']}")
                page.locator("#v5-headline").wait_for(state="visible", timeout=18000)
                page.evaluate("document.fonts.ready")
                result["headline"] = page.locator("#v5-headline").inner_text()
                result["document_width"] = page.evaluate("document.documentElement.scrollWidth")
                result["viewport_inner_width"] = page.evaluate("window.innerWidth")
                result["horizontal_overflow_px"] = max(0, int(result["document_width"]) - int(result["viewport_inner_width"]))
                if result["horizontal_overflow_px"] > 3:
                    raise AssertionError(f"horizontal overflow {result['horizontal_overflow_px']} px")
                assert page.locator("h1").count() == 1, "expected one H1"
                assert page.locator(".v5-actions a[href='#project']").count() == 1, "missing sales CTA"
                assert page.locator("a[href='/onchain/hub/']").count() >= 1, "missing first-party wallet Hub"
                assert page.locator("[data-layer]").count() == 4, "four operating layers required"
                assert page.locator("[data-network]").count() == 5, "five network explorations required"
                # Capture the actual first fold before interacting.
                page.screenshot(path=str(OUTPUT / f"onchain-{width}-first-fold.png"), animations="disabled")
                policy = page.locator('[data-layer="policy"]')
                policy.scroll_into_view_if_needed()
                policy.click(timeout=10000)
                assert page.locator("#v6LayerTitle").inner_text() == "Policy & Control Layer"
                assert policy.get_attribute("aria-pressed") == "true"
                solana = page.locator('[data-network="solana"]')
                solana.scroll_into_view_if_needed()
                solana.click(timeout=10000)
                assert page.locator("#v6NetworkName").inner_text() == "Solana"
                assert solana.get_attribute("aria-pressed") == "true"
                result["interactive_layers"] = "PASS"
                result["interactive_networks"] = "PASS"
                if width <= 1050:
                    trigger = page.locator("#onchainMenuToggle")
                    assert trigger.is_visible(), "mobile menu not visible"
                    trigger.click()
                    assert trigger.get_attribute("aria-expanded") == "true"
                    assert page.locator("#onchainNav").is_visible()
                    page.locator('#onchainNav a[href="#solutions"]').click()
                    assert trigger.get_attribute("aria-expanded") == "false"
                    result["mobile_navigation"] = "PASS"
                if width in (1440, 390):
                    page.screenshot(path=str(OUTPUT / f"onchain-{width}-full-page.png"), full_page=True, animations="disabled")
                result["status"] = "PASS"
            except (AssertionError, PlaywrightTimeoutError, Exception) as exc:
                result["status"] = "FAIL"
                result["error"] = str(exc)
                errors.append(f"{width}: {exc}")
                try:
                    page.screenshot(path=str(OUTPUT / f"onchain-{width}-failure.png"), full_page=False, timeout=10000)
                except Exception:
                    pass
            finally:
                findings.append(result)
                page.close()
        browser.close()
    (OUTPUT / "report.json").write_text(json.dumps({"url": URL, "results": findings, "errors": errors}, indent=2) + "\n")
    for item in findings:
        print(f"{item['viewport']}px: {item['status']}; overflow={item.get('horizontal_overflow_px','?')}; {item.get('error','')}")
    if errors:
        print("FAIL live visual QA: " + " | ".join(errors), file=sys.stderr)
        return 1
    print("PASS: onchain responsive layout and interactive controls at 1920 / 1440 / 768 / 390 px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
