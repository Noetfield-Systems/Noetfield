#!/usr/bin/env python3
"""Read-only actual Chromium E2E checks for Noetfield OS entire public onchain site.
No wallet connects, payment calls, token transactions or synthetic user creation.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = os.getenv("ONCHAIN_BASE_URL", "http://127.0.0.1:8765")
OUT = Path("tmp/onchain-enterprise-qa")
ROUTES = ("/onchain/", "/onchain/rwa/", "/onchain/policy/",
          "/onchain/stablecoin/", "/onchain/agents/",
          "/onchain/hub/", "/onchain/whitepaper/")
WIDTHS = (390, 768, 1440)
SOLUTIONS = {"rwa": "rwa-private-credit", "policy": "policy-to-code",
             "stablecoin": "stablecoin-operations", "agents": "agent-authorization"}

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for width in WIDTHS:
            for route in ROUTES:
                page = browser.new_page(viewport={"width": width, "height": 900},
                                        device_scale_factor=1)
                page_errors = []
                page.on("pageerror", lambda exc: page_errors.append(str(exc)))
                result = {"route": route, "viewport": width}
                try:
                    response = page.goto(BASE + route, wait_until="domcontentloaded", timeout=45000)
                    assert response is not None and response.status == 200, (
                        "http", response.status if response else None)
                    page.locator("h1").first.wait_for(state="visible", timeout=18000)
                    page.evaluate("document.fonts.ready")
                    width_actual = page.evaluate("document.documentElement.scrollWidth")
                    overflow = max(0, width_actual - width)
                    result["overflow"] = overflow
                    if overflow > 4:
                        culprits = page.evaluate("""() => [...document.querySelectorAll('body *')]
                          .map(el=>({element:el.tagName,cls:typeof el.className==='string'?el.className.slice(0,70):'',right:Math.round(el.getBoundingClientRect().right)}))
                          .filter(x=>x.right>innerWidth+5).sort((a,b)=>b.right-a.right).slice(0,6)""")
                        raise AssertionError(f"Horizontal overflow {overflow}px: {culprits}")
                    assert page.locator("h1").count() == 1, "exactly one H1 required"
                    if route in ("/onchain/rwa/", "/onchain/policy/",
                                 "/onchain/stablecoin/", "/onchain/agents/"):
                        key = route.split("/")[-2]
                        assert page.locator(".nf-nav a[aria-current='page']").count() == 1
                        assert page.locator(".nf-proof-card").count() == 3
                        assert page.locator(".nf-capability").count() == 4
                        assert page.locator(".nf-step").count() == 4
                        assert page.locator(".nf-qa").count() == 3
                        assert page.locator(f'a[href="/onchain/?solution={key}#project"]').count() >= 2
                        page.locator(".nf-qa summary").first.click()
                        assert page.locator(".nf-qa").first.get_attribute("open") is not None
                        if width <= 1120:
                            menu = page.locator("#nfMenu")
                            assert menu.is_visible()
                            menu.click()
                            assert menu.get_attribute("aria-expanded") == "true"
                            page.locator("#nfNav").get_by_text("Network Hub").click()
                            assert page.url.endswith("/onchain/hub/")
                        else:
                            assert page.locator("#nfNav").is_visible()
                    if route == "/onchain/":
                        art = page.locator(".v5-campus")
                        assert art.evaluate("(el)=>el.complete && el.naturalWidth >= 600")
                        if width >= 1440:
                            assert art.evaluate("(el)=>el.currentSrc.endsWith(\"/onchain/hero-architecture-hd.webp\")"), "desktop is not using high-definition hero source"
                        assert page.locator(".nf-nav-solutions a").count() == 4
                        assert page.locator(".v5-hero-services a").count() == 4
                        assert page.locator("form#nfOnchainIntake[data-nf-intake-form]").count() == 1
                        page.locator(".nf-nav-solutions summary").click()
                        assert page.locator('.nf-nav-submenu a[href="/onchain/agents/"]').is_visible()
                    if route == "/onchain/hub/":
                        assert page.locator(".nf-hub-solution-links a").count() == 4
                        assert page.locator("#connectWallet").count() == 1
                        assert page.locator("#dailyClaim").count() == 1
                        assert page.locator("#inviteLink").count() == 1
                    if route == "/onchain/whitepaper/":
                        assert page.locator(".nf-paper-explore a").count() == 4
                        assert page.locator(".toc a").count() >= 10
                    if page_errors:
                        raise AssertionError(f"JS page errors: {page_errors[:3]}")
                    if width in (390, 1440):
                        label = route.strip("/").replace("/", "-") or "home"
                        page.screenshot(path=str(OUT / f"{label}-{width}.png"),
                                        animations="disabled", timeout=15000)
                    result["result"] = "PASS"
                except Exception as exc:
                    result["result"] = "FAIL"
                    result["error"] = str(exc)
                    errors.append(f"{width} {route}: {exc}")
                    try:
                        label = route.strip("/").replace("/", "-") or "home"
                        page.screenshot(path=str(OUT / f"{label}-{width}-failure.png"),
                                        timeout=15000)
                    except Exception:
                        pass
                finally:
                    page.close()
                    results.append(result)

        # Prove each new page's commercial CTA reaches exactly the existing intake.
        for key, topic in SOLUTIONS.items():
            p = browser.new_page(viewport={"width": 1440, "height": 900})
            try:
                r = p.goto(BASE + f"/onchain/?solution={key}#project",
                           wait_until="domcontentloaded", timeout=45000)
                assert r is not None and r.status == 200
                p.locator('form#nfOnchainIntake select[name="topic"]').wait_for()
                actual = p.locator('form#nfOnchainIntake select[name="topic"]').input_value()
                assert actual == topic, (key, topic, actual)
                assert len(p.locator('form#nfOnchainIntake textarea[name="notes"]').input_value()) > 30
                results.append({"route": f"project-prefill/{key}", "result": "PASS"})
            except Exception as exc:
                errors.append(f"Prefill {key}: {exc}")
                results.append({"route": f"project-prefill/{key}", "result": "FAIL", "error": str(exc)})
            finally:
                p.close()
        browser.close()
    (OUT / "report.json").write_text(json.dumps({"results": results, "failures": errors},
                                                indent=2) + "\n")
    for row in results:
        print(f"{row['result']} {row['route']} {row.get('viewport','scope')} overflow={row.get('overflow','n/a')} {row.get('error','')}")
    if errors:
        print("FAILURES: " + " | ".join(errors))
        return 1
    print(f"PASS: {len(results)} cross-page checks; {len(ROUTES)} routes, 3 viewports, 4 scoped intake paths.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
