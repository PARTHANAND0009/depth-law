"""P2 A2: 10 paraphrase templates per relation from a shared frame design, plus validation on facts_v1.

Frames (shared across relations, so frame is a crossed factor):
  order  (subject-first SF, relation-first RF) x form (cloze, question "Q: ...?\\nA:") x length (short, long)
  long = the shared neutral clause "According to reference sources, " placed at the start of the
  statement / question; plus 2 lexical variants (LEX1: reworded SF cloze, LEX2: reworded RF cloze; short).
Every prompt ends where the next token is the answer's first token (cloze stems end before the object;
questions end with "A:").
Validation per fact x paraphrase (tokenizers: llama31, qwen3, pythia, olmo2): subject appears exactly once,
object string absent (case-insensitive), token length, subject-to-final distance (as in the S3 code).
Writes materials/paraphrases_v1.jsonl (+ .sha256) and materials/paraphrases_v1_validation.csv (+ report).
"""
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from depthlaw.hr.assemble import subj_final_dist  # noqa: E402

TOK = {"llama31": "meta-llama/Llama-3.1-8B", "qwen3": "Qwen/Qwen3-8B", "pythia": "EleutherAI/pythia-1.4b",
       "olmo2": "allenai/OLMo-2-1124-7B"}
NEUTRAL = "According to reference sources, "
# relation: (SF cloze, RF cloze, SF question, RF question, LEX1 (SF cloze variant), LEX2 (RF cloze variant))
STEMS = {
    "citizenship": ("{} is a citizen of", "The country of citizenship of {} is", "{} is a citizen of which country?",
                    "Which country is {} a citizen of?", "{} holds citizenship of", "The country whose citizenship {} holds is"),
    "continent": ("{} is located on the continent of", "The continent where {} is located is", "{} is located on which continent?",
                  "Which continent is {} located on?", "{} lies on the continent of", "The continent on which {} lies is"),
    "country": ("{} is located in the country of", "The country where {} is located is", "{} is located in which country?",
                "Which country is {} located in?", "{} is situated in the country of", "The country in which {} is situated is"),
    "country_of_origin": ("{} originated in the country of", "The country of origin of {} is", "{} originated in which country?",
                          "Which country did {} originate in?", "{} comes from the country of", "The country that {} comes from is"),
    "employer": ("{} is employed by", "The employer of {} is", "{} is employed by which organization?",
                 "Which organization employs {}?", "{} works for", "The organization that employs {} is"),
    "field_of_work": ("{} works in the field of", "The field of work of {} is", "{} works in which field?",
                      "Which field does {} work in?", "{} is a specialist in the field of", "The area of expertise of {} is"),
    "formation_location": ("{} was founded in the city of", "The city where {} was founded is", "{} was founded in which city?",
                           "Which city was {} founded in?", "{} was formed in the city of", "The city in which {} was formed is"),
    "headquarters": ("{} is headquartered in the city of", "The city where {} is headquartered is", "{} is headquartered in which city?",
                     "Which city is {} headquartered in?", "{} has its headquarters in the city of", "The city that hosts the headquarters of {} is"),
    "instrument": ("{} plays the", "The instrument played by {} is the", "{} plays which instrument?",
                   "Which instrument does {} play?", "{} is known for playing the", "The musical instrument of {} is the"),
    "manufacturer": ("{} is manufactured by", "The manufacturer of {} is", "{} is manufactured by which company?",
                     "Which company manufactures {}?", "{} is produced by", "The company that makes {} is"),
    "music_genre": ("{} performs music in the genre of", "The musical genre of {} is", "{} performs music in which genre?",
                    "Which musical genre does {} perform?", "{} is known for playing the genre of", "The style of music performed by {} is"),
    "native_language": ("{} is a native speaker of", "The native language of {} is", "{} is a native speaker of which language?",
                        "Which language is the native language of {}?", "{} grew up speaking", "The mother tongue of {} is"),
    "occupation": ("{} works as a", "The occupation of {} is", "{} has which occupation?",
                   "What is the occupation of {}?", "{} is by profession a", "The profession of {} is"),
    "official_language": ("{} has as its official language", "The official language of {} is", "{} has which official language?",
                          "What is the official language of {}?", "In {}, the official language is", "The language officially used in {} is"),
    "original_language": ("{} was originally produced in the language", "The original language of {} is",
                          "{} was originally produced in which language?", "What is the original language of {}?",
                          "{} was first made in the language", "The language in which {} was originally made is"),
    "original_network": ("{} originally aired on", "The original network of {} is", "{} originally aired on which network?",
                         "Which network originally aired {}?", "{} was first broadcast on", "The network that first broadcast {} is"),
    "place_of_death": ("{} died in the city of", "The place of death of {} is", "{} died in which city?",
                       "Which city did {} die in?", "{} passed away in the city of", "The city where {} died is"),
    "sport": ("{} plays the sport of", "The sport played by {} is", "{} plays which sport?",
              "Which sport does {} play?", "{} is a professional player of", "The sport that {} competes in is"),
    "sport_position": ("{} plays in the position of", "The position played by {} is", "{} plays in which position?",
                       "Which position does {} play?", "{} plays as a", "The playing position of {} is"),
    "work_location": ("{} worked in the city of", "The city where {} worked is", "{} worked in which city?",
                      "Which city did {} work in?", "{} was employed in the city of", "The city in which {} was employed is"),
}


