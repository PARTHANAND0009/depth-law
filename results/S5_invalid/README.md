# INVALID: pythia-2.8b S5 runs that loaded the main weights

Do not use these runs. Found 2026-11-19.

- **What happened:** these four runs evaluated the final model, not the named checkpoint.
- **Cause:** the Hub branches `EleutherAI/pythia-2.8b@step*` carry a stale single-file `model.safetensors` (and `pytorch_model.bin`) whose sha256 equals main's (`ab496f1c3fd7...`), next to the real sharded checkpoint `model-0000{1,2}-of-00002.safetensors` (different sha256 per step). transformers prefers the single file.
- **Evidence:** step1000, step2000 and step4000 give identical results. Each has N=1524 rows, correct@1 0.5276 and mean obj_first_logprob -2.7473 (read from each `depth.parquet`).
- **Fix:** `src/depthlaw/depth/common.resolve_weights` loads only the shards for non-main revisions and refuses any weight file whose sha256 equals main's. `weights_shard*.json` records the hashes in every run dir. Test: `tests/test_revisions.py`.
- **pythia-1.4b:** S5 runs are unaffected. Its branches have no single-file safetensors, and its results differ across steps (correct@1 0.000 at step1000 to 0.469 at step128000).
