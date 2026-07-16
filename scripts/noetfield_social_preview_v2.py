#!/usr/bin/env python3
"""Generate, apply and verify Noetfield social-preview package v2."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import tempfile
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "noetfield-social-preview-v2.json"
ALLOWLIST_PATH = ROOT / "governance" / "www-public-artifact-v1.json"
DEFAULT_ARTIFACT = ROOT / "www-pages-dist"
DEFAULT_RECEIPT = ROOT / "receipts" / "noetfield-social-preview-v2.json"
CARD_WIDTH = 1200
CARD_HEIGHT = 630
SOCIAL_PATH = "/assets/social/"
TITLE_RE = re.compile(r"\s*<title\b[^>]*>.*?</title>\s*", re.IGNORECASE | re.DOTALL)
META_RE = re.compile(r"\s*<meta\b[^>]*>\s*", re.IGNORECASE)
LINK_RE = re.compile(r"\s*<link\b[^>]*>\s*", re.IGNORECASE)
HEAD_RE = re.compile(r"<head\b[^>]*>", re.IGNORECASE)
MANAGED_COMMENT_RE = re.compile(
    r"\s*<!--\s*Noetfield social preview v2: generated from "
    r"data/noetfield-social-preview-v2\.json\s*-->\s*",
    re.IGNORECASE,
)
ATTR_RE = re.compile(
    r"([:\w-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
    re.IGNORECASE,
)
TARGET_META_NAMES = {
    "description",
    "robots",
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
    "twitter:image:alt",
}
TARGET_META_PROPERTIES = {
    "og:title",
    "og:description",
    "og:url",
    "og:type",
    "og:site_name",
    "og:image",
    "og:image:width",
    "og:image:height",
    "og:image:alt",
}
FORBIDDEN_STALE_STRINGS = (
    "AI Governance " + "& Digital Trust",
    "Infrastructure for Trust " + "& Stewardship in the Age of AI",
    "Trust Ledger " + "for AI Governance",
    "noetfield-" + "og.png",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def load_config() -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    if config.get("schema") != "noetfield-social-preview-v2":
        raise ValueError("unsupported social-preview config schema")
    cards = config.get("cards")
    if not isinstance(cards, dict) or set(cards) != {
        "corporate",
        "enterprise",
        "motors",
        "investors",
        "proof",
        "frontier",
    }:
        raise ValueError("social-preview config must define the six canonical cards")
    return config


def html_static_files() -> list[str]:
    allowlist = load_json(ALLOWLIST_PATH)
    files = allowlist.get("static_files")
    if not isinstance(files, list):
        raise ValueError("public artifact static_files must be a list")
    return sorted(
        rel
        for rel in files
        if isinstance(rel, str)
        and rel.endswith(".html")
        and HEAD_RE.search((ROOT / rel).read_text(encoding="utf-8"))
    )


def route_for_path(relative_path: str) -> str:
    if relative_path == "index.html":
        return "/"
    if relative_path.endswith("/index.html"):
        return f"/{relative_path[:-10]}"
    return f"/{relative_path}"


def path_for_route(route: str) -> str:
    if route == "/":
        return "index.html"
    if route.endswith("/"):
        return f"{route.lstrip('/')}index.html"
    return route.lstrip("/")


def attr_value(tag: str, name: str) -> str:
    for match in ATTR_RE.finditer(tag):
        if match.group(1).lower() == name.lower():
            return next(value for value in match.groups()[1:] if value is not None)
    return ""


class DocumentMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta_names: dict[str, str] = {}
        self.meta_properties: dict[str, str] = {}
        self.canonical = ""
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.in_title = False
        self.in_h1 = False
        self.has_refresh = False

    @property
    def title(self) -> str:
        return collapse(" ".join(self.title_parts))

    @property
    def h1(self) -> str:
        return collapse(" ".join(self.h1_parts))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        lower = tag.lower()
        if lower == "title":
            self.in_title = True
        elif lower == "h1":
            self.in_h1 = True
        elif lower == "meta":
            name = values.get("name", "").lower()
            prop = values.get("property", "").lower()
            content = values.get("content", "")
            if name:
                self.meta_names[name] = content
            if prop:
                self.meta_properties[prop] = content
            if values.get("http-equiv", "").lower() == "refresh":
                self.has_refresh = True
        elif lower == "link" and values.get("rel", "").lower() == "canonical":
            self.canonical = values.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        elif tag.lower() == "h1":
            self.in_h1 = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_h1:
            self.h1_parts.append(data)


def parse_document(text: str) -> DocumentMetadata:
    parser = DocumentMetadata()
    parser.feed(text)
    return parser


def collapse(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def route_label(route: str) -> str:
    if route == "/":
        return "Noetfield Systems"
    segment = route.rstrip("/").rsplit("/", 1)[-1]
    return " ".join(word.capitalize() for word in re.split(r"[-_]", segment) if word)


def profile_for_route(route: str, config: dict[str, Any]) -> str:
    exact = config["route_profiles"].get(route)
    if exact:
        return str(exact)
    for row in config["profile_prefixes"]:
        if any(route.startswith(prefix) for prefix in row["prefixes"]):
            return str(row["profile"])
    return "corporate"


def noindex_reason(source: DocumentMetadata, route: str) -> str | None:
    robots = source.meta_names.get("robots", "").lower()
    if route == "/404.html":
        return "not-found document"
    if "noindex" in robots:
        return "source declares noindex"
    if source.has_refresh:
        return "redirect or placeholder route"
    return None


@dataclass(frozen=True)
class RouteMetadata:
    relative_path: str
    route: str
    title: str
    description: str
    profile: str
    noindex_reason: str | None

    @property
    def indexable(self) -> bool:
        return self.noindex_reason is None


def resolve_route_metadata(
    root: Path, relative_paths: list[str], config: dict[str, Any]
) -> list[RouteMetadata]:
    used_titles: set[str] = set()
    rows: list[RouteMetadata] = []
    overrides = config["metadata_overrides"]
    for relative_path in sorted(relative_paths):
        route = route_for_path(relative_path)
        source_text = (root / relative_path).read_text(encoding="utf-8")
        source = parse_document(source_text)
        override = overrides.get(route, {})
        title = collapse(str(override.get("title") or source.title))
        if not title or title.lower().startswith(("redirect", "loading", "please wait")):
            title = route_label(route)
        if "noetfield" not in title.lower():
            title = f"{title} — Noetfield"
        candidate = title
        if candidate.casefold() in used_titles:
            candidate = f"{title} · {route_label(route)}"
        if candidate.casefold() in used_titles:
            candidate = f"{title} · {route}"
        title = candidate
        used_titles.add(title.casefold())

        description = collapse(
            str(override.get("description") or source.meta_names.get("description", ""))
        )
        if len(description) < 30:
            description = (
                f"Explore {route_label(route)} from Noetfield Systems Inc.—governed AI "
                "products, custom AI Motors and institutional workflows."
            )
        rows.append(
            RouteMetadata(
                relative_path=relative_path,
                route=route,
                title=title,
                description=description,
                profile=profile_for_route(route, config),
                noindex_reason=noindex_reason(source, route),
            )
        )
    return rows


def card_url(profile: str, config: dict[str, Any]) -> str:
    return f"{config['site_origin']}{SOCIAL_PATH}{config['cards'][profile]['filename']}"


def metadata_block(row: RouteMetadata, config: dict[str, Any]) -> str:
    canonical = f"{config['site_origin']}{row.route}"
    image = card_url(row.profile, config)
    card = config["cards"][row.profile]
    robots = "index,follow" if row.indexable else "noindex,nofollow"
    values = {
        "title": escape(row.title),
        "description": escape(row.description, quote=True),
        "canonical": escape(canonical, quote=True),
        "image": escape(image, quote=True),
        "alt": escape(str(card["alt"]), quote=True),
        "site_name": escape(str(config["site_name"]), quote=True),
        "robots": robots,
    }
    return (
        "\n <!-- Noetfield social preview v2: generated from "
        "data/noetfield-social-preview-v2.json -->\n"
        f" <title>{values['title']}</title>\n"
        f' <meta name="description" content="{values["description"]}" />\n'
        f' <meta name="robots" content="{values["robots"]}" />\n'
        f' <link rel="canonical" href="{values["canonical"]}" />\n'
        f' <meta property="og:site_name" content="{values["site_name"]}" />\n'
        f' <meta property="og:title" content="{values["title"]}" />\n'
        f' <meta property="og:description" content="{values["description"]}" />\n'
        f' <meta property="og:url" content="{values["canonical"]}" />\n'
        ' <meta property="og:type" content="website" />\n'
        f' <meta property="og:image" content="{values["image"]}" />\n'
        ' <meta property="og:image:width" content="1200" />\n'
        ' <meta property="og:image:height" content="630" />\n'
        f' <meta property="og:image:alt" content="{values["alt"]}" />\n'
        ' <meta name="twitter:card" content="summary_large_image" />\n'
        f' <meta name="twitter:title" content="{values["title"]}" />\n'
        f' <meta name="twitter:description" content="{values["description"]}" />\n'
        f' <meta name="twitter:image" content="{values["image"]}" />\n'
        f' <meta name="twitter:image:alt" content="{values["alt"]}" />\n'
    )


def remove_managed_metadata(text: str) -> str:
    text = MANAGED_COMMENT_RE.sub("\n", TITLE_RE.sub("\n", text))

    def remove_meta(match: re.Match[str]) -> str:
        tag = match.group(0)
        name = attr_value(tag, "name").lower()
        prop = attr_value(tag, "property").lower()
        if name in TARGET_META_NAMES or prop in TARGET_META_PROPERTIES:
            return "\n"
        return tag

    def remove_link(match: re.Match[str]) -> str:
        tag = match.group(0)
        return "\n" if attr_value(tag, "rel").lower() == "canonical" else tag

    return LINK_RE.sub(remove_link, META_RE.sub(remove_meta, text))


def inject_metadata(text: str, row: RouteMetadata, config: dict[str, Any]) -> str:
    rendered = remove_managed_metadata(text)
    head = HEAD_RE.search(rendered)
    if head is None:
        raise ValueError(f"HTML document has no head: {row.relative_path}")
    insert_at = head.end()
    viewport = re.search(
        r"<meta\b[^>]*name\s*=\s*([\"'])viewport\1[^>]*>",
        rendered[head.end() :],
        re.IGNORECASE,
    )
    if viewport:
        insert_at = head.end() + viewport.end()
    block = metadata_block(row, config)
    rendered = f"{rendered[:insert_at]}{block}{rendered[insert_at:]}"
    return re.sub(r"\n{3,}", "\n\n", rendered)


def apply_metadata_to_artifact(root: Path, artifact: Path, relative_paths: list[str]) -> int:
    config = load_config()
    documents = [
        rel for rel in relative_paths if HEAD_RE.search((root / rel).read_text(encoding="utf-8"))
    ]
    rows = resolve_route_metadata(root, documents, config)
    for row in rows:
        path = artifact / row.relative_path
        path.write_text(
            inject_metadata(path.read_text(encoding="utf-8"), row, config),
            encoding="utf-8",
        )
    return len(rows)


def sync_source_metadata() -> int:
    config = load_config()
    routes = set(config["source_sync_routes"])
    relative_paths = [path_for_route(route) for route in routes]
    rows = resolve_route_metadata(ROOT, relative_paths, config)
    for row in rows:
        path = ROOT / row.relative_path
        path.write_text(
            inject_metadata(path.read_text(encoding="utf-8"), row, config),
            encoding="utf-8",
        )
    return len(rows)


def tracking_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    tracking: float,
) -> None:
    x, y = xy
    for character in text:
        draw.text((x, y), character, font=font, fill=fill)
        x += draw.textlength(character, font=font) + tracking


def load_font(path: Path, size: int, weight: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.BASIC)
    try:
        font.set_variation_by_axes([weight])
    except (AttributeError, OSError):
        pass
    return font


def wrap_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def fit_wrapped_font(
    draw: ImageDraw.ImageDraw,
    font_path: Path,
    text: str,
    max_width: int,
    max_lines: int,
    start_size: int,
    min_size: int,
    weight: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(start_size, min_size - 1, -1):
        font = load_font(font_path, size, weight)
        lines = wrap_lines(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = load_font(font_path, min_size, weight)
    return font, wrap_lines(draw, text, font, max_width)


def draw_architecture(draw: ImageDraw.ImageDraw, card_index: int) -> None:
    muted = "#29403A"
    faint = "#182824"
    accent = "#9DC4AF"
    x0, x1 = 875, 1120
    y0 = 155 + (card_index % 3) * 18
    points = [
        (x0, y0),
        (x0 + 82, y0 + 72),
        (x0 + 12, y0 + 174),
        (x1, y0 + 242),
    ]
    draw.line(points, fill=muted, width=2, joint="curve")
    draw.line((x0 + 82, 112, x0 + 82, 494), fill=faint, width=1)
    draw.line((830, y0 + 174, 1148, y0 + 174), fill=faint, width=1)
    for index, (x, y) in enumerate(points):
        radius = 7 if index == card_index % 4 else 4
        colour = accent if index == card_index % 4 else muted
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=colour)
    gate_y = 466 - (card_index % 2) * 32
    draw.rounded_rectangle((902, gate_y, 1092, gate_y + 46), radius=23, outline=muted, width=2)
    draw.line((932, gate_y + 23, 1062, gate_y + 23), fill=accent, width=2)
    draw.ellipse((988, gate_y + 18, 998, gate_y + 28), fill=accent)


def render_card(
    profile: str,
    card: dict[str, Any],
    index: int,
    font_path: Path,
    output: Path,
) -> None:
    background = "#08110F"
    ivory = "#F3F0E7"
    secondary = "#C7CEC8"
    accent = "#9DC4AF"
    line = "#263832"
    image = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), background)
    draw = ImageDraw.Draw(image)
    draw.rectangle((28, 28, 1171, 601), outline=line, width=1)
    draw.line((82, 124, 160, 124), fill=accent, width=4)
    draw.line((817, 72, 817, 558), fill=line, width=1)
    draw_architecture(draw, index)

    eyebrow_font = load_font(font_path, 18, 580)
    tracking_text(draw, (82, 70), str(card["eyebrow"]), eyebrow_font, accent, 2.2)
    number_font = load_font(font_path, 16, 500)
    draw.text((1098, 70), f"0{index + 1}", font=number_font, fill=secondary, anchor="ra")
    draw.line((1110, 80, 1148, 80), fill=line, width=1)

    headline_font, headline_lines = fit_wrapped_font(
        draw,
        font_path,
        str(card["headline"]),
        max_width=688,
        max_lines=2,
        start_size=72,
        min_size=57,
        weight=560,
    )
    y = 162
    headline_spacing = int(headline_font.size * 1.03)
    for line_text in headline_lines:
        draw.text((82, y), line_text, font=headline_font, fill=ivory)
        y += headline_spacing

    support_font, support_lines = fit_wrapped_font(
        draw,
        font_path,
        str(card["supporting"]),
        max_width=682,
        max_lines=3,
        start_size=25,
        min_size=21,
        weight=410,
    )
    y += 25
    for line_text in support_lines:
        draw.text((84, y), line_text, font=support_font, fill=secondary)
        y += int(support_font.size * 1.42)

    draw.line((82, 536, 774, 536), fill=line, width=1)
    footer_font = load_font(font_path, 17, 480)
    draw.ellipse((82, 562, 90, 570), fill=accent)
    draw.text((106, 553), str(card["footer"]), font=footer_font, fill=secondary)
    profile_font = load_font(font_path, 13, 520)
    tracking_text(draw, (932, 556), profile.upper(), profile_font, line, 1.5)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", compress_level=9, optimize=False)


def render_cards(output_dir: Path) -> list[Path]:
    config = load_config()
    font_path = ROOT / config["font"]
    if not font_path.is_file():
        raise ValueError(f"vendored font is absent: {font_path.relative_to(ROOT)}")
    outputs: list[Path] = []
    for index, (profile, card) in enumerate(config["cards"].items()):
        output = output_dir / card["filename"]
        render_card(profile, card, index, font_path, output)
        outputs.append(output)
    return outputs


def check_render(expected_dir: Path) -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="noetfield-social-preview-") as temp_dir:
        rendered = render_cards(Path(temp_dir))
        for actual in rendered:
            expected = expected_dir / actual.name
            if not expected.is_file():
                errors.append(f"missing expected card: {expected}")
            elif actual.read_bytes() != expected.read_bytes():
                errors.append(f"non-deterministic card bytes: {actual.name}")
    return errors


def verify_package(artifact: Path, receipt_path: Path) -> tuple[dict[str, Any], list[str]]:
    config = load_config()
    relative_paths = html_static_files()
    expected_rows = {row.route: row for row in resolve_route_metadata(ROOT, relative_paths, config)}
    errors: list[str] = []
    route_rows: list[dict[str, Any]] = []
    seen_titles: dict[str, str] = {}
    image_cache: dict[str, dict[str, Any]] = {}

    for relative_path in relative_paths:
        route = route_for_path(relative_path)
        expected = expected_rows[route]
        path = artifact / relative_path
        if not path.is_file():
            errors.append(f"{route}: artifact HTML is absent")
            continue
        text = path.read_text(encoding="utf-8")
        document = parse_document(text)
        canonical = f"{config['site_origin']}{route}"
        expected_image = card_url(expected.profile, config)
        required_names = {
            "description": expected.description,
            "robots": "index,follow" if expected.indexable else "noindex,nofollow",
            "twitter:card": "summary_large_image",
            "twitter:title": expected.title,
            "twitter:description": expected.description,
            "twitter:image": expected_image,
        }
        required_properties = {
            "og:title": expected.title,
            "og:description": expected.description,
            "og:url": canonical,
            "og:type": "website",
            "og:image": expected_image,
            "og:image:width": "1200",
            "og:image:height": "630",
        }
        if document.title != expected.title:
            errors.append(f"{route}: title mismatch")
        if document.canonical != canonical:
            errors.append(f"{route}: canonical URL mismatch")
        for name, value in required_names.items():
            if document.meta_names.get(name) != value:
                errors.append(f"{route}: meta name={name} mismatch or absent")
        for prop, value in required_properties.items():
            if document.meta_properties.get(prop) != value:
                errors.append(f"{route}: meta property={prop} mismatch or absent")
        alt = document.meta_properties.get("og:image:alt", "")
        if len(alt) < 20:
            errors.append(f"{route}: og:image:alt is not meaningful")
        if document.meta_names.get("twitter:image:alt") != alt:
            errors.append(f"{route}: twitter:image:alt mismatch or absent")
        for label, url in (
            ("canonical", document.canonical),
            ("og:url", document.meta_properties.get("og:url", "")),
            ("og:image", document.meta_properties.get("og:image", "")),
            ("twitter:image", document.meta_names.get("twitter:image", "")),
        ):
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{route}: {label} is not absolute HTTPS")
        for forbidden in FORBIDDEN_STALE_STRINGS:
            if forbidden.casefold() in text.casefold():
                errors.append(f"{route}: forbidden stale string present: {forbidden}")

        title_key = document.title.casefold()
        if expected.indexable and title_key in seen_titles:
            errors.append(
                f"{route}: indexable title duplicates {seen_titles[title_key]}: {document.title}"
            )
        elif expected.indexable:
            seen_titles[title_key] = route

        image_rel = expected_image.removeprefix(config["site_origin"]).lstrip("/")
        image_path = artifact / image_rel
        image_info = image_cache.get(image_rel)
        if image_info is None:
            if not image_path.is_file():
                errors.append(f"{route}: referenced preview image is absent: {image_rel}")
                image_info = {"width": 0, "height": 0, "sha256": "", "bytes": 0}
            else:
                try:
                    with Image.open(image_path) as source:
                        source.verify()
                    with Image.open(image_path) as source:
                        width, height = source.size
                        image_format = source.format
                    if (width, height) != (CARD_WIDTH, CARD_HEIGHT):
                        errors.append(f"{route}: preview image is not 1200x630")
                    if image_format != "PNG":
                        errors.append(f"{route}: preview image format is not PNG")
                    if mimetypes.guess_type(image_path.name)[0] != "image/png":
                        errors.append(f"{route}: preview image MIME type is not image/png")
                    image_info = {
                        "width": width,
                        "height": height,
                        "sha256": sha256_file(image_path),
                        "bytes": image_path.stat().st_size,
                    }
                except (OSError, ValueError) as exc:
                    errors.append(f"{route}: invalid PNG: {exc}")
                    image_info = {"width": 0, "height": 0, "sha256": "", "bytes": 0}
            image_cache[image_rel] = image_info

        route_rows.append(
            {
                "route": route,
                "canonical_url": canonical,
                "title": document.title,
                "description": document.meta_names.get("description", ""),
                "og_image": expected_image,
                "profile": expected.profile,
                "indexability": "indexable" if expected.indexable else "noindex",
                "noindex_reason": expected.noindex_reason,
                "png_dimensions": {
                    "width": image_info["width"],
                    "height": image_info["height"],
                },
                "image_sha256": image_info["sha256"],
                "verdict": "PASS" if expected.indexable else "NOINDEX_DOCUMENTED",
            }
        )

    retired_name = "noetfield-" + "og.png"
    for retired in (ROOT / retired_name, artifact / retired_name):
        if retired.exists():
            errors.append(f"retired social image still exists: {retired}")

    images: list[dict[str, Any]] = []
    for profile, card in config["cards"].items():
        rel = f"assets/social/{card['filename']}"
        info = image_cache.get(rel)
        if info is None:
            errors.append(f"unreferenced or absent canonical card: {rel}")
            info = {"width": 0, "height": 0, "sha256": "", "bytes": 0}
        images.append(
            {
                "profile": profile,
                "path": f"/{rel}",
                "width": info["width"],
                "height": info["height"],
                "sha256": info["sha256"],
                "bytes": info["bytes"],
            }
        )

    receipt = {
        "schema": "noetfield-social-preview-verification-v2",
        "verdict": "PASS" if not errors else "FAIL",
        "artifact": "www-pages-dist",
        "route_count": len(route_rows),
        "indexable_route_count": sum(row["indexability"] == "indexable" for row in route_rows),
        "noindex_route_count": sum(row["indexability"] == "noindex" for row in route_rows),
        "images": images,
        "routes": route_rows,
    }
    if not errors:
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return receipt, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    render = subparsers.add_parser("render")
    render.add_argument("--output-dir", type=Path, default=ROOT / "assets" / "social")
    check = subparsers.add_parser("check-render")
    check.add_argument("--expected-dir", type=Path, default=ROOT / "assets" / "social")
    subparsers.add_parser("sync-sources")
    verify = subparsers.add_parser("verify")
    verify.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    verify.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()

    try:
        if args.command == "render":
            outputs = render_cards(args.output_dir)
            for output in outputs:
                display_path = output.relative_to(ROOT) if output.is_relative_to(ROOT) else output
                print(f"rendered {display_path} sha256={sha256_file(output)}")
            return 0
        if args.command == "check-render":
            errors = check_render(args.expected_dir)
            if errors:
                for error in errors:
                    print(f"FAIL social-preview render: {error}")
                return 1
            print("social-preview render determinism: PASS")
            return 0
        if args.command == "sync-sources":
            count = sync_source_metadata()
            print(f"social-preview source metadata: updated {count} key routes")
            return 0
        receipt, errors = verify_package(args.artifact, args.receipt)
        if errors:
            for error in errors:
                print(f"FAIL social-preview verifier: {error}")
            print(f"social-preview verifier: FAIL ({len(errors)} findings)")
            return 1
        print(
            "social-preview verifier: PASS "
            f"routes={receipt['route_count']} "
            f"indexable={receipt['indexable_route_count']} "
            f"noindex={receipt['noindex_route_count']}"
        )
        print(f"receipt={args.receipt}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL social-preview {args.command}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