def lc(s):
    return s if s.startswith("{}") else s[0].lower() + s[1:]


def templates(rel):
    sf, rf, qsf, qrf, lx1, lx2 = STEMS[rel]
    q = lambda body: f"Q: {body}\nA:"  # noqa: E731
    rows = [("SF", "cloze", "short", sf), ("SF", "cloze", "long", NEUTRAL + lc(sf)),
            ("RF", "cloze", "short", rf), ("RF", "cloze", "long", NEUTRAL + lc(rf)),
            ("SF", "question", "short", q(qsf)), ("SF", "question", "long", q(NEUTRAL + lc(qsf))),
            ("RF", "question", "short", q(qrf)), ("RF", "question", "long", q(NEUTRAL + lc(qrf)))]
    out = [{"relation": rel, "template_id": i, "frame": f"{o}-{fm}-{ln}", "order": o, "form": fm, "length": ln,
            "lexical_variant": False, "template": t} for i, (o, fm, ln, t) in enumerate(rows)]
    out.append({"relation": rel, "template_id": 8, "frame": "LEX1-SF-cloze-short", "order": "SF", "form": "cloze",
                "length": "short", "lexical_variant": True, "template": lx1})
    out.append({"relation": rel, "template_id": 9, "frame": "LEX2-RF-cloze-short", "order": "RF", "form": "cloze",
                "length": "short", "lexical_variant": True, "template": lx2})
    return out


def main():
    facts = [json.loads(l) for l in open(ROOT / "materials/facts_v1.jsonl")]
    rels = sorted({f["relation"] for f in facts})
    assert set(rels) <= set(STEMS), set(rels) - set(STEMS)
    T = [t for r in rels for t in templates(r)]
    for t in T:
        assert t["template"].count("{}") == 1, t
    dst = ROOT / "materials/paraphrases_v1.jsonl"
    dst.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in T))
    sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    (ROOT / "materials/paraphrases_v1.jsonl.sha256").write_text(f"{sha}  materials/paraphrases_v1.jsonl\n")
    toks = {k: AutoTokenizer.from_pretrained(v, local_files_only=True) for k, v in TOK.items()}
    rows = []
    byrel = {}
    for t in T:
        byrel.setdefault(t["relation"], []).append(t)
    for f in facts:
        for t in byrel[f["relation"]]:
            text = t["template"].format(f["subject"])
            row = {"fact_id": f["fact_id"], "relation": f["relation"], "template_id": t["template_id"], "frame": t["frame"],
                   "subject_once": text.count(f["subject"]) == 1,
                   "answer_absent": f["object"].lower() not in text.lower()}
            for k, tk in toks.items():
                row[f"n_tokens_{k}"] = len(tk(text)["input_ids"])
                row[f"subj_final_dist_{k}"] = subj_final_dist(tk, t["template"], f["subject"])
            rows.append(row)
    V = pd.DataFrame(rows)
    V.to_csv(ROOT / "materials/paraphrases_v1_validation.csv", index=False)
    bad = V[~(V.subject_once & V.answer_absent)]
    L = ["# P2 paraphrases v1: validation", "",
         f"- **Templates:** {len(T)} ({len(rels)} relations × 10); sha256 {sha}.",
         f"- **Prompts checked:** {len(V)} fact × paraphrase.",
         f"- **Subject exactly once:** {int(V.subject_once.sum())}/{len(V)}.",
         f"- **Answer string absent:** {int(V.answer_absent.sum())}/{len(V)}.", "",
         "Failing prompts (excluded from P2 at analysis time):", ""]
    L += [f"- {r.fact_id} {r.relation} t{r.template_id}: subject_once={r.subject_once} answer_absent={r.answer_absent}" for r in bad.itertuples()] or ["- none"]
    L += ["", "| tokenizer | token length min / median / max | subject-to-final distance min / median / max |", "|---|---|---|"]
    for k in TOK:
        a, b = V[f"n_tokens_{k}"], V[f"subj_final_dist_{k}"]
        L.append(f"| {k} | {a.min()} / {int(a.median())} / {a.max()} | {b.min()} / {int(b.median())} / {b.max()} |")
    (ROOT / "materials/paraphrases_v1_report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
