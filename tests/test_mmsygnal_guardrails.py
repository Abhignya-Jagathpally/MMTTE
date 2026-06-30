"""Guardrails for the mmSYGNAL external benchmark (GPL-3.0, not vendored)."""
from pathlib import Path
import subprocess
import yaml

REPO = Path(__file__).resolve().parents[1]
RDS_NAMES = [
    "agnostic_risk_model.Rds", "amp(1q)_risk_model.Rds", "del(13)_risk_model.Rds",
    "del(1p)_risk_model.Rds", "t(4;14)_risk_model.Rds", "FGFR3_risk_model.Rds",
]


def test_mmsygnal_weights_not_vendored():
    """No mmSYGNAL .Rds artifact may live OUTSIDE external/ (would carry GPL-3.0)."""
    offenders = [str(p.relative_to(REPO)) for p in REPO.rglob("*.Rds")
                 if "external/" not in str(p.relative_to(REPO))]
    assert not offenders, f"mmSYGNAL/.Rds artifacts copied outside external/: {offenders}"


def test_mmsygnal_not_git_tracked():
    """Git must not track the cloned external repo or its weights."""
    try:
        tracked = subprocess.check_output(
            ["git", "-C", str(REPO), "ls-files", "external/"], text=True).strip()
    except Exception:
        tracked = ""
    assert "mmSYGNAL" not in tracked, f"external mmSYGNAL is git-tracked: {tracked[:200]}"


def test_benchmark_claim_policy_blocks_relapse():
    cfg = yaml.safe_load((REPO / "configs/benchmarks/mmsygnal.yaml").read_text())
    pol = cfg["claim_policy"]
    assert pol["direct_relapse_pfs_claim_allowed"] is False
    assert pol["clinical_use_allowed"] is False
    assert pol["research_benchmark_allowed"] is True


def test_provenance_doc_records_license_and_commit():
    doc = (REPO / "docs/third_party/mmSYGNAL_provenance.md").read_text()
    assert "GPL-3.0" in doc
    assert "6017dd8d" in doc  # upstream commit
