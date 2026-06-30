import torch
from mm_tte_survival.training.losses import cox_ph_loss, lognormal_aft_loss, first_hitting_time_loss
from mm_tte_survival.metrics import harrell_c_index


def test_cindex_perfect_ordering():
    time = [1, 2, 3, 4]
    event = [1, 1, 1, 0]
    risk = [4, 3, 2, 1]
    assert harrell_c_index(time, event, risk) == 1.0


def test_losses_are_finite():
    time = torch.tensor([5.0, 10.0, 20.0, 25.0])
    event = torch.tensor([1.0, 0.0, 1.0, 0.0])
    risk = torch.tensor([0.5, 0.2, -0.1, -0.4])
    params = torch.tensor([[2.0, 0.2], [2.4, 0.3], [3.0, 0.4], [3.2, 0.5]])
    assert torch.isfinite(cox_ph_loss(risk, time, event))
    assert torch.isfinite(lognormal_aft_loss(params, time, event))
    assert torch.isfinite(first_hitting_time_loss(params, time, event))
