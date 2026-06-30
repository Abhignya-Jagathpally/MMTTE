"""Patient-disjoint splitting."""
from __future__ import annotations

import hashlib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def hash_split(patient_id: str, seed: int = 42) -> str:
    """Deterministic train/val/test by hashing the patient id."""
    h = hashlib.sha256(f"{seed}:{patient_id}".encode()).hexdigest()
    v = int(h[:8], 16) / 0xFFFFFFFF
    if v < 0.70:
        return "train"
    if v < 0.85:
        return "val"
    return "test"


def stratified_event_split(df: pd.DataFrame, event_col: str, seed: int,
                           test_frac: float = 0.25) -> pd.Series:
    """Stratify the train/test split on the event indicator (boolean train mask)."""
    idx = np.arange(len(df))
    tr, te = train_test_split(idx, test_size=test_frac, random_state=seed,
                              stratify=df[event_col].astype(int).values)
    split = np.array(["train"] * len(df), dtype=object)
    split[te] = "test"
    return pd.Series(split == "train")
