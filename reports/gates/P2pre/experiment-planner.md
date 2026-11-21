<!-- experiment-planner subagent (.claude/agents/experiment-planner.md), fresh context, 2026-11-21, P2 A6 run manifest. Saved verbatim by the main session; not edited. The YAML block is also saved as run_manifest.yaml (repo root). -->
I could not write the file, so the content of `run_manifest.yaml` for the P2 GPU session is below.

Three things block renting the GPU. They are listed under `preconditions_before_renting` in the YAML:
- The P2 preregistration is still only a staged draft.
- The bootstrap simulation that the prereg needs to choose its CI method has not finished. There is no `results/P2sim/p2_bootsim.json`, only an `.out` file full of singular-fit warnings.
- No session driver script for P2 exists yet.

**Budget:** floor(240/207.36×60) − 15 = 54 minutes.
- Qwen3-8B plus Llama-3.1-8B with 3 carriers is estimated at 47.3 minutes. That fits, but the upper estimate is 58.3 minutes, which does not.
- The YAML therefore applies the fallback order between models, using Qwen's measured speed. Qwen's 3-carrier data already contains the 2-carrier subset, so the two models stay comparable if Llama drops to 2 carriers.
- If Llama has to be dropped, every claim that needs at least 2 models depends on Pythia. Under the 1.8 GB CPU cap, Pythia cannot run on the CPU here.

**Top-up:** INR 500 alone buys 144 minutes. With it the budget becomes 199 minutes. All five models in one session cost about 80 to 95 minutes (INR 278 to 329).

(YAML: identical to /home/user/depth-law/run_manifest.yaml below the three header comment lines.)

The top-up is the human's call. Without it, P2-A is the fallback, but it risks ending with only one GPU model, which would then need a second paid session.

Files:
- /home/user/depth-law/reports/pending_frozen_changes/P2_prompt_vs_fact.md
- /home/user/depth-law/src/depthlaw/p2/run_p2.py
- /home/user/depth-law/src/depthlaw/depth/causal.py
- /home/user/depth-law/results/S3b/S3b-OLMo-2-1124-7B-923945f-20261121T061237Z/log.jsonl
- /home/user/depth-law/results/S3b/S3b-pythia-1.4b-a7dfeb5-20261121T063528Z/log.jsonl
- /home/user/depth-law/results/S3b/S3b-pythia-2.8b-a7dfeb5-20261121T064110Z/log.jsonl
- /home/user/depth-law/results/S3bsmoke/S3bsmoke-pythia-70m-923945f-20261121T061039Z/log.jsonl
- /home/user/depth-law/reports/env_gpu.md
- /home/user/depth-law/reports/GATE_A2.md
- /home/user/depth-law/cache/hf/local/EleutherAI--pythia-2.8b--step32000/config.json
- /home/user/depth-law/results/P2sim/p2_bootsim.out
- /home/user/depth-law/reports/gates/G1/experiment-planner.md
- /home/user/depth-law/PROGRESS.md

RECOMMEND: P2-B
