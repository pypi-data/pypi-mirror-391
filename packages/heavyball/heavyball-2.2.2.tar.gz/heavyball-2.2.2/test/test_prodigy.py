from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch
import torch.nn.functional as F

import heavyball

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

PRODIGY_ROOT = Path(__file__).resolve().parents[1] / "prodigy"
if PRODIGY_ROOT.exists():
    sys.path.insert(0, str(PRODIGY_ROOT))

try:
    from prodigyopt import Prodigy as ReferenceProdigy
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ReferenceProdigy = None


def _make_model():
    return torch.nn.Sequential(
        torch.nn.Linear(8, 16),
        torch.nn.Tanh(),
        torch.nn.Linear(16, 4),
    ).to(DEVICE)


def _run_step(model: torch.nn.Module, optimizer, data: torch.Tensor, target: torch.Tensor):
    def closure():
        optimizer.zero_grad(set_to_none=True)
        out = model(data)
        loss = F.mse_loss(out, target)
        loss.backward()
        return loss

    optimizer.step(closure)


@pytest.mark.skipif(ReferenceProdigy is None, reason="vendored prodigyopt not available")
def test_foreach_prodigy_matches_reference():
    if ReferenceProdigy is None:  # pragma: no cover - handled by skip above
        pytest.skip("prodigyopt is not available in this environment")

    torch.manual_seed(42)
    model_hb = _make_model()
    model_ref = _make_model()
    model_ref.load_state_dict(model_hb.state_dict())

    opt_hb = heavyball.ForeachProdigy(
        model_hb.parameters(),
        lr=0.75,
        betas=(0.9, 0.999),
        d0=1e-6,
        d_coef=1.5,
        slice_p=3,
        safeguard_warmup=True,
    )
    opt_ref = ReferenceProdigy(
        model_ref.parameters(),
        lr=0.75,
        betas=(0.9, 0.999),
        d0=1e-6,
        d_coef=1.5,
        slice_p=3,
        safeguard_warmup=True,
    )

    for step_seed in range(3):
        torch.manual_seed(1337 + step_seed)
        data = torch.randn(6, 8, device=DEVICE)
        target = torch.randn(6, 4, device=DEVICE)
        _run_step(model_hb, opt_hb, data, target)
        _run_step(model_ref, opt_ref, data.clone(), target.clone())

    for param_hb, param_ref in zip(model_hb.parameters(), model_ref.parameters()):
        torch.testing.assert_close(param_hb, param_ref, atol=1e-6, rtol=1e-5)
