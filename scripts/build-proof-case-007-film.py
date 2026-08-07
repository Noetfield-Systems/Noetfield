#!/usr/bin/env python3
"""Build Proof Case 007 film — edited live session + ElevenLabs business VO."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCEA_SCRIPTS = Path.home() / "Desktop/Noetfield-Systems/SourceA/scripts"
if str(SOURCEA_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SOURCEA_SCRIPTS))

from film_elevenlabs_wire_v1 import synthesize_narration  # noqa: E402

WORK = Path.home() / ".sina/proof-case-007-film-work-v1"
OUT_DIR = WORK / "out"
# Daniel — clear business narrator; override with ELEVENLABS_VOICE_ID if set
BUSINESS_VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "onwK4e9ZLuTAKqWW03F9")

NARRATION = """
Proof Case 007. Summit Ridge Physical Therapy.

Here is what one real client sentence delivers on production.

A professional landing page for Summit Ridge Physical Therapy, a boutique physiotherapy studio in Vancouver.
Services, team, and an online intake form.
And automate it: when someone submits the intake form, email the details and add each lead to a Google Sheet.

One ask. The front person hires its team, and the work shows in the cockpit.

After about three minutes, the page is live. Preview ready. Customer delivered. While the build lane is still running.

Summit Ridge Physical Therapy: services, team, and the intake form, all serving at a public address you can open right now.

Same session. No second ask. The automation lane fires on its own and delivers a verified workflow file in Files.

Page and workflow. One sentence. One cockpit session.

