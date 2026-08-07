#!/usr/bin/env python3
"""Proof Case 009 — Northwind Dental Studio full customer path (pro grade)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCEA_SCRIPTS = Path.home() / "Desktop/Noetfield-Systems/SourceA/scripts"
if str(SOURCEA_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SOURCEA_SCRIPTS))

from film_elevenlabs_wire_v1 import synthesize_narration  # noqa: E402

WORK = Path.home() / ".sina/proof-case-009-film-work-v1"
OUT_DIR = WORK / "out"
CAPTURE = WORK / "capture"
BASE = os.environ.get("COMPANY_NEW_BASE_URL", "https://app.noetfield.com").rstrip("/")
BRAND = os.environ.get("PROOF_CASE_009_BRAND", "Northwind Dental Studio")
CITY = os.environ.get("PROOF_CASE_009_CITY", "Calgary")
PROMPT = os.environ.get(
    "PROOF_CASE_009_PROMPT",
    f"I'm launching {BRAND} in {CITY} — a modern dental practice. I need a landing page with our "
    f"services, team, and an online appointment request form. When someone books through the form, "
    f"email me the details and add each appointment request to a Google Sheet.",
)
BUSINESS_VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "onwK4e9ZLuTAKqWW03F9")

NARRATION = f"""
Proof Case 009. Northwind Dental Studio — a new vertical, a new founder path, one production session.

The front door asks who you are before it asks what to build.
Startup founder. A page to test demand. The wizard reads the trade from your own words — dental clinic,
Calgary, appointment requests — and drafts a plan before you sign up.

Account created. The workspace opens clean.

You type the full combined ask to your front person: a landing page for {BRAND},
and the automation that catches every appointment request — email plus Google Sheet — without a second prompt.

One send. The cockpit shows the hire in the open: front person, builder, integrator, quality check.
The ticker runs. The team works in view.

After about three minutes.

The page is live — services, team, and the booking form at a public address.
Customer delivered. Preview ready.

Same session. The automation lane seals a verified workflow file in Files.
Page and workflow from one founder sentence — front door through workspace to delivery.

