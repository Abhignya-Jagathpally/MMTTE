# Comparator registry (categorised — not every model solves the same task)

The benchmark does not pretend all comparators share a task or endpoint.
Comparators are grouped by what they actually are.

## A. Same-cohort direct OS comparators (runnable here, OS endpoint)
| Comparator | Runnable | Endpoint | Interpretation |
|---|---|---|---|
| Clinical Cox | Yes | OS | Required baseline |
| Clinical+cytogenetics | Yes | OS | Full clinical+FISH/CNV |
| Clinical+omics | Yes | OS | **Current strongest Experiment 0 model** |
| Clinical+cytogenetics+omics | Yes | OS | Full matched feature model |
| Residual-risk (clinical+molecular) | Yes | OS | Proposed interpretable decomposition |

## B. Public-weight off-endpoint biological comparators (runnable, native ≠ OS)
| Comparator | Runnable | Endpoint | Interpretation |
|---|---|---|---|
| mmSYGNAL agnostic | Yes | relapse/PFS model tested on OS | Off-endpoint transfer check (OS C≈0.62) |
| mmSYGNAL selected subtype | Yes | relapse/PFS model tested on OS | Off-endpoint subtype benchmark (OS C≈0.59) |

## C. Literature-only OS comparators (not reproduced; cite, do not fabricate)
| Comparator | Runnable | Endpoint | Interpretation |
|---|---|---|---|
| MyeVAE | Literature/reproducibility | OS/PFS | Reported multi-omics VAE comparator; no open weights → not scored here |
| ISS / R-ISS staging | Literature | OS | Standard clinical staging reference (R-ISS needs LDH ULN + FISH) |

## D. Literature-only progression/PFS comparators (endpoint-different)
| Comparator | Runnable | Endpoint | Interpretation |
|---|---|---|---|
| Ferle progression model | Literature | Progression | Not comparable until a longitudinal progression endpoint exists |
| UAMS GEP70 / SKY92 | Literature | PFS/OS (microarray) | Panel signatures; endpoint/platform-different |

## E. Future endpoint-correct validation comparators (pending controlled access)
| Comparator | Runnable | Endpoint | Interpretation |
|---|---|---|---|
| Controlled CoMMpass PFS | Pending | PFS/relapse | **Required for the main biological claim** |
| TTNT / early-progression (24 mo) | Pending | proxy/landmark | Secondary endpoint-correct checks |

## Framing rule
Off-endpoint comparators (B, D) are never ranked against OS C-index without the
off-endpoint warning. The main biological question (molecular residual risk vs
progression/relapse) is only answerable under category E.
