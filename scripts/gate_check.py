#!/usr/bin/env python3
"""gate_check.py <G>: required gate reports present, each with a VERDICT:/RECOMMEND: line and no
'VERDICT: BLOCK'; responses.md present when needs_responses. Exit 1 on any problem (docs/guards.md 3.4)."""
import pathlib, re, sys
import yaml

root = pathlib.Path(__file__).resolve().parents[1]
if len(sys.argv) != 2:
    print("usage: gate_check.py <G>"); sys.exit(1)
g = sys.argv[1]
gates = (yaml.safe_load((root / "gates.yaml").read_text()) or {}).get("gates", {})
if g not in gates:
    print(f"gate {g}: not defined in gates.yaml"); sys.exit(1)
spec, d, problems = gates[g] or {}, root / "reports" / "gates" / g, []
for agent in spec.get("requires", []):
    f = d / f"{agent}.md"
    if not f.exists():
        problems.append(f"{f.relative_to(root)}: missing")
        continue
    t = f.read_text()
    if re.search(r"VERDICT:\s*BLOCK", t):
        problems.append(f"{f.relative_to(root)}: VERDICT: BLOCK")
    if not re.search(r"^\s*(VERDICT|RECOMMEND):", t, re.M):
        problems.append(f"{f.relative_to(root)}: no VERDICT: or RECOMMEND: line")
if spec.get("needs_responses") and not (d / "responses.md").exists():
    problems.append(f"reports/gates/{g}/responses.md: missing")
print("\n".join(problems) or f"gate {g}: ready")
sys.exit(1 if problems else 0)
