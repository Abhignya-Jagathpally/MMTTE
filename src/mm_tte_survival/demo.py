from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def make_demo_data(outdir: str | Path = "data/demo", n: int = 260, p: int = 120, seed: int = 42) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    ids = np.array([f"MM_{i:04d}" for i in range(n)])
    age = rng.normal(65, 9, n).clip(35, 90)
    sex_M = rng.binomial(1, 0.55, n)
    iss = rng.choice([1, 2, 3], size=n, p=[0.38, 0.34, 0.28])
    riss = np.clip(iss + rng.choice([0, 1], n, p=[0.75, 0.25]), 1, 3)
    line = rng.choice([1, 2, 3], size=n, p=[0.65, 0.25, 0.10])
    cyto = pd.DataFrame({
        "patient_id": ids,
        "amp1q": rng.binomial(1, 0.35, n),
        "del1p": rng.binomial(1, 0.14, n),
        "del13q": rng.binomial(1, 0.42, n),
        "del17p": rng.binomial(1, 0.11, n),
        "t_4_14": rng.binomial(1, 0.14, n),
        "t_11_14": rng.binomial(1, 0.16, n),
        "hyperdiploid": rng.binomial(1, 0.45, n),
    })
    X = rng.normal(0, 1, (n, p))
    # Inject subtype and clinical signal into first features.
    X[:, 0] += cyto["amp1q"].to_numpy() * 1.0 + cyto["del17p"].to_numpy() * 1.3
    X[:, 1] += cyto["t_4_14"].to_numpy() * 1.2 - cyto["hyperdiploid"].to_numpy() * 0.5
    X[:, 2] += cyto["del1p"].to_numpy() * 0.8
    risk = (
        0.025 * (age - 65) + 0.22 * (iss == 3) + 0.18 * (riss == 3) + 0.18 * (line - 1)
        + 0.55 * cyto["del17p"].to_numpy() + 0.38 * cyto["amp1q"].to_numpy()
        + 0.30 * cyto["t_4_14"].to_numpy() + 0.18 * cyto["del1p"].to_numpy()
        - 0.25 * cyto["hyperdiploid"].to_numpy() + 0.12 * X[:, 0] + 0.08 * X[:, 1]
    )
    base_scale = 42.0
    event_time = rng.weibull(1.35, n) * base_scale * np.exp(-risk)
    censor_time = rng.uniform(12, 72, n)
    observed = (event_time <= censor_time).astype(int)
    time = np.minimum(event_time, censor_time).clip(1.0, None)
    h = np.array([int(__import__("hashlib").sha256(f"{seed}:{x}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF for x in ids])
    split = np.where(h < 0.70, "train", np.where(h < 0.85, "val", "test"))
    clinical = pd.DataFrame({
        "patient_id": ids, "time_months": time.round(2), "event": observed,
        "age": age.round(1), "sex_M": sex_M, "iss_2": (iss == 2).astype(int), "iss_3": (iss == 3).astype(int),
        "riss_2": (riss == 2).astype(int), "riss_3": (riss == 3).astype(int), "line_of_therapy": line,
        "split": split,
    })
    omics = pd.DataFrame(X, columns=[f"gene_{i:04d}" for i in range(p)])
    omics.insert(0, "patient_id", ids)
    clinical.to_csv(out / "clinical.csv", index=False)
    cyto.to_csv(out / "cytogenetics.csv", index=False)
    omics.to_csv(out / "omics.csv", index=False)
    (out / "README.md").write_text(
        "# Demo MM TTE data\n\nSynthetic, non-clinical demo data for smoke-testing the code path. Replace with CoMMpass/MMRF VLab or institutional data before scientific use.\n",
        encoding="utf-8",
    )