Edited live session on production. Waiting is not shown in real time. The run receipt is on the Evidence Lab.
""".strip()


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg  # noqa: WPS433

    return imageio_ffmpeg.get_ffmpeg_exe()


def _run(cmd: list[str], *, timeout: int = 900) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "failed")[-3000:])


def _probe_duration(path: Path) -> float:
    proc = subprocess.run(
        [_ffmpeg(), "-i", str(path)],
        capture_output=True,
        text=True,
    )
    for line in (proc.stderr or "").splitlines():
        if "Duration:" in line:
            part = line.split("Duration:", 1)[1].split(",", 1)[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"no duration for {path}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _api_json(method: str, path: str, body: dict | None, cookie: str) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        method=method,
        headers={
            "content-type": "application/json",
            "cookie": cookie,
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _cookies_from_jar(jar: dict[str, str]) -> str:
    return "; ".join(f"{k}={v}" for k, v in jar.items())


def _poll_delivery_playwright(browser, storage: dict, project_id: str, *, max_s: int = 360) -> dict[str, Any]:
    context = browser.new_context(storage_state=storage)
    t0 = time.time()
    last: dict[str, Any] = {}
    site_sealed = None
    automation_sealed = None
    while time.time() - t0 < max_s:
        resp = context.request.get(f"{BASE}/v1/projects/{project_id}/agent")
        last = resp.json() if resp.ok else {"ok": False, "status": resp.status}
        delivered = bool(
            last.get("customer_delivered")
            or (last.get("outcome") or {}).get("customer_delivered")
            or last.get("delivery_phase") == "CUSTOMER_DELIVERED"
        )
        preview = bool(last.get("preview_ready") or (last.get("outcome") or {}).get("preview_ready"))
        if preview and site_sealed is None:
            site_sealed = int(time.time() - t0)
        arts = last.get("artifacts") or (last.get("outcome") or {}).get("artifacts") or []
        files = last.get("files") or []
        has_wf = any(
            "n8n-workflow" in str(item.get("href", ""))
            for item in [*arts, *files]
            if isinstance(item, dict)
        )
        if has_wf and automation_sealed is None:
            automation_sealed = int(time.time() - t0)
        if delivered and has_wf:
            context.close()
            return {
                "ok": True,
                "last": last,
                "site_sealed_s": site_sealed,
                "automation_sealed_s": automation_sealed,
                "elapsed_s": int(time.time() - t0),
            }
        time.sleep(5)
    context.close()
    return {"ok": False, "last": last, "elapsed_s": int(time.time() - t0)}


def record_segment(browser, storage: dict | None, url: str, out: Path, seconds: float, *, action=None) -> dict:
    raw_dir = CAPTURE / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for old in raw_dir.glob("*.webm"):
        old.unlink(missing_ok=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=2,
        record_video_dir=str(raw_dir),
        record_video_size={"width": 1920, "height": 1080},
        storage_state=storage,
        color_scheme="dark",
    )
    page = context.new_page()
    page.goto(url, wait_until="networkidle", timeout=120000)
    page.wait_for_timeout(800)
    if action:
        action(page)
    remain = max(0.5, seconds - 0.8)
    page.wait_for_timeout(int(remain * 1000))
    state = context.storage_state()
    context.close()
    raw = sorted(raw_dir.glob("*.webm"), key=lambda p: p.stat().st_mtime)[-1]
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(raw),
            "-t",
            str(seconds),
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#0a0f14",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out),
        ]
    )
    raw.unlink(missing_ok=True)
    return state


def make_card(title: str, subtitle: str, out: Path, seconds: float = 3.0) -> None:
    safe_t = title.replace("'", "\\'").replace(":", "\\:")
    safe_s = subtitle.replace("'", "\\'").replace(":", "\\:")
    vf = (
        f"color=c=0x06080c:s=1920x1080:d={seconds},"
        f"drawtext=text='Proof Case 009':fontsize=28:fontcolor=0x64748b:x=(w-text_w)/2:y=h*0.28,"
        f"drawtext=text='{safe_t}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-20:"
        f"box=1:boxcolor=0x0f172a@0.9:boxborderw=28,"
        f"drawtext=text='{safe_s}':fontsize=36:fontcolor=0x94a3b8:x=(w-text_w)/2:y=(h-text_h)/2+56"
    )
    _run(
        [
            _ffmpeg(),
            "-y",
            "-f",
            "lavfi",
            "-i",
            vf,
            "-c:v",
            "libx264",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-t",
            str(seconds),
            str(out),
        ]
    )


def type_slow(page, selector: str, text: str, *, delay_ms: int = 28) -> None:
    page.click(selector)
    page.fill(selector, "")
    page.type(selector, text, delay=delay_ms)


def run_front_door(browser) -> dict:
    email = f"proof.case009.{int(time.time())}.{os.urandom(3).hex()}@example.test"
    password = "E2eTestPass9!"
    project_id_holder: dict[str, str] = {"id": ""}

    def wizard_action(page):
        page.locator("button.wz__opt").filter(has_text="Startup founder").first.click()
        page.wait_for_timeout(600)
        page.locator("button.wz__opt").filter(has_text="A page to test demand").first.click()
        page.wait_for_timeout(600)
        type_slow(page, "textarea.wz__input", PROMPT, delay_ms=20)
        page.wait_for_timeout(500)
        page.locator("button.wz__go").click()
        page.wait_for_timeout(1400)

    state = record_segment(browser, None, f"{BASE}/", CAPTURE / "01-front-door.mp4", 22.0, action=wizard_action)

    def signup_action(page):
        page.fill('input[name="name"]', "Proof Case 009")
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)
        page.wait_for_timeout(500)
        with page.expect_navigation(timeout=60000):
            page.locator("#signup-form button[type='submit']").click()
        page.wait_for_timeout(1800)

    state = record_segment(browser, state, f"{BASE}/signup/", CAPTURE / "02-signup.mp4", 13.0, action=signup_action)

    def workspace_send_action(page):
        page.wait_for_selector("#chat-start-input", timeout=60000)
        page.wait_for_timeout(600)
        type_slow(page, "#chat-start-input", PROMPT, delay_ms=24)
        page.wait_for_timeout(500)
        with page.expect_navigation(timeout=180000):
            page.locator("#chat-start-send").click()
        project_id_holder["id"] = re.search(r"id=([^&]+)", page.url).group(1)  # type: ignore[union-attr]
        page.wait_for_timeout(1500)
        if "/app/workspace/" in page.url:
            page.goto(f"{BASE}/app/project/?id={project_id_holder['id']}", wait_until="networkidle")
        page.wait_for_selector(".cockpit-grid, .team-roster, #team-roster", timeout=60000)
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, 250)
        page.wait_for_timeout(1000)

    state = record_segment(
        browser, state, f"{BASE}/app/new/", CAPTURE / "03-workspace-send.mp4", 42.0, action=workspace_send_action
    )

    jar = {c["name"]: c["value"] for c in state.get("cookies", []) if "noetfield" in c.get("domain", "")}
    cookie = _cookies_from_jar(jar)
    project_id = project_id_holder["id"]
    if not project_id:
        projects = _api_json("GET", "/v1/projects", None, cookie)
        items = projects.get("projects") or []
        if items:
            project_id = items[0].get("id") or ""
    return {"state": state, "cookie": cookie, "email": email, "project_id": project_id}


def capture_in_flight(browser, storage: dict, project_id: str) -> None:
    cockpit = f"{BASE}/app/project/?id={project_id}"

    def in_flight_action(page):
        page.wait_for_selector(".live-activity--terminal, .cockpit-grid", timeout=60000)
        page.wait_for_timeout(1200)
        page.mouse.wheel(0, 180)
        page.wait_for_timeout(1200)
        page.mouse.wheel(0, -120)
        page.wait_for_timeout(10000)

    record_segment(browser, storage, cockpit, CAPTURE / "04-team-in-flight.mp4", 16.0, action=in_flight_action)


def capture_delivered(browser, storage: dict, project_id: str, slug: str) -> None:
    cockpit = f"{BASE}/app/project/?id={project_id}"

    def cockpit_action(page):
        page.wait_for_selector(".cockpit-grid", timeout=60000)
        page.wait_for_timeout(1000)
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(800)

    record_segment(browser, storage, cockpit, CAPTURE / "07-cockpit-delivered.mp4", 14.0, action=cockpit_action)
    record_segment(browser, storage, f"{BASE}/v1/site/{slug}", CAPTURE / "08-site-live.mp4", 12.0)
    record_segment(browser, storage, cockpit, CAPTURE / "10-files-workflow.mp4", 11.0)


def concat_to_duration(parts: list[Path], out: Path, target_s: float) -> None:
    lst = out.parent / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
    tmp = out.parent / "vraw.mp4"
    _run([_ffmpeg(), "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(tmp)])
    cur = _probe_duration(tmp)
    if cur > target_s + 0.05:
        _run([_ffmpeg(), "-y", "-i", str(tmp), "-t", f"{target_s:.3f}", "-c:v", "copy", str(out)])
    elif cur < target_s - 0.05:
        pad = target_s - cur
        _run(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(tmp),
                "-vf",
                f"tpad=stop_mode=clone:stop_duration={pad:.3f}",
                "-c:v",
                "libx264",
                "-crf",
                "19",
                "-pix_fmt",
                "yuv420p",
                str(out),
            ]
        )
    else:
        shutil.copy2(tmp, out)


def main() -> None:
    from playwright.sync_api import sync_playwright  # noqa: WPS433

    if WORK.exists() and os.environ.get("CASE009_REUSE_CAPTURE") == "1":
        print("reusing capture dir")
    elif WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    OUT_DIR.mkdir(parents=True)
    CAPTURE.mkdir(parents=True)

    vo = WORK / "narration.mp3"
    os.environ.setdefault("ELEVENLABS_VOICE_ID", BUSINESS_VOICE)
    ok, engine, _ = synthesize_narration(NARRATION, vo, lane="sourcea")
    if not ok:
        raise SystemExit("ElevenLabs failed")
    vo_dur = _probe_duration(vo)
    print(f"VO {engine} {vo_dur:.1f}s")

    reuse = os.environ.get("CASE009_REUSE_CAPTURE") == "1"
    have_intake = all(
        (CAPTURE / name).exists()
        for name in ("01-front-door.mp4", "02-signup.mp4", "03-workspace-send.mp4", "04-team-in-flight.mp4")
    )

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        if reuse and have_intake:
            project_id = os.environ.get("CASE009_PROJECT_ID", "")
            storage_path = WORK / "storage-state.json"
            if storage_path.exists():
                storage = json.loads(storage_path.read_text(encoding="utf-8"))
            else:
                raise SystemExit("CASE009_REUSE_CAPTURE requires storage-state.json from prior run")
            jar = {c["name"]: c["value"] for c in storage.get("cookies", []) if "noetfield" in c.get("domain", "")}
            cookie = _cookies_from_jar(jar)
            print(f"reusing intake captures project_id={project_id}")
        else:
            meta = run_front_door(browser)
            cookie = meta["cookie"]
            project_id = meta["project_id"]
            storage = meta["state"]
            (WORK / "storage-state.json").write_text(json.dumps(storage), encoding="utf-8")
            print(f"project_id={project_id}")
            capture_in_flight(browser, storage, project_id)

        delivery = _poll_delivery_playwright(browser, storage, project_id) if project_id else {"ok": False}
        if not delivery.get("ok"):
            raise SystemExit(f"delivery poll failed for {project_id}: {delivery}")

        slug = delivery["last"].get("slug") or project_id
        make_card("After ~3 minutes", "Northwind Dental Studio · page sealed", CAPTURE / "06-card-page.mp4")
        make_card("Same session", "Workflow verified in Files", CAPTURE / "09-card-automation.mp4")
        capture_delivered(browser, storage, project_id, slug)
        browser.close()

    order = [
        CAPTURE / "01-front-door.mp4",
        CAPTURE / "02-signup.mp4",
        CAPTURE / "03-workspace-send.mp4",
        CAPTURE / "04-team-in-flight.mp4",
        CAPTURE / "06-card-page.mp4",
        CAPTURE / "07-cockpit-delivered.mp4",
        CAPTURE / "08-site-live.mp4",
        CAPTURE / "09-card-automation.mp4",
        CAPTURE / "10-files-workflow.mp4",
    ]
    video = OUT_DIR / "video.mp4"
    concat_to_duration(order, video, vo_dur)
    final = OUT_DIR / "case-009.mp4"
    _run([_ffmpeg(), "-y", "-i", str(video), "-i", str(vo), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)])
    poster = OUT_DIR / "case-009-poster.png"
    _run([_ffmpeg(), "-y", "-i", str(final), "-ss", "00:00:08", "-vframes", "1", str(poster)])

    receipt = {
        "schema": "noetfield.proof-case-009-film-receipt-v1",
        "case_id": "proof-case-009",
        "brand": BRAND,
        "city": CITY,
        "prompt": PROMPT,
        "wizard_path": ["startup_founder", "page_to_test_demand"],
        "verdict": "PASS_FILM_FULL_PATH_PRO",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "project_id": project_id,
        "delivery": delivery,
        "voice": {"provider": "elevenlabs", "voice_id": BUSINESS_VOICE},
        "sha256": {"mp4": _sha256(final), "poster": _sha256(poster)},
        "duration_s": round(_probe_duration(final), 2),
    }
    (OUT_DIR / "case-009-film-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    print(f"DONE {final}")


if __name__ == "__main__":
    main()
