# Dataset release plan and data card (G5 draft; licence table added after GO G4)

## Release plan
| item | plan |
|---|---|
| name (working) | P2 readout-depth curves (anonymous name for review) |
| what | every (fact × paraphrase × carrier × layer) patched curve from the P2 GPU session for all five preregistered models, with facts, paraphrases, carriers, co-occurrence counts and correctness; plus the analysis tables and code to reproduce every P2 number |
| size | about 10.5 MB of parquet for the five runs (`results/P2/*`, 2.0–2.3 MB each) + under 1 MB of materials |
| review link | **anonymized repository on Anonymous GitHub** (anonymous.4open.science; ARR names it as acceptable). It mirrors a fresh repository that holds only the release bundle: no git history, no author names, no ledger lines carrying names, no session links. Data fit within it (≈ 11 MB), so no separate data host is needed. Download-tracking hosts (e.g. Dropbox) are not allowed by ARR and are not used. |
| anonymization pass | strip from the bundle: commit trailers and session URLs, `.claude/`, user e-mail and machine paths (`/home/user/...` → relative), PROGRESS.md and reviewer files (not part of the release); keep run_ids (they carry only stage, model, short hash and UTC time) |
| camera-ready | public repository + a dataset host with a DOI (e.g. Zenodo or the Hugging Face Hub under the authors' organisation), with this card as README |
| licence | code: MIT; own derived data (curves, correctness, frames, carriers): CC BY 4.0; PopQA/LRE facts: MIT (upstream); CounterFact text and infini-gram counts: **not released**, regeneration scripts instead (licence table below) |
| checksums | sha256 of every file in a MANIFEST (the run manifests already exist: `results/P2/*/manifest.json`) |
| when | review bundle built at G6 (freeze, by 2027-01-01) with the anonymized supplementary zip |

## Data card

### Summary
Layer-wise readout curves for 300 English factual associations × 10 designed paraphrases × 3 neutral carriers in five open-weight language models. For each prompt, the residual stream at the prompt's final token, taken at layer l, is patched into the final token of each carrier, and the probability and rank of the object's first token are recorded at the carrier's final position. Collected 2026-11-24 in one preregistered GPU session (prereg/P2_prompt_vs_fact.md, tag prereg-P2 = ff119ca; deviation D-P2-20261124T044034Z-0 concerns only the copy mechanism).

### Composition
| file (per model run) | unit | fields |
|---|---|---|
| `chunks/b*.parquet` | fact × paraphrase (3000 rows) | fact_id, relation, template_id, frame, correct_at1 (top-1 next token = object first token), obj_first_logprob (unpatched), n_prompt_tokens, carrier_alone_logprob_c0..c2 (object first-token log-prob on each carrier alone) |
| `chunks/c*.parquet` | fact × paraphrase × carrier × layer (3000 × 3 × L rows) | fact_id, relation, template_id, carrier, layer (0-based block), p_object (float16), rank |
| `manifest.json`, `meta.json`, `log.jsonl` | run | sha256 of each chunk, model, revision, library versions, materials sha256, run log |

| materials | content |
|---|---|
| `materials/facts_v1.jsonl` | 300 facts: fact_id, relation (20), subject, object, co-occurrence tercile, log1p co-occurrence (PROXY: DCLM-baseline EXACT phrase count via infini-gram), object first token per tokenizer |
| `materials/paraphrases_v1.jsonl` | 200 templates (20 relations × 10 frames); frame metadata: order (subject first / object-slot first), form (cloze / question), length, lexical variant |
| `materials/carriers_v1.jsonl` | 3 carriers: "{} is associated with", "{} is linked to", "A word that goes with {} is" |
| `materials/SAMPLING_RULES_v1.md`, `*_report.md` | sampling rules fixed before sampling; selection and paraphrase-validation reports |

Models (fp32 inference, revision `main` on 2026-11-24; per-run `meta.json`): Qwen/Qwen3-8B, meta-llama/Llama-3.1-8B, EleutherAI/pythia-1.4b, EleutherAI/pythia-2.8b, allenai/OLMo-2-1124-7B. All five runs are complete (5 × 3000 cells, 3 carriers).

### Collection process
- Facts: sampled from the project's fact pool (`data/facts.parquet`, built at S1 from CounterFact, LRE and PopQA true facts; P2's 300 = 278 CounterFact, 13 PopQA, 9 LRE) under the rules in `materials/SAMPLING_RULES_v1.md`: distinct and contentful object first token under every tokenizer, 5 facts per co-occurrence tercile per relation, seed 20261121.
- Paraphrases: 10 designed frames per relation, written and validated before the session (`materials/paraphrases_v1_report.md`).
- Inference: one GPU session (RTX PRO 6000, fp32), scripted driver `scripts/p2_gpu_run.sh`; files verified off-instance (603/603 sha256 matches).

### Intended uses
Studying how readout depth varies with fact, paraphrase and model; reliability (D-study) analyses of layer-wise measures; reproducing the paper's P2 numbers.

