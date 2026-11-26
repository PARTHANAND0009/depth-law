#!/usr/bin/env python3
"""P2R tokenizer check (tokenizers only, no model weights; amendment A_P2R_new_families section 3).
For every fact x all 10 paraphrases: does the frozen object-token rule (obj_ids: first token of " " + object) equal
the first token that follows the filled prompt when " " + object is appended? Also: bare-space first tokens, and
first-token distinctness among the objects of each relation. Writes counts per tokenizer to <out.json>.
Run through scripts/log_run.py at the standing CPU cap with HF_HUB_OFFLINE=1 (tokenizers cached).
Usage: p2r_tokcheck.py <out.json> <model> [<model> ...]"""
import json
import sys
from pathlib import Path

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]
facts = [json.loads(l) for l in open(ROOT / "materials/facts_v1.jsonl")]
paras = {}
for l in open(ROOT / "materials/paraphrases_v1.jsonl"):
    p = json.loads(l); paras.setdefault(p["relation"], []).append(p)
out = {"status": "tokenizer check (no model outputs)", "models": {}}
for name in sys.argv[2:]:
    tok = AutoTokenizer.from_pretrained(name, local_files_only=True)
    n = n_diff = n_space = 0
    firsts = {}
    for f in facts:
        oi = tok.encode(" " + f["object"], add_special_tokens=False)[0]
        n_space += tok.convert_ids_to_tokens(oi) in ("▁", "Ġ", " ")
        firsts.setdefault(f["relation"], {}).setdefault(oi, set()).add(f["object"])
        for p in paras[f["relation"]]:
            prompt = p["template"].format(f["subject"])
            a = tok(prompt, add_special_tokens=False)["input_ids"]
            b = tok(prompt + " " + f["object"], add_special_tokens=False)["input_ids"]
            k = 0
            while k < len(a) and k < len(b) and a[k] == b[k]:
                k += 1
            n += 1
            n_diff += (b[k] if k < len(b) else None) != oi
    shared = sum(len(o) for rel in firsts.values() for o in rel.values() if len(o) > 1)
    out["models"][name] = {"fact_paraphrase_pairs": n, "obj_ids_differs_from_continuation": n_diff,
                           "bare_space_first_token_facts": n_space, "facts_sharing_first_token_within_relation": shared,
                           "vocab_size": len(tok)}
    print(name, out["models"][name])
Path(sys.argv[1]).parent.mkdir(parents=True, exist_ok=True)
Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + "\n")
