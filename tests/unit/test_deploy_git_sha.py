"""deploy_git_sha — runtime GIT_SHA must win over baked .deploy_git_sha stamp."""

from __future__ import annotations

from pathlib import Path

from noetfield_governance import api as api_mod
from noetfield_governance.api import deploy_git_sha


def test_deploy_git_sha_from_env(monkeypatch) -> None:
    monkeypatch.setenv("GIT_SHA", "d8bb0e16194ef65acb8d356acbf143d539ff3145")
    assert deploy_git_sha() == "d8bb0e16194ef65acb8d356acbf143d539ff3145"


def test_deploy_git_sha_env_wins_over_stamp(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    api_path = repo_root / "services" / "governance" / "noetfield_governance" / "api.py"
    api_path.parent.mkdir(parents=True)
    api_path.write_text("# stub\n", encoding="utf-8")
    stamp = repo_root / ".deploy_git_sha"
    stamp.write_text("e0bb318c9ef8deadbeefdeadbeefdeadbeefdeadbeef\n", encoding="utf-8")

    monkeypatch.setattr(api_mod, "__file__", str(api_path))
    monkeypatch.setenv("GIT_SHA", "50dd9fdb5cc59aac43790c243fba313f57fea4e5")
    assert deploy_git_sha() == "50dd9fdb5cc59aac43790c243fba313f57fea4e5"