This is an edited live demonstration. The run receipt is on the Evidence Lab.
The workflow is ready to import. This film does not show it running inside the client's own automation tenant.
""".strip()

CAPTURES = [
    {
        "id": "site-hero",
        "url": "https://app.noetfield.com/v1/site/summit-ridge-physical-therapy",
        "seconds": 8.0,
        "scroll": True,
    },
    {
        "id": "site-form",
        "url": "https://app.noetfield.com/v1/site/summit-ridge-physical-therapy#contact",
        "seconds": 7.0,
        "scroll": False,
    },
    {
        "id": "cockpit",
        "url": "https://app.noetfield.com/app/project/?id=prj_e86138a98476452fbe51628c",
        "seconds": 10.0,
        "scroll": True,
    },
    {
        "id": "app-new",
        "url": "https://app.noetfield.com/app/new/",
        "seconds": 8.0,
        "scroll": False,
    },
]

CARDS = [
    ("After ~3 minutes", "Page seals while build continues"),
    ("Same session", "No second ask — automation auto-fires"),
]


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # noqa: WPS433

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as exc:
        raise SystemExit("ffmpeg missing") from exc


def _run(cmd: list[str], *, timeout: int = 900) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "command failed")[-3000:])


def _probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [_ffmpeg(), "-i", str(path), "-f", "null", "-"],
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in out.splitlines():
        if "Duration:" in line:
            part = line.split("Duration:", 1)[1].split(",", 1)[0].strip()
            h, m, s = part.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"no duration for {path}")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def synthesize_vo(out_mp3: Path) -> float:
    os.environ.setdefault("ELEVENLABS_VOICE_ID", BUSINESS_VOICE)
    ok, engine, _words = synthesize_narration(NARRATION, out_mp3, lane="sourcea")
    if not ok or not out_mp3.is_file():
        raise SystemExit("ElevenLabs narration failed — check API key")
    dur = _probe_duration(out_mp3)
    print(f"VO ok ({engine}) duration={dur:.1f}s voice={BUSINESS_VOICE[:8]}…")
    return dur


def capture_clips(capture_dir: Path) -> list[Path]:
    from playwright.sync_api import sync_playwright  # noqa: WPS433

    capture_dir.mkdir(parents=True, exist_ok=True)
    clips: list[Path] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for spec in CAPTURES:
            out = capture_dir / f"{spec['id']}.webm"
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                device_scale_factor=2,
                color_scheme="dark",
            )
            page = context.new_page()
            page.goto(spec["url"], wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(1500)
            if spec.get("scroll"):
                page.evaluate(
                    """async () => {
                      const steps = 6;
                      const max = Math.max(document.body.scrollHeight - window.innerHeight, 0);
                      for (let i = 0; i <= steps; i++) {
                        window.scrollTo(0, (max * i) / steps);
                        await new Promise(r => setTimeout(r, 250));
                      }
                    }"""
                )
            page.wait_for_timeout(500)
            page.video.save_as(str(out)) if page.video else None
            # Record via screencast alternative: screenshot sequence → mp4
            context.close()
        browser.close()

    # Playwright video API needs record_video_dir on context — redo properly
    clips.clear()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for spec in CAPTURES:
            out = capture_dir / f"{spec['id']}.mp4"
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                device_scale_factor=2,
                record_video_dir=str(capture_dir / "raw"),
                record_video_size={"width": 1920, "height": 1080},
            )
            page = context.new_page()
            page.goto(spec["url"], wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(1200)
            if spec.get("scroll"):
                page.mouse.wheel(0, 400)
                page.wait_for_timeout(600)
                page.mouse.wheel(0, 500)
                page.wait_for_timeout(600)
            remain_ms = int(spec["seconds"] * 1000) - 2400
            if remain_ms > 0:
                page.wait_for_timeout(remain_ms)
            context.close()
            raw_videos = sorted((capture_dir / "raw").glob("*.webm"), key=lambda p: p.stat().st_mtime)
            if not raw_videos:
                raise RuntimeError(f"capture failed for {spec['id']}")
            latest = raw_videos[-1]
            _run(
                [
                    _ffmpeg(),
                    "-y",
                    "-i",
                    str(latest),
                    "-t",
                    str(spec["seconds"]),
                    "-vf",
                    "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#0a0f14",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "medium",
                    "-crf",
                    "20",
                    "-pix_fmt",
                    "yuv420p",
                    "-an",
                    str(out),
                ]
            )
            latest.unlink(missing_ok=True)
            clips.append(out)
            print(f"captured {spec['id']} -> {out.name}")
        browser.close()
    return clips


def make_card_mp4(title: str, subtitle: str, out: Path, seconds: float = 2.5) -> Path:
    safe_t = title.replace("'", "\\'").replace(":", "\\:")
    safe_s = subtitle.replace("'", "\\'").replace(":", "\\:")
    vf = (
        f"color=c=0x0a0f14:s=1920x1080:d={seconds},"
        f"drawtext=text='{safe_t}':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-40:"
        f"box=1:boxcolor=0x111827@0.8:boxborderw=24,"
        f"drawtext=text='{safe_s}':fontsize=34:fontcolor=0xcbd5e1:x=(w-text_w)/2:y=(h-text_h)/2+48"
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
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-t",
            str(seconds),
            str(out),
        ]
    )
    return out


def concat_video(parts: list[Path], out: Path, target_s: float) -> None:
    list_file = out.parent / "concat.txt"
    list_file.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
    tmp = out.parent / "video_raw.mp4"
    _run([_ffmpeg(), "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(tmp)])
    cur = _probe_duration(tmp)
    if cur < target_s - 0.05:
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
                "-preset",
                "medium",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(out),
            ]
        )
    elif cur > target_s + 0.05:
        _run(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(tmp),
                "-t",
                f"{target_s:.3f}",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(out),
            ]
        )
    else:
        shutil.copy2(tmp, out)


def mux_av(video: Path, audio: Path, out: Path) -> None:
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(out),
        ]
    )


def poster_from_video(video: Path, out: Path) -> None:
    _run([_ffmpeg(), "-y", "-i", str(video), "-ss", "00:00:04", "-vframes", "1", str(out)])


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    OUT_DIR.mkdir(parents=True)
    capture_dir = WORK / "capture"
    cards_dir = WORK / "cards"

    vo_mp3 = WORK / "narration.mp3"
    vo_dur = synthesize_vo(vo_mp3)

    clips = capture_clips(capture_dir)
    cards_dir.mkdir(parents=True)
    card_clips = [
        make_card_mp4(t, s, cards_dir / f"card-{i}.mp4") for i, (t, s) in enumerate(CARDS)
    ]

    # Interleave: app-new, card1, site-hero, site-form, card2, cockpit
    order = [clips[3], card_clips[0], clips[0], clips[1], card_clips[1], clips[2]]
    video_mp4 = OUT_DIR / "case-007-video.mp4"
    concat_video(order, video_mp4, vo_dur)

    final_mp4 = OUT_DIR / "case-007.mp4"
    mux_av(video_mp4, vo_mp3, final_mp4)

    poster = OUT_DIR / "case-007-poster.png"
    poster_from_video(final_mp4, poster)

    receipt = {
        "schema": "noetfield.proof-case-007-film-receipt-v1",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "verdict": "PASS_FILM_EDITED",
        "voice": {"provider": "elevenlabs", "voice_id": BUSINESS_VOICE},
        "sha256": {
            "mp4": _sha256(final_mp4),
            "poster": _sha256(poster),
            "narration_mp3": _sha256(vo_mp3),
        },
        "duration_s": round(_probe_duration(final_mp4), 2),
        "outputs": {
            "mp4": str(final_mp4),
            "poster": str(poster),
        },
    }
    receipt_path = OUT_DIR / "case-007-film-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    print(f"\nDONE {final_mp4} ({receipt['duration_s']}s)")


if __name__ == "__main__":
    main()
