# P2 paraphrases v1: validation

- **Templates:** 200 (20 relations × 10); sha256 dd481a359860bcb4a8cfec6ed6e85a35904dfcc42b7042a4278d030c1c707548.
- **Prompts checked:** 3000 fact × paraphrase.
- **Subject exactly once:** 3000/3000.
- **Answer string absent:** 3000/3000.

Failing prompts (excluded from P2 at analysis time):

- none

| tokenizer | token length min / median / max | subject-to-final distance min / median / max |
|---|---|---|
| llama31 | 5 / 14 / 27 | 1 / 4 / 10 |
| qwen3 | 4 / 13 / 26 | 1 / 4 / 10 |
| pythia | 4 / 13 / 27 | 1 / 5 / 11 |
| olmo2 | 4 / 13 / 26 | 1 / 4 / 10 |
