#!/usr/bin/env python3
"""Fail if paper prose has bare numbers, numbers.tex is stale, or a preregistered test is unreported."""
import hashlib, json, pathlib, re, sys
P, errors = pathlib.Path("paper"), []
if not (P / "numbers.tex").exists():  # added: report instead of crashing
    print("paper/numbers.tex missing (generate it with scripts/make_numbers.py)"); sys.exit(1)
nums = (P / "numbers.tex").read_text()
hdr = re.search(r"^% inputs: (\{.*\})$", nums, re.M)  # written by make_numbers.py
if not hdr:
    errors.append("numbers.tex lacks '% inputs: {...}' provenance header")
else:
    for path, sha in json.loads(hdr.group(1)).items():
        f = pathlib.Path(path)
        if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest() != sha:
            errors.append(f"stale or missing input: {path}")
macros = set(re.findall(r"\\newcommand\{\\(\w+)\}", nums))
req = pathlib.Path("config/required_macros.json")
for m in (json.loads(req.read_text()) if req.exists() else []):
    if m not in macros:
        errors.append(f"preregistered result \\{m} missing from numbers.tex")
ALLOW = re.compile(r"(19|20)\d\d|\d+(\.\d+)?[bBmMkK]")
STRIP = re.compile(r"\\(cite\w*|ref|eqref|cref|label|includegraphics|input|include|usepackage|"
                   r"documentclass|begin|end|vspace|hspace|setlength|url|href)\*?(\[[^\]]*\])?\{[^}]*\}")
for tex in P.rglob("*.tex"):
    if tex.name == "numbers.tex" or "generated" in tex.parts:
        continue
    for i, line in enumerate(tex.read_text().splitlines(), 1):
        if "allow-number" in line:
            continue
        s = re.sub(r"\\\w+", "", STRIP.sub("", line.split("%")[0]))
        for tok in re.findall(r"(?<![\w.\-])\d+(?:\.\d+)?[a-zA-Z]?", s):
            if not ALLOW.fullmatch(tok):
                errors.append(f"{tex}:{i}: bare number '{tok}' (use a numbers.tex macro)")
print("\n".join(errors) or "check_numbers: ok"); sys.exit(1 if errors else 0)
