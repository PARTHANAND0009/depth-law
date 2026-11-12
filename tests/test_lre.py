import torch

from depthlaw.depth.common import _out_tensor, load_lm
from depthlaw.depth.lre import jacobian, states


def test_lre_jacobian_matches_finite_difference():
    lm = load_lm("EleutherAI/pythia-70m", dtype=torch.float64)
    for p in lm.model.parameters():
        p.requires_grad_(False)
    layer = lm.n_layers // 3 - 1
    ids, sp, s, o, _ = states(lm, "The capital of {} is", "France", layer)
    J = jacobian(lm, ids, sp, layer, s)
    v = torch.randn(s.shape, dtype=s.dtype, generator=torch.Generator().manual_seed(0))

    def o_of(x):
        st = {}
        def h1(m, i, out):
            _out_tensor(out)[0, sp] = x
            return out
        a = lm.layers[layer].register_forward_hook(h1)
        b = lm.layers[-1].register_forward_hook(lambda m, i, out: st.__setitem__("o", _out_tensor(out)[0, -1].clone()))
        with torch.no_grad():
            lm.model(ids)
        a.remove(); b.remove()
        return st["o"]

    eps = 1e-5
    fd = (o_of(s + eps * v) - o_of(s - eps * v)) / (2 * eps)
    assert float((fd - J @ v).norm() / fd.norm()) < 1e-4
    assert torch.allclose(o_of(s), o)
