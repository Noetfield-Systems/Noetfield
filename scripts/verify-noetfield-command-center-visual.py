#!/usr/bin/env python3
"""Visual acceptance of founder-approved corporate command center on the exact static build.
No fabricated business metrics; visual geometry, click-through, canvas and mobile checks."""
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
            response=page.goto("http://127.0.0.1:8979/",wait_until="networkidle",timeout=30000)
            page.locator("[data-cc-scene]").wait_for()
            page.wait_for_timeout(500)
            title=page.locator("h1#hero-title").inner_text()
            cards=page.locator("#command-capabilities a.cc-card").count()
            nodes=page.locator(".cc-node").count()
            canvas=page.locator("[data-cc-scene]").evaluate("""el => {
               const ctx=el.getContext('2d'),im=ctx.getImageData(0,0,el.width,el.height).data;
               let active=0;for(let i=3;i<im.length;i+=4)if(im[i]>10)active++;
               return {width:el.width,height:el.height,active};
            }""")
            dimensions=page.evaluate("""() => ({doc:document.documentElement.scrollWidth,viewport:window.innerWidth})""")
            if width<1070:
                page.locator(".nf-q-menu").click()
                assert page.locator(".nf-corp-nav").get_attribute("data-open")=="true"
                assert page.locator(".cc-hero-ctas a[href='/connect/']").count()>0
                page.keyboard.press("Escape")
            hrefs=page.locator("#command-capabilities a.cc-card").evaluate_all("xs => xs.map(x=>x.getAttribute('href'))")
            assert response.status==200,response.status
            assert "intelligent businesses" in title.lower(),title
            assert cards==6,cards
            assert nodes==3,nodes
            paths=page.locator("#choose-your-path a.cc-path")
            assert paths.count()==3,paths.count()
            assert page.locator(".cc-evidence-image img").evaluate("img => img.complete && img.naturalWidth > 0"),"First-party product screenshot missing"
            assert "Real Business" in page.locator(".cc-world-people").inner_text()
            assert canvas["active"]>8000,canvas
            assert dimensions["doc"]<=width+2,dimensions
            assert not errors,errors
            assert all(h.startswith("/") for h in hrefs),hrefs
            page.screenshot(path=str(OUT/f"{name}.png"),full_page=False,animations="disabled")
            results.append(dict(viewport=name,canvas=canvas,document=dimensions,cards=cards,nodes=nodes,paths=paths.count(),jsErrors=errors,ok=True))
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
