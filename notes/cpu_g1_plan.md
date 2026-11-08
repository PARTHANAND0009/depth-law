# CPU G1 plan (2026-11-08, written before any gate-model depth data)
Human approval: "OK CPU G1" (2026-11-08). No prereg threshold changed.
- Models: pythia-1.4b, pythia-2.8b on CPU (fp32). olmo-2-1124-7b: MISSING (does not fit 15.7 GB RAM).
  With OLMo missing, GO needs both Pythia models to PASS (min_models_passing = 2).
- Facts: data/facts_g1cpu.parquet = data/splits/g1_cpu_subsample.json
  (facts.groupby('relation').sample(50, random_state=1234); 1,300 facts, 26 relations), 3 templates.
  Override partner B is drawn from this subsample (run_depth.partners, seed 1234).
- Rule 4: tests on pythia-70m run before pythia-2.8b (results/S3/tests_pythia70m_before_2.8b_junit.xml).
- Predictor: exact phrase counts (data/counts_exact.parquet, S2x chain); Pile index (EXACT) for Pythia.
- Chain: scripts/run_g1_cpu.sh, log results/g1_cpu.out. Writes reports/GATE_G1.md, then STOP.