### Out-of-scope uses and cautions
- The curves are **final-position readout** under a final-token patch; they say nothing about where a fact is stored or about the subject position.
- `correct_at1` is defined on the object's **first token** only.
- Co-occurrence values are **PROXY** for every model (DCLM-baseline is not any of these models' training corpus).
- Three of five models answered too few facts for the preregistered analysis (MISSING (insufficient data) in the paper); their curves are released but were not analysed confirmatorily.

### People and sensitive content
Subjects include public figures and organisations taken from public knowledge bases (via CounterFact, PopQA, LRE). Facts are public attributes (citizenship, occupation, employer, place of death, ...). No private individuals were targeted and no new personal data was collected. Some facts may be outdated or wrong in the source datasets; the dataset records model behaviour on them, not ground truth.

### Licence check and release decision (checked 2026-11-25 against official sources; decided per the human's rule at GO G4)
Rule (GO G4): release only what is clearly permitted, with the required notices; for anything unclear, release the regeneration scripts instead of the data.

| component | in the release candidate | official source checked | licence / terms found (verbatim where quoted) | decision |
|---|---|---|---|---|
| CounterFact facts (P2: 278 of 300; H-R pool: 4359 of 5200): subject/object text, prompts | facts_v1.jsonl, data/facts.parquet | github.com/kmeng01/rome (README, LICENSE, dsets/counterfact.py); rome.baulab.info and /data/ | Code: "MIT License", Copyright (c) 2022 Kevin Meng. The dataset is not in the repository; `dsets/counterfact.py` downloads it at run time (`REMOTE_URL = f"{REMOTE_ROOT_URL}/data/dsets/counterfact.json"`). No licence or terms on the download pages. Upstream: built on ParaRel ("We use their ParaRel data set as the basis for CounterFact"; ParaRel repo "MIT license"), whose relation data comes from LAMA's T-REx, and LAMA states "LAMA is licensed under the CC-BY-NC 4.0 license". | **UNCLEAR → not released as data.** Release `source_id` (CounterFact case_id) + Wikidata QIDs per fact and a regeneration script that rebuilds subject/object text from the user's own CounterFact download and checks sha256. |
| PopQA facts (P2: 13; H-R pool: 326) | facts_v1.jsonl, data/facts.parquet | github.com/AlexTMallen/adaptive-retrieval (LICENSE; README links data/popQA.tsv in the repo); HF dataset card akariasai/PopQA | Repository LICENSE: "MIT License", "Copyright (c) 2023 Alex Mallen"; the data file is in the same repository. HF card: no licence field visible. | **Permitted (MIT)**, with the MIT copyright notice and licence text in NOTICE. |
| LRE facts (P2: 9; H-R pool: 515) | facts_v1.jsonl, data/facts.parquet | github.com/evandez/relations (LICENSE; data/ folder) | "MIT License", "Copyright (c) 2022 Evan Hernandez"; data/ is inside the repository, no separate data licence. | **Permitted (MIT)**, with notice. |
| Wikidata QIDs and aliases | data/facts.parquet | (Wikidata: CC0 for structured data; not re-checked in this pass) | not re-checked | Released as identifiers only; **to re-check before release**. |
| Paraphrase frames (200) and carriers (3) | materials/paraphrases_v1.jsonl, carriers_v1.jsonl | own work | — | **Released** (CC BY 4.0). Relation frames contain no fact text. |
| Curves from Pythia-1.4b/2.8b, OLMo-2-1124-7B, Qwen3-8B | results/P2/*/chunks (fact_id, relation, template_id, carrier, layer, p_object, rank; correctness) | Hugging Face model pages (licence tags) | All four: `apache-2.0`. Apache-2.0 places no restriction on model outputs. | **Released** (CC BY 4.0) with model citations. |
| Curves from Llama-3.1-8B | results/P2/llama31/* | Llama 3.1 Community License (LICENSE file in the meta-llama/Llama-3.1-8B repository) | "Llama Materials" = "Meta's proprietary Llama 3.1 and Documentation". Outputs are restricted only for use "to create, train, fine tune, or otherwise improve an AI model" (then "Llama" must begin the model name) and by the Acceptable Use Policy. Redistributing Llama Materials requires a copy of the Agreement, "Built with Llama", and the Notice "Llama 3.1 is licensed under the Llama 3.1 Community License, Copyright © Meta Platforms, Inc. All Rights Reserved." | **Released** (layer-wise probabilities/ranks are outputs, not Llama Materials, and are not used to train a model). As a precaution, NOTICE carries the Llama 3.1 notice, the README says "Built with Llama", and a copy of the Agreement is included. Human to confirm. |
| Co-occurrence counts (infini-gram API: DCLM-baseline PROXY for P2; Pile / OLMo-mix EXACT for H-R) | facts_v1.jsonl (log1p_cooc_dclm), counts parquet | infini-gram.io; infini-gram.readthedocs.io API page | No licence, terms of use or redistribution statement on either page ("we offer a free and easy-to-use API endpoint"). The pip package is under a different (academic) software licence, not relevant to API results. | **UNCLEAR → not released as data.** Release the query specification (CNF clauses, windows, index names, `max_clause_freq`) and the client script (`src/depthlaw/freq/`) to regenerate counts; the paper reports only aggregate statistics. |
| Analysis code, R/Python | analysis/, src/, scripts/ | own work | — | **Released** (MIT). |
| H-R depth tables (Pythia, OLMo) | results/S3*, results/HR* | as above (Apache-2.0 models) | — | **Released** with fact text removed for CounterFact rows (IDs only), same as P2. |

Consequence for reproduction: every P2 and H-R number can be rebuilt from released curves + regenerated fact text and counts; the regeneration scripts check sha256 against the hashes in the run manifests. Still open for the human: confirm the Llama reading; re-check Wikidata CC0 before release; consider asking the CounterFact and infini-gram authors for explicit permission (would allow releasing the text and counts at camera-ready).

### Maintenance
Versioned by the materials sha256 in each run's `meta.json`. Errata go to the repository's issue tracker after de-anonymization.
