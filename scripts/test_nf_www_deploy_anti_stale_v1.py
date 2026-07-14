#!/usr/bin/env python3
"""Unit tests for nf_www_deploy_anti_stale_v1 (no network)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nf_www_deploy_anti_stale_v1 import evaluate_homepage, load_ssot, run_gate

GOOD = """<!doctype html><html><body class="nf-gate">
<a href="/enterprise/">Enterprise</a>
<a href="/motors/">Motor</a>
<a href="/proof/">Proof</a>
</body></html>"""

LEAK = """<!doctype html><html><body class="nf-gate">
<a href="/enterprise/">Enterprise</a>
<a href="/motors/">Motor</a>
<a href="/proof/">Proof</a>
<a href="/investors/">Investor</a>
<span>Invest in Noetfield</span>
</body></html>"""

STALE_MISSING = """<!doctype html><html><body>
<a href="/about/">About</a>
</body></html>"""


class AntiStaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ssot = load_ssot()

    def test_good_dist_offline(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "index.html").write_text(GOOD, encoding="utf-8")
            result = run_gate(dist_dir=p, live_base=None, ssot=self.ssot)
            self.assertTrue(result["ok"], result)

    def test_forbidden_leak_offline(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "index.html").write_text(LEAK, encoding="utf-8")
            result = run_gate(dist_dir=p, live_base=None, ssot=self.ssot)
            self.assertFalse(result["ok"])
            self.assertIn("DIST_FORBIDDEN_LEAK", result["reasons"])
            self.assertTrue(result["dist"]["present_forbidden"])

    def test_live_ahead_missing_required(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "index.html").write_text(STALE_MISSING, encoding="utf-8")
            result = run_gate(
                dist_dir=p,
                live_base="https://www.noetfield.com",
                ssot=self.ssot,
                live_html=GOOD,
            )
            self.assertFalse(result["ok"])
            self.assertIn("LIVE_AHEAD_OF_DIST", result["reasons"])

    def test_live_ahead_reintroduces_leak(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / "index.html").write_text(LEAK, encoding="utf-8")
            result = run_gate(
                dist_dir=p,
                live_base="https://www.noetfield.com",
                ssot=self.ssot,
                live_html=GOOD,
            )
            self.assertFalse(result["ok"])
            self.assertIn("LIVE_AHEAD_OF_DIST", result["reasons"])
            self.assertTrue(any("LIVE_AHEAD_LEAK" in e for e in result["errors"]))

    def test_evaluate_homepage_direct(self) -> None:
        lock = self.ssot["homepage_lock"]
        self.assertTrue(evaluate_homepage(GOOD, lock)["ok"])
        self.assertFalse(evaluate_homepage(LEAK, lock)["ok"])


if __name__ == "__main__":
    unittest.main()
