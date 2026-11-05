# Environment (S0)

- Python 3.13.18, Linux-6.18.44-fc-v236-x86_64-with-glibc2.39
- CPU-only (tier CPU, see reports/hw.json); torch CPU wheel from download.pytorch.org/whl/cpu

| package | version |
|---|---|
| torch | 2.15.0+cpu |
| transformers | 5.22.1 |
| nnsight | 0.8.2 |
| tuned-lens | 0.2.0 |
| datasets | 5.1.0 |
| numpy | 2.5.4 |
| pandas | 3.1.1 |
| statsmodels | 0.15.0 |
| scipy | 1.18.1 |
| pyarrow | 26.0.1 |
| safetensors | 0.8.0 |
| huggingface_hub | 2.4.0 |
| requests | 2.34.2 |
| pytest | 9.2.0 |

## API checks done against installed source (not memory)
- tuned-lens 0.2.0: `TunedLens.from_model_and_pretrained(model, lens_resource_id=None, **kwargs)`; kwargs go to `torch.load`, so `map_location` must be passed on CPU (tuned_lens/nn/lenses.py:206-277). `TunedLens.forward(h, idx)`.
- tuned-lens pretrained lenses (HF Space AlignmentResearch/tuned-lens, listed 2026-11-05): Pythia only as *-deduped (70m..12b); no lenses for non-deduped Pythia, OLMo-2, Llama-3.1, Qwen3, Gemma-3. Meta-Llama-3-8B (not 3.1) exists. Core-model lenses must be trained (GPU).
- nnsight 0.8.2: tracing API differs from older docs; depth code uses raw HF forward hooks (CLAUDE.md fallback) in src/depthlaw/depth/common.py.
- transformers 5.22.1: `from_pretrained(..., dtype=...)` (not torch_dtype).
- infini-gram API: max 4 OR-terms per clause (error text: 'Please enter at most 4 terms in each disjunctive clause!'); AWS API Gateway throttling (HTTP 429/403) at >~3 q/s from this host; effective sustained rate ~2.5 q/s.
- Wikidata: REST API (wbsearchentities) rate-limited from this host; SPARQL endpoint works.
- Gated tokenizers (Llama-3.1, Gemma-3) download OK with the injected HF token.
