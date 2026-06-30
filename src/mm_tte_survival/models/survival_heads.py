"""Survival heads operating on the shared latent z: Cox / AFT / FHT."""
from __future__ import annotations

import torch
import torch.nn as nn


class CoxHead(nn.Module):
    """Single risk score (log partial hazard)."""
    def __init__(self, latent_dim: int):
        super().__init__()
        self.fc = nn.Linear(latent_dim, 1)

    def forward(self, z):
        return self.fc(z)  # (N,1)


class AFTHead(nn.Module):
    """Log-normal AFT: outputs (mu, log_sigma)."""
    def __init__(self, latent_dim: int):
        super().__init__()
        self.fc = nn.Linear(latent_dim, 2)

    def forward(self, z):
        return self.fc(z)  # (N,2)


class FHTHead(nn.Module):
    """Inverse-Gaussian first-hitting-time: outputs (log_drift, log_barrier)."""
    def __init__(self, latent_dim: int):
        super().__init__()
        self.fc = nn.Linear(latent_dim, 2)

    def forward(self, z):
        return self.fc(z)  # (N,2)


_HEADS = {"cox": CoxHead, "aft": AFTHead, "fht": FHTHead}


def build_survival_heads(latent_dim: int, heads=("cox", "aft", "fht")) -> nn.ModuleDict:
    return nn.ModuleDict({h: _HEADS[h](latent_dim) for h in heads if h in _HEADS})
