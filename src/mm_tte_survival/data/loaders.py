"""Modality loaders. Returns the raw per-patient tables for the run."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class RawModalities:
    clinical: pd.DataFrame
    cytogenetics: pd.DataFrame | None
    omics: pd.DataFrame | None
    program_activity: pd.DataFrame | None
    provenance: pd.DataFrame | None


def _read(path: str | None) -> pd.DataFrame | None:
    if path and Path(path).exists():
        df = pd.read_csv(path)
        if "patient_id" in df.columns:
            df["patient_id"] = df["patient_id"].astype(str)
        return df
    return None


def load_modalities(clinical_path: str, cytogenetics_path: str | None = None,
                    omics_path: str | None = None,
                    program_activity_path: str | None = None) -> RawModalities:
    clinical = _read(clinical_path)
    if clinical is None:
        raise FileNotFoundError(f"clinical table not found: {clinical_path}")
    prov_path = Path(clinical_path).parent / "cytogenetics_provenance.csv"
    return RawModalities(
        clinical=clinical,
        cytogenetics=_read(cytogenetics_path),
        omics=_read(omics_path),
        program_activity=_read(program_activity_path),
        provenance=_read(str(prov_path)),
    )
