#!/usr/bin/env python3
"""Real-source corporate homepage visual acceptance; desktop, tablet and phone.

Checks the redesigned custom systems artwork and existing commercial cards
render correctly at real browser viewport sizes with live links and controls.
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
        for name,width,height in [("desktop-1440",1440,900),("desktop-1680",1680,1000),("tablet",820,1040),("mobile",390,844)]:
            page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            response=page.goto("http://127.0.0.1:8979/",wait_until="networkidle",timeout=35000)
            assert response.status==200,response.status
            page.locator(".nx-visual .nx-core").wait_for()
            title=page.locator("h1#hero-title").inner_text()
            assert "intelligent businesses" in title.lower(),title
            assert page.locator("h1").count()==1
            paths=page.locator("#choose-your-path a.nf-ins-path-card")
            capabilities=page.locator("#command-capabilities a.nf-ins-platform-item")
            assert paths.count()==3,paths.count()
            assert capabilities.count()==4,capabilities.count()
            allimgs=page.locator(".nf-institutional-hero img")
            image_results=allimgs.evaluate_all("""els=>els.map(el=>({
              src:el.getAttribute('src'),
              loaded:el.complete&&el.naturalWidth>300,
              naturalWidth:el.naturalWidth,
              naturalHeight:el.naturalHeight
            }))""")
            assert len(image_results)==4,image_results
            assert all(z["loaded"] for z in image_results),image_results
            dimensions=page.evaluate("""() => ({doc:document.documentElement.scrollWidth,viewport:window.innerWidth})""")
            assert dimensions["doc"]<=width+2,dimensions
            design_diagnostics=page.evaluate("""() => ({sheet:[...document.styleSheets].filter(s=>s.href&&s.href.includes('corporate-next')).map(s=>({url:s.href,rules:(()=>{try{return s.cssRules.length}catch(e){return 'error'}})()})), bodyClass:document.body.className,heroClass:document.querySelector('.nf-institutional-hero')?.className,coreWidth:getComputedStyle(document.querySelector('.nx-core')).width,heroBackground:getComputedStyle(document.querySelector('.nf-institutional-hero')).background})""")
            print("CORPORATE_DESIGN_DIAGNOSTICS="+json.dumps(design_diagnostics),flush=True)
            hero_background=page.locator(".nf-institutional-hero").evaluate("el => getComputedStyle(el).backgroundColor")
            assert hero_background=="rgb(7, 18, 29)", f"Corporate navy background overridden: {hero_background}"
            assert page.locator(".nx-orb-label").count()==4
            assert page.locator(".nx-visual svg").is_visible()
            assert page.locator(".nx-core").is_visible()
            hero_box=page.locator(".nx-visual").bounding_box()
            assert hero_box and hero_box["width"]>=280 and hero_box["height"]>=300,hero_box
            if width<=700:
                assert hero_box["y"]<height-70, f"Artwork falls below first screen: {hero_box}"
                brand_box=page.locator(".nf-ins-header .nf-corp-brand").bounding_box()
                menu_box=page.locator(".nf-q-menu").bounding_box()
                assert brand_box and menu_box and abs(brand_box["y"]-menu_box["y"]) < 20, f"Mobile header wraps: {brand_box}, {menu_box}"
                page.locator(".nf-q-menu").click()
                assert page.locator(".nf-corp-nav").get_attribute("data-open")=="true"
                assert page.locator(".nf-corp-nav a[href='/workflows/']").is_visible()
                page.keyboard.press("Escape")
                assert page.locator(".nf-corp-nav").get_attribute("data-open")=="false"
            links=paths.evaluate_all("els=>els.map(a=>a.getAttribute('href'))")
            assert links==["/connect/","/company-os/","/onchain/"],links
            assert page.locator(".nf-ins-button--primary").get_attribute("href")=="/connect/"
            assert page.locator("a[href='/demo/complete-run/']").count()>0
            assert not errors,errors
            page.screenshot(path=str(OUT/f"{name}.png"),full_page=False,animations="disabled")
            results.append(dict(viewport=name,document=dimensions,hero=hero_box,images=image_results,paths=paths.count(),capabilities=capabilities.count(),jsErrors=errors,ok=True))
            page.close()
        # New corporate inner pages must work as pages, not decorative screenshots:
        # mobile menu can open/close without stealing the App CTA or breaking navigation.
        for route,slug in [("/about/","about"),("/investors/","investors")]:
            page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1)
            response=page.goto("http://127.0.0.1:8979"+route,wait_until="networkidle",timeout=35000)
            assert response.status==200,(route,response.status)
            toggle=page.locator(".nx-inner-menu")
            assert toggle.is_visible(),route
            toggle.click()
            assert toggle.get_attribute("aria-expanded")=="true",route
            nav=page.locator(".nf-corp-header .nf-corp-nav")
            assert nav.is_visible(),route
            assert nav.locator('a[href="https://app.noetfield.com/"]').count()==1,route
            page.screenshot(path=str(OUT/f"{slug}-mobile.png"),full_page=False,animations="disabled")
            page.keyboard.press("Escape")
            assert toggle.get_attribute("aria-expanded")=="false",route
            assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth+2"),route
            page.close()
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
