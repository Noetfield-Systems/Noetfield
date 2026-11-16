#!/usr/bin/env python3
"""Real-source corporate homepage visual acceptance; desktop, tablet and phone.

Checks the bespoke corporate editorial sculpture, accessible live links,
and layout at four viewport sizes. No screenshot-as-a-page approximation.
No fabricated business activity or dynamic numbers are asserted.
"""
from __future__ import annotations
import os, pathlib, subprocess, time, json
from playwright.sync_api import sync_playwright

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"tmp"/"noetfield-command-visual"
OUT.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen(["python3","-m","http.server","8979","--bind","127.0.0.1","--directory",str(ROOT)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
results=[]
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        # The Renaissance website is tested as rendered browser UI, not as static image.
        for name,width,height in [("desktop-1440",1440,900),("desktop-1680",1680,1000),("tablet",820,1040),("mobile",390,844)]:
            page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            response=page.goto("http://127.0.0.1:8979/",wait_until="networkidle",timeout=35000)
            assert response.status==200,response.status
            title=page.locator("h1#hero-title").inner_text()
            assert "make ambitious" in title.lower() and "work real" in title.lower(),title
            assert page.locator(".nr-hero-stage svg.nr-stage-orbit").is_visible()
            assert page.locator("#solutions .nr-product").count()==3
            assert page.locator(".nr-opportunity").count()==3
            assert page.locator(".nr-proof-card").count()==2
            assert page.locator("h1").count()==1
            assert page.locator(".nr-global, .nr-home-header").count()==1
            assert page.locator('a[href="/community/"]').count()>0
            assert page.locator('a[href="/opportunities/"]').count()>0
            assert page.locator('a[href^="/connect/"]').count()>0
            sheets=page.evaluate("""() => [...document.styleSheets].filter(s=>s.href?.includes('noetfield-renaissance')).map(s=>({rules:(()=>{try{return s.cssRules.length}catch(e){return -1}})()}))""")
            assert sheets and sheets[0]["rules"]>25,sheets
            title_style=page.locator("#hero-title").evaluate("""e=>({font:getComputedStyle(e).fontFamily,color:getComputedStyle(e).color})""")
            assert "Newsreader" in title_style["font"],title_style
            dimensions=page.evaluate("""() => ({doc:document.documentElement.scrollWidth,viewport:window.innerWidth})""")
            assert dimensions["doc"]<=width+2,dimensions
            if width<=980:
                menu=page.locator(".nr-home-header [data-nr-menu]")
                assert menu.is_visible()
                menu.click()
                nav=page.locator(".nr-home-header [data-nr-nav]")
                assert menu.get_attribute("aria-expanded")=="true"
                assert nav.is_visible()
                page.keyboard.press("Escape")
                assert menu.get_attribute("aria-expanded")=="false"
                assert not nav.is_visible()
            else:
                assert page.locator(".nr-home-header [data-nr-nav]").is_visible()
            assert not errors,errors
            page.screenshot(path=str(OUT/f"{name}.png"),full_page=False,animations="disabled")
            if name=="desktop-1440":
                page.screenshot(path=str(OUT/"desktop-full-page.png"),full_page=True,animations="disabled")
                tech=page.locator("details#technical-depth")
                assert tech.count()==1 and not tech.evaluate("(e)=>e.open")
                tech.locator("summary").click()
                assert tech.evaluate("(e)=>e.open")
                assert page.locator("#product-live").is_visible()
            results.append(dict(viewport=name,document=dimensions,styles=sheets,jsErrors=errors,ok=True))
            page.close()
        # Shared brand header must work on real corporate pages at mobile width.
        for route,slug in [("/about/","about"),("/investors/","investors"),("/work-with-us/","work-with-us"),("/opportunities/","opportunities")]:
            page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1)
            response=page.goto("http://127.0.0.1:8979"+route,wait_until="networkidle",timeout=35000)
            assert response.status==200,(route,response.status)
            toggle=page.locator(".nr-global [data-nr-menu]")
            assert toggle.is_visible(),route
            page.screenshot(path=str(OUT/f"{slug}-mobile.png"),full_page=False,animations="disabled")
            toggle.click()
            assert toggle.get_attribute("aria-expanded")=="true",route
            nav=page.locator(".nr-global [data-nr-nav]")
            assert nav.is_visible(),route
            assert nav.locator('a[href="/opportunities/"]').count()==1,route
            page.keyboard.press("Escape")
            assert toggle.get_attribute("aria-expanded")=="false",route
            assert not nav.is_visible(),route
            assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth+2"),route
            page.close()
        # The flagship commercial path reuses the already approved public intake
        # and its live link, without generating any real Stripe charge in CI.
        for width,height in [(1440,900),(390,844)]:
            pcap=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
            pcap.route("**/api/intake",lambda route:route.fulfill(
                status=200,content_type="application/json",
                body='{"intake_id":"qa-fixture-only","request_id":"qa-rid","intake_persisted":true}'
            ))
            pcap.route("**/api/intake/health",lambda route:route.fulfill(
                status=200,content_type="application/json",body='{"enabled":true}'
            ))
            errs=[]
            pcap.on("pageerror",lambda e:errs.append(str(e)))
            response=pcap.goto("http://127.0.0.1:8979/real-world-capital/",wait_until="networkidle",timeout=35000)
            assert response.status==200,("capital",response.status)
            assert pcap.locator("h1").count()==1
            assert "real assets" in pcap.locator("h1").inner_text().lower()
            assert pcap.locator("#paths .lane").count()==2
            assert pcap.locator("a[data-offer-payment='rwa-paid-sprint-deposit']").get_attribute("href")=="https://buy.stripe.com/7sY6oI3iUaa06qmcDi1Nu0h"
            assert pcap.locator("#nfCapitalIntake[data-nf-intake-form]").count()==1
            assert pcap.locator("#nfCapitalIntake").get_attribute("data-intake-vector")=="onchain-project"
            assert pcap.evaluate("document.documentElement.scrollWidth<=innerWidth+2"),width
            if width<=600:
                menu=pcap.locator(".nr-global [data-nr-menu]")
                assert menu.is_visible()
                menu.click()
                assert menu.get_attribute("aria-expanded")=="true"
                assert pcap.locator(".nr-global [data-nr-nav]").is_visible()
                pcap.keyboard.press("Escape")
                assert menu.get_attribute("aria-expanded")=="false"
            pcap.screenshot(path=str(OUT/f"capital-{width}.png"),full_page=(width==1440),animations="disabled")
            pcap.locator("#paths a[data-select-capital-track='business-acquisition']").click()
            assert pcap.locator('#nfCapitalIntake select[name="topic"]').input_value()=="business-acquisition"
            pcap.locator('#nfCapitalIntake input[name="email"]').fill("qa@example.org")
            pcap.locator('#nfCapitalIntake input[name="org"]').fill("QA Fixture Organization")
            pcap.locator('#nfCapitalIntake textarea[name="notes"]').fill("Non-confidential test: acquisition preparation, qualified project owner, scope requested.")
            with pcap.expect_request("**/api/intake") as req:
                pcap.locator("#nfCapitalIntake button[type='submit']").click()
            payload=req.value.post_data_json
            assert payload["organization"]=="QA Fixture Organization",payload
            assert payload["contact_email"]=="qa@example.org",payload
            assert payload["vector"]=="onchain-project",payload
            assert "business-acquisition" in str(payload),payload
            pcap.locator(".nf-intake-async-status--ok").wait_for(timeout=10000)
            assert not errs,errs
            pcap.close()
        # Founding community: practical no-wallet product entry. QA uses
        # synthetic fixture responses; it never records or emails a real lead.
        for width,height in [(1440,900),(390,844)]:
            comm=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
            comm.route("**/api/intake",lambda route:route.fulfill(
                status=200,content_type="application/json",
                body='{"intake_id":"fixture-community-only","request_id":"qa-community","intake_persisted":true}'
            ))
            comm.route("**/api/intake/health",lambda route:route.fulfill(
                status=200,content_type="application/json",body='{"enabled":true}'
            ))
            comm_errors=[]
            comm.on("pageerror",lambda e:comm_errors.append(str(e)))
            response=comm.goto("http://127.0.0.1:8979/community/",wait_until="networkidle",timeout=35000)
            assert response.status==200,response.status
            assert comm.locator("h1").count()==1
            assert comm.locator("h1").inner_text().startswith("Get in early")
            assert comm.locator(".cards .card").count()==3
            assert comm.locator("a[href='https://app.noetfield.com/']").count()>0
            assert comm.locator("#nfCommunityIntake").get_attribute("data-intake-vector")=="founding-community"
            assert comm.locator("#nfCommunityIntake input[name='consent']").is_visible()
            assert comm.evaluate("document.documentElement.scrollWidth<=innerWidth+2"),width
            comm.screenshot(path=str(OUT/f"community-{width}.png"),full_page=(width==1440),animations="disabled")
            comm.locator("#nfCommunityIntake input[name='email']").fill("fixture@example.org")
            comm.locator("#nfCommunityIntake select[name='topic']").select_option("early-access-ai-software")
            comm.locator("#nfCommunityIntake input[name='consent']").check()
            with comm.expect_request("**/api/intake") as req:
                comm.locator("#nfCommunityIntake button[type='submit']").click()
            submitted=req.value.post_data_json
            assert submitted["contact_email"]=="fixture@example.org",submitted
            assert submitted["vector"]=="founding-community",submitted
            assert submitted["metadata"]["topic"]=="early-access-ai-software",submitted
            assert submitted["metadata"]["consent_updates"] is True,submitted
            assert submitted["metadata"]["consent_scope"]=="noetfield-product-and-community-updates-v1",submitted
            comm.locator(".nf-intake-async-status--ok").wait_for(timeout=10000)
            assert not comm_errors,comm_errors
            comm.close()
        browser.close()
finally:
    server.terminate()
    try:server.wait(timeout=5)
    except subprocess.TimeoutExpired:server.kill()
(OUT/"report.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
print(json.dumps(results,indent=2))
print("noetfield_command_center_visual: PASS")

# Expose P0 site-audit evidence in the visual CI log for exact, actionable correction.
audit=subprocess.run(["python3","scripts/nf_site_audit_v1.py","--mode","disk","--fail-on","P0","--json"],cwd=ROOT,capture_output=True,text=True)
try:
    audit_data=json.loads(audit.stdout)
    p0=[{"check":f.get("check"),"reason":f.get("reason"),"page":f.get("page"),"evidence":f.get("evidence")} for f in audit_data.get("findings",[]) if f.get("severity")=="P0"]
    print("COMMAND_CENTER_SITE_AUDIT_P0="+json.dumps(p0,ensure_ascii=False),flush=True)
except json.JSONDecodeError:
    print("COMMAND_CENTER_SITE_AUDIT_ERROR="+(audit.stderr or audit.stdout)[-1000:],flush=True)

# Only the route-group fingerprints are printed; never expose private build paths.
try:
    import sys
    sys.path.insert(0,str(ROOT/"scripts"))
    from site_audit import audit as nav_audit, crawl as nav_crawl
    nav_dir=OUT/"nav-snapshots"
    idx=nav_crawl.crawl_disk(ROOT,nav_dir,max_pages=120)
    groups={}
    for row in idx["index"]:
        if row.get("row_class")!="HTML":continue
        blob=(nav_dir/row["snapshot"]).read_text(encoding="utf-8")
        mark=tuple(sorted(nav_audit.nav_fingerprint(blob)))
        groups.setdefault(mark,[]).append(row["www_path"])
    print("COMMAND_CENTER_NAV_GROUPS="+json.dumps([{"pages":v,"links":k} for k,v in groups.items()]),flush=True)
except Exception as exc:
    print("COMMAND_CENTER_NAV_DIAGNOSTIC_ERROR="+str(exc),flush=True)
