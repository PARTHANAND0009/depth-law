#!/usr/bin/env python3
"""P2R analysis: the frozen P2 analysis (analysis/p2/p2_analysis.py, unchanged) applied to the two replication models
of amendment A_P2R_new_families. This wrapper changes only three module constants before calling the frozen main():
  PREREG_MODELS -> the two P2R models (the gating call must name exactly these, MODEL=none for a model with no run);
  TOKMAP        -> adds the two new families ("gemma" -> gemma2, "mistral" -> mistral);
  nothing else: materials sha256, n_boot = n_null = 1000, inclusion rule (>= 150 facts with >= 2 correct paraphrases,
                >= 15 relations), formula, CI method, null, decision rules and wording rules are the frozen ones.
Usage (same arguments as p2_analysis.py):
  p2r_analysis.py <out> --runs google/gemma-2-9b=<run_dir|none> mistralai/Mistral-7B-v0.1=<run_dir|none> --set correct
then the sensitivity sets with --primary <out>, as in prereg P2 section 7."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "p2"))
import p2_analysis as PA  # noqa: E402  (frozen code, imported, not modified)

P2R_MODELS = ("google/gemma-2-9b", "mistralai/Mistral-7B-v0.1")
P2R_FAMILIES = {"gemma": "gemma2", "mistral": "mistral"}


def configure():
    PA.PREREG_MODELS = P2R_MODELS
    PA.TOKMAP = {**PA.TOKMAP, **P2R_FAMILIES}
    for m in P2R_MODELS:  # each replication model must map to a family not tested in P2
        fam = PA.family(m)
        assert fam in P2R_FAMILIES.values(), (m, fam)


if __name__ == "__main__":
    configure()
    PA.main()
