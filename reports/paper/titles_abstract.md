# Candidate titles and abstract (G4 setup, revised after the G4 reviews; not paper text until GO G4)

Numbers appear as `paper/numbers.tex` macros; the rendered value is in brackets for review only. Reviews: `reports/gates/G4/{claim-auditor,novelty-scout}.md`; responses: `reports/gates/G4/responses.md`. The first version is in git (`21692bb`).

## Titles
1. **How Much of Answer-Readout Depth Is Fact-Level? Two Preregistered Studies**
2. **Paraphrase Sensitivity of Final-Position Readout Depth: A Preregistered Variance Decomposition in Two Model Families**
3. **One Fact, Many Readout Depths: Preregistered Evidence from Two Model Families**

Recommendation: title 1 (states the question, not an answer; both reviewers found the original titles 2 and 3 over-reached).

## Abstract (≈ 150 words)
At which layer does a language model's answer to a factual prompt become readable at the prediction position, and how much of that depth is fact-level? We patch a prompt's final hidden state, layer by layer, into neutral carrier prompts and report two preregistered studies. In three models from two families with exact pretraining counts, within-relation subject–object co-occurrence added little explained variance (point estimates ≤ `\hrDRsqMax` [0.0016]; all upper 95% bounds below the preregistered 0.02), and the relation-level share was small (≤ `\hrIccMax` [0.060]; upper bounds ≤ `\hrIccHiMax` [0.123]). In a separate study of Llama-3.1-8B and OLMo-2-7B, on the prompts each model answers correctly, the fact share is above zero. Estimated fact-level shares, which include answer-token identity, were `\ptIccRangeLo`–`\ptIccRangeHi` [0.28–0.42] of within-relation variance; paraphrase-related shares were `\ptWordingRangeLo`–`\ptWordingRangeHi` [0.55–0.68], exceeding the fact share by the preregistered test in one model. A decision study estimates `\ptNprimeOlmo` [4] (OLMo) and `\ptNprimeLlama` [8] (Llama) paraphrases for a generalizability coefficient of 0.8.

## Sentence-by-sentence licensing
| sentence | basis | status |
|---|---|---|
| question + method | design (P2 prereg section 1; HR B1); "at the prediction position" scopes it to final-position readout | description |
| co-occurrence: point ≤ 0.0016, upper bounds < 0.02 | HR H3 PASS in 3/3; marginal R² (Nakagawa), within-relation (relation-centred) counts | CONFIRMATORY; not blind (disclosed in the body, with the survival-model association) |
| relation-level share ≤ 0.060, upper ≤ 0.123 | HR H1 (covariate-adjusted ICC_rel) FAILED in 3/3; upper bounds descriptive | CONFIRMATORY (failed positive test, not a confirmed null); H2 raw (orderings ρ ≈ 0.5–0.6, below 0.7) in the body |
| "in a separate study ... on the prompts each model answers correctly" | P2 is a different design; correct cells only; the three other preregistered models are MISSING (body) | scope |
| "the fact share is above zero" | P2 section 6, licensed in 2/2 families (GO G2) | CONFIRMATORY, licensed, verbatim |
| fact-level shares 0.28–0.42 "which include answer-token identity" | P2 ICC(1) D1/D4 estimates (intermediate result) | CONFIRMATORY estimates; no sentence licensed by them |
| paraphrase-related 0.55–0.68; "exceeding the fact share by the preregistered test in one model" | P2 wording share estimates; H1 met in Llama, not OLMo; family-level not licensed | CONFIRMATORY estimates + per-model result |
| n′ 4 and 8 for G = 0.8 | P2 H2 (estimation only) | CONFIRMATORY estimate; "estimates", not "needs" |

Removed from the abstract: the rank-1 correctness-conditioning note (EXPLORATORY audit; stays in section 3 of the paper, scoped to final-token patching), "reliable per-fact depth", and any comparison of H-R and P2 numbers.
Not in the abstract (not licensed or not complete): "prompt wording matters more than the fact", "it takes N paraphrases", "facts have their own depth", "frequency does not matter", "where a fact is stored", S5 dynamics.
