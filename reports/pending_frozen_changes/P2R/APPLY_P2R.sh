#!/usr/bin/env bash
# HUMAN ONLY, at GO PREREG-R. Installs the P2R replication amendment before any P2R model run:
#   reports/pending_frozen_changes/P2R/A_P2R_new_families.md -> prereg/amendments/A_P2R_new_families.md (write-once)
#   prereg/amendments/A_P2R_new_families.sha256: sha256 of the amendment and of the P2R code it freezes
#   gates.yaml: gate PREREG-R (reports/pending_frozen_changes/P2R/gates_PREREGR.txt)
#   prereg/INDEX.md: one line
#   tag prereg-P2R on the resulting commit
# Requires APPLY_precommit_fix.sh to have been applied (otherwise every commit is rejected).
set -euo pipefail
cd "$(dirname "$0")/../../.."
S=reports/pending_frozen_changes/P2R
[ -e prereg/amendments/A_P2R_new_families.md ] && { echo "REFUSED: amendment already installed" >&2; exit 1; }
grep -q "excluded from the byte comparison" scripts/pre-commit || { echo "REFUSED: apply APPLY_precommit_fix.sh first" >&2; exit 1; }
python3 scripts/log_run.py --tag "P2R tests before the freeze (EXPLORATORY test only; no model data)" --status EXPLORATORY --seed 0 \
  --in analysis/p2r/p2r_analysis.py --in analysis/p2r/p2r_combine.py --in analysis/p2r/p2r_test.py -- .venv/bin/python analysis/p2r/p2r_test.py
# everything the session and analysis need, and the paper state that stays fixed (section 7), must already be committed
for f in analysis/p2r/p2r_analysis.py analysis/p2r/p2r_combine.py analysis/p2r/p2r_test.py analysis/p2r/p2r_tokcheck.py \
         analysis/p2r/p2r_weights_check.py analysis/g5/g5_expl_object.R materials/p2r_weights_pinned.json results/P2R/tokcheck.json \
         results/P2R/hubcheck_test.json results/P2R/cachecheck_test.json results/P2R/cachecheck_negtest.json \
         reports/p2r/GPU_RUNBOOK_P2R.md "$S/A_P2R_new_families.md" paper/main.tex paper/appendix.tex paper/numbers.tex paper/models.tex; do
  git ls-files --error-unmatch "$f" > /dev/null || { echo "REFUSED: $f is not committed" >&2; exit 1; }
  git diff --quiet HEAD -- "$f" || { echo "REFUSED: $f has uncommitted changes" >&2; exit 1; }
done
# the wording rules (amendment section 5(c)) assume the paper as it is now: 199-word abstract ending with the
# decision-study sentence, and the five anchor texts L1-L5 plus the Limitations sentence
python3 - <<'PYEOF'
t = open("paper/main.tex").read()
a = t[t.index("\\begin{abstract}") + len("\\begin{abstract}"):t.index("\\end{abstract}")].strip()
assert len(a.split()) == 199, f"abstract has {len(a.split())} words, amendment assumes 199"
assert a.splitlines()[-1].startswith("A decision study estimates"), "abstract does not end with the decision-study sentence"
m = open("paper/models.tex").read()
for macro in ["\\newcommand{\\GemmaTwoNineB}{Gemma-2-9B}", "\\newcommand{\\MistralSevenB}{Mistral-7B-v0.1}"]:
    assert m.count(macro) == 1, f"macro missing in paper/models.tex: {macro}"
for anchor in ["In a separate study of \\llama{} and \\olmo, on correctly answered prompts, the fact share is above zero",
               "is not licensed (Table~\\ref{tab:rules})",
               "Only the first sentence is licensed.}",
               "\\section{What this implies for single-prompt depths}",
               "\\label{sec:p2}",
               "\\item A preregistered variance decomposition of readout depth over facts and paraphrases",
               "\\paragraph{The fact share is above zero; separating answer identity lowers it.}",
               "\\paragraph{What the licensed sentence says.}",
               "In both models the estimated paraphrase-related share is larger than the estimated fact share",
               "\\section{Conclusion}",
               "The estimated paraphrase-related share is larger, confirmed by the preregistered test in one of two models",
               "Code, materials, curves and the preregistration record will be released",
               "\\STwo includes two model families, which share answer first-token ids",
               "\\paragraph{Agreement across models.}",
               "\\paragraph{Decision study.}",
               "\\subsection{Robustness simulation (non-selecting)}",
               "As an \\expl estimate for our depth measure, in our two models and on correct prompts,",
               "Both studies are English and use models of at most eight billion parameters."]:
    assert t.count(anchor) == 1, f"anchor not found exactly once: {anchor}"
print("paper anchors and abstract length: OK")
PYEOF
mkdir -p prereg/amendments
cp "$S/A_P2R_new_families.md" prereg/amendments/A_P2R_new_families.md
sha256sum prereg/amendments/A_P2R_new_families.md analysis/p2r/p2r_analysis.py analysis/p2r/p2r_combine.py \
  analysis/p2r/p2r_tokcheck.py analysis/p2r/p2r_test.py analysis/p2r/p2r_weights_check.py analysis/g5/g5_expl_object.R \
  materials/p2r_weights_pinned.json results/P2R/tokcheck.json reports/p2r/GPU_RUNBOOK_P2R.md \
  results/P2R/hubcheck_test.json results/P2R/cachecheck_test.json results/P2R/cachecheck_negtest.json \
  paper/main.tex paper/appendix.tex paper/numbers.tex paper/models.tex > prereg/amendments/A_P2R_new_families.sha256
echo "| prereg/amendments/A_P2R_new_families.md (+ .sha256) | P2R confirmatory replication in two new families (Gemma-2-9B, Mistral-7B-v0.1) | tag prereg-P2R |" >> prereg/INDEX.md
chattr -i gates.yaml 2>/dev/null || true
grep -q '^  PREREG-R:' gates.yaml || cat "$S/gates_PREREGR.txt" >> gates.yaml
python3 -c "import yaml; g = yaml.safe_load(open('gates.yaml'))['gates']; assert 'PREREG-R' in g, g; print('gates.yaml PREREG-R:', g['PREREG-R'])"
python3 scripts/log_run.py --kind NOTE --tag "HUMAN-AUTHORIZED FROZEN CHANGE: install P2R amendment and gate PREREG-R" --status ADMIN \
  --note "GO PREREG-R: installed prereg/amendments/A_P2R_new_families.md and .sha256, gate PREREG-R in gates.yaml, INDEX line." \
  --file gates.yaml --file prereg/amendments/A_P2R_new_families.md
git add prereg/amendments/A_P2R_new_families.md prereg/amendments/A_P2R_new_families.sha256 prereg/INDEX.md gates.yaml results/ledger.jsonl
DEPTHLAW_FROZEN_OVERRIDE=1 git commit -m "human: freeze P2R replication amendment (two new families); gate PREREG-R" -- \
  prereg/amendments/A_P2R_new_families.md prereg/amendments/A_P2R_new_families.sha256 prereg/INDEX.md gates.yaml results/ledger.jsonl
git tag prereg-P2R
bash scripts/install_guard.sh
echo "frozen: prereg-P2R = $(git rev-parse --short HEAD); push with: git push origin master prereg-P2R"
