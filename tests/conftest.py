import os
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("HF_HOME", str(ROOT / "cache" / "hf"))

TEST_MODEL = os.environ.get("DEPTHLAW_TEST_MODEL", "EleutherAI/pythia-70m")


@pytest.fixture(scope="session")
def lm():
    from depthlaw.depth.common import load_lm
    return load_lm(TEST_MODEL)


@pytest.fixture(scope="session")
def hand_facts():
    return yaml.safe_load(open(ROOT / "configs" / "hand_facts.yaml"))["facts"]


@pytest.fixture(scope="session")
def carriers():
    return yaml.safe_load(open(ROOT / "configs" / "s3.yaml"))["carriers"]


@pytest.fixture(scope="session")
def lm_knows():
    """Fact-dependent tests need a model that knows the hand facts: pythia-70m gets 0/20
    correct at rank 1, pythia-410m 14/20 (checked 2026-11-05), so these use 410m."""
    from depthlaw.depth.common import load_lm
    return load_lm(os.environ.get("DEPTHLAW_KNOWS_MODEL", "EleutherAI/pythia-410m"))
