"""S6 corpus: download a FineWeb-Edu prefix, train a small byte-level BPE tokenizer on it (a small
vocabulary keeps the unembedding cheap on CPU), and tokenize the corpus to a uint16 array.

  python -m depthlaw.pretrain.corpus download --tokens 70000000
  python -m depthlaw.pretrain.corpus tokenizer
  python -m depthlaw.pretrain.corpus encode

Files under data/s6/corpus/: docs.jsonl, meta.json, corpus.bin (uint16), and data/s6/tokenizer/.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import yaml

from depthlaw.io import ROOT

D = ROOT / "data" / "s6"
C = D / "corpus"
EOS = "<|endoftext|>"


def download(tokens: int) -> None:
    from datasets import load_dataset
    cfg = yaml.safe_load(open(ROOT / "configs" / "s6.yaml"))["corpus"]
    C.mkdir(parents=True, exist_ok=True)
    ds = load_dataset(cfg["path"], name=cfg["name"], split=cfg["split"], streaming=True)
    n_tok = n_doc = 0
    with open(C / "docs.jsonl", "w") as f:
        for x in ds:
            f.write(json.dumps({"id": x["id"], "text": x["text"]}) + "\n")
            n_tok += int(x["token_count"])
            n_doc += 1
            if n_tok >= tokens:
                break
    (C / "meta.json").write_text(json.dumps({**cfg, "n_docs": n_doc, "gpt2_token_count": n_tok,
                                            "rule": "first documents of the stream until the gpt2 token_count sum reaches the target"}, indent=1))
    print(n_doc, n_tok)


def docs():
    with open(C / "docs.jsonl") as f:
        for line in f:
            yield json.loads(line)["text"]


def tokenizer(vocab: int, train_docs: int) -> None:
    from tokenizers import ByteLevelBPETokenizer
    from transformers import PreTrainedTokenizerFast

    def it():
        for i, t in enumerate(docs()):
            if i >= train_docs:
                break
            yield t

    bpe = ByteLevelBPETokenizer()
    bpe.train_from_iterator(it(), vocab_size=vocab, min_frequency=2, special_tokens=[EOS])
    tk = PreTrainedTokenizerFast(tokenizer_object=bpe, eos_token=EOS, bos_token=EOS, unk_token=EOS, pad_token=EOS)
    tk.save_pretrained(D / "tokenizer")
    print(len(tk))


def encode(batch: int = 1000) -> None:
    from transformers import AutoTokenizer
    tk = AutoTokenizer.from_pretrained(D / "tokenizer")
    eos = tk.eos_token_id
    out, buf = [], []
    for t in docs():
        buf.append(t)
        if len(buf) == batch:
            for ids in tk(buf, add_special_tokens=False).input_ids:
                out.append(np.asarray(ids + [eos], dtype=np.uint16))
            buf = []
    if buf:
        for ids in tk(buf, add_special_tokens=False).input_ids:
            out.append(np.asarray(ids + [eos], dtype=np.uint16))
    arr = np.concatenate(out)
    arr.tofile(C / "corpus.bin")
    m = json.loads((C / "meta.json").read_text())
    m.update({"n_tokens_own_tokenizer": int(len(arr)), "vocab": len(tk)})
    (C / "meta.json").write_text(json.dumps(m, indent=1))
    print(len(arr))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["download", "tokenizer", "encode"])
    ap.add_argument("--tokens", type=int, default=70_000_000)
    ap.add_argument("--vocab", type=int, default=8192)
    ap.add_argument("--train-docs", type=int, default=30000)
    a = ap.parse_args()
    {"download": lambda: download(a.tokens), "tokenizer": lambda: tokenizer(a.vocab, a.train_docs),
     "encode": encode}[a.cmd]()


if __name__ == "__main__":
    main()
