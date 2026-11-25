#!/usr/bin/env bash
# Build the G5 draft: appendix tables (logged), check_numbers, verify_bib, latexmk; prints the page count and the
# page on which the main text ends (the Limitations heading).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/log_run.py --tag "paper appendix tables generated from numbers.tex macro names and integrity summary" \
  --status CONFIRMATORY --seed 0 --in paper/numbers.tex --in results/integrity/summary.json --in scripts/make_tables.py \
  --out paper/generated/robust.tex --out paper/generated/sens.tex --out paper/generated/hrvar.tex \
  --out paper/generated/reviews.tex --out paper/generated/guardtests.tex -- .venv/bin/python scripts/make_tables.py
.venv/bin/python scripts/check_numbers.py
.venv/bin/python scripts/verify_bib.py
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex > build.log 2>&1 || { tail -30 build.log; exit 1; }
grep -E "^!|undefined|Overfull" main.log | sort | uniq -c || true
echo "pages: $(pdfinfo main.pdf | awk '/^Pages/{print $2}')"
for p in $(seq 1 "$(pdfinfo main.pdf | awk '/^Pages/{print $2}')"); do
  if pdftotext -f "$p" -l "$p" main.pdf - | grep -q "^Limitations$"; then echo "Limitations heading on page $p"; fi
done
