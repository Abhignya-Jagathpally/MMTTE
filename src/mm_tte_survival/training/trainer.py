"""Trainer for the abstract MultiHeadSurvivalModel (optional neural path).

The default production model is ResidualRiskModel (see models/residual_risk.py);
this trains the parallel neural encoder + Cox head when a run explicitly enables
it. Kept deliberately small — the legacy per-model trainer in trainer_legacy.py
is used by `run-experiments`.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import torch

from ..models.neural_survival import MultiHeadSurvivalModel
from .losses import cox_ph_loss
from .distillation import DistillationPolicy


@dataclass
class FittedNeuralModel:
    model: MultiHeadSurvivalModel
    feature_names: list[str]
    history: list[float]


def train_survival_model(X_train, t_train, e_train, model: MultiHeadSurvivalModel,
                         feature_names, epochs=100, lr=1e-3, weight_decay=1e-4,
                         distillation: DistillationPolicy | None = None) -> FittedNeuralModel:
    Xt = torch.tensor(np.asarray(X_train), dtype=torch.float32)
    tt = torch.tensor(np.asarray(t_train), dtype=torch.float32)
    et = torch.tensor(np.asarray(e_train), dtype=torch.float32)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    history = []
    model.train()
    for _ in range(epochs):
        opt.zero_grad()
        out = model(Xt)
        loss = cox_ph_loss(out["cox"].squeeze(-1), tt, et)
        loss.backward()
        opt.step()
        history.append(float(loss.item()))
    return FittedNeuralModel(model=model, feature_names=list(feature_names), history=history)
