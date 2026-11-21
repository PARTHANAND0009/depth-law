# GPU environment (2026-11-21)

| item | value |
|---|---|
| GPU | NVIDIA RTX PRO 6000 Blackwell, 97887 MiB, driver 595.91.07 (nvidia-smi CUDA 13.2) |
| compute capability | (12, 0) |
| torch | 2.15.0+cu132 (pinned version from requirements-gpu.txt; default PyPI wheel) |
| torch.version.cuda | 13.2 |
| torch arch list | sm_75 sm_80 sm_86 sm_90 sm_100 sm_120 |
| fp32 matmul 2048x2048 on cuda vs CPU fp64 | max abs err 1.6e-4, rel 6.8e-7 (TF32 off) |
| python | 3.12.3, .venv from requirements-gpu.txt |

The pinned torch supports sm_120; no replacement build was installed.
Setup notes: python3.12-venv was installed with apt (venv module missing on the VM image).
GPU check completed 06:10 UTC (session start 06:08 UTC).
