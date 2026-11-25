# Candidate titles and abstract (G4 setup; not paper text until GO G4)

Numbers appear as `paper/numbers.tex` macros; the rendered value is in brackets for review only.

## Titles
1. **How Much of a Fact's Readout Depth Belongs to the Fact? Two Preregistered Studies**
2. **Fact or Phrasing? A Preregistered Variance Decomposition of Where Language Models Read Out Answers**
3. **One Fact, Many Depths: Paraphrase Sensitivity of Causal Readout Depth in Language Models**

## Abstract (150 words)
At which layer does a language model's answer to a factual prompt become readable, and is that depth a property of the fact or of the prompt? We measure readout depth by patching a prompt's final hidden state into neutral carrier prompts, and report two preregistered studies. In three models from two families with exact pretraining counts, within-relation subject–object co-occurrence added at most `\hrDRsqOlmoSeven` [0.0016] explained variance (every upper bound below the preregistered 0.02), and relation identity explained at most `\hrIccOlmoSeven` [0.060]. In Llama-3.1-8B and OLMo-2-7B, with 300 facts × 10 designed paraphrases, the fact share is above zero; it was estimated at 0.28–0.42 [`\ptIccDFourLlama`–`\ptIccDOneOlmo`] of within-relation variance, and paraphrase-related variance at 0.55–0.68 [`\ptWordingDOneOlmo`–`\ptWordingDFourLlama`], but wording exceeded the fact share in only one model. A decision study estimates 4–8 [`\ptNprimeOlmo`–`\ptNprimeLlama`] paraphrases for a reliable per-fact depth. We also show that rank-based causal depth exists only for correctly answered prompts.

## Sentence-by-sentence licensing
| sentence | basis | status |
|---|---|---|
| question + method | design description (P2 prereg section 1; HR B1) | description |
| co-occurrence ≤ 0.0016, upper bounds < 0.02 | HR H3 PASS in 3/3 | CONFIRMATORY (not blind; disclosed in paper) |
| relation identity ≤ 0.060 | HR H1 FAIL; CI uppers < 0.15 | CONFIRMATORY |
| "the fact share is above zero" | P2 section 6, licensed in 2/2 families | CONFIRMATORY, licensed |
| 0.28–0.42 fact share, 0.55–0.68 wording share | P2 estimates (intermediate result, section 6) | CONFIRMATORY estimates; no sentence licensed by them |
| "wording exceeded the fact share in only one model" | H1 met in Llama, not OLMo | CONFIRMATORY (per-model result, no claim) |
| 4–8 paraphrases | P2 H2 n′ (estimation only) | CONFIRMATORY estimate; "estimates" wording, not "needs" |
| rank-based depth exists only for correct prompts | derivation + audit | EXPLORATORY audit (labelled in the paper body; the abstract states the derivation) |

Not in the abstract (not licensed or not complete): "prompt wording matters more than the fact", "it takes N paraphrases", "facts have their own depth", "frequency does not matter", S5 dynamics.
