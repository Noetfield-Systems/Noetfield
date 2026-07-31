#!/usr/bin/env python3
"""Product preservation gate (NOETFIELD_PRODUCT_SURFACE_RECOVERY_V1, P7).

Fails when the site loses a capability, route, CTA, or product card that the
manifest still declares active — and when a manifest removal lacks founder
approval, a replacement route, or a recorded reason. Claim auditing may narrow
wording or add status labels; it may not delete product surface.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "governance" / "product-surface-manifest-v1.json"

REQUIRED_CAPABILITY_FIELDS = (
    "capability_id",
    "route",
    "surface",
    "maturity",
    "state",
    "backend_binding",
    "evidence_link",
    "founder_approved_visibility",
    "needle",
)
REQUIRED_REMOVAL_FIELDS = (
    "capability_id",
    "reason",
    "replacement_route",
    "founder_approved",
    "removed_at",
)
PRIMARY_NAV_LABELS = (
    ">Product<",
    ">Workflows<",
    ">Assurance<",
    ">Developers<",
    ">TrustField<",
    ">Proof<",
    ">Company<",
)


def main() -> int:
    failures: list[str] = []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    seen: set[str] = set()
    for cap in data.get("capabilities", []):
        for field in REQUIRED_CAPABILITY_FIELDS:
            if field not in cap:
                failures.append(f"{cap.get('capability_id', '?')}: missing field {field}")
        cap_id = cap.get("capability_id", "?")
        if cap_id in seen:
            failures.append(f"duplicate capability_id {cap_id}")
        seen.add(cap_id)
        if cap.get("state") != "active":
            continue
        surface = cap.get("surface", "")
        if surface in ("", "external"):
            continue
        path = ROOT / surface
        if not path.is_file():
            failures.append(f"{cap_id}: surface file missing: {surface}")
            continue
        needle = cap.get("needle", "")
        if needle and needle not in path.read_text(encoding="utf-8"):
            failures.append(f"{cap_id}: needle not found in {surface}: {needle!r}")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for label in PRIMARY_NAV_LABELS:
        if label not in home:
            failures.append(f"primary nav label missing from homepage: {label}")

    for removal in data.get("removals", []):
        for field in REQUIRED_REMOVAL_FIELDS:
            if field not in removal:
                failures.append(
                    f"removal {removal.get('capability_id', '?')}: missing {field}"
                )
        if removal.get("founder_approved") is not True:
            failures.append(
                f"removal {removal.get('capability_id', '?')}: founder_approved must be true"
            )
        if not str(removal.get("reason", "")).strip():
            failures.append(
                f"removal {removal.get('capability_id', '?')}: reason must be recorded"
            )
        if removal.get("capability_id") in seen:
            failures.append(
                f"removal {removal.get('capability_id', '?')}: still present in capabilities"
            )

    if failures:
        for failure in failures:
            print(f"FAIL product-surface-manifest: {failure}")
        return 1
    active = sum(1 for c in data.get("capabilities", []) if c.get("state") == "active")
    print(f"verify-product-surface-manifest: PASS ({active} active capabilities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
