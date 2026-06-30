# PFS / relapse data acquisition plan

**Open GDC OS is not enough for primary relapse/PFS claims.** The GDC open
clinical export carries vital status and survival time but NOT progression or
relapse dates. To make an endpoint-correct progression/relapse claim, controlled
**MMRF CoMMpass (Researcher Gateway / dbGaP)** or equivalent institutional data is
required.

## Fields needed to define a PFS / relapse endpoint
- `patient_id`
- diagnosis date or baseline (treatment-start) date
- progression date(s)
- relapse date(s), if recorded separately
- death date
- last follow-up date
- treatment start/end dates (per line)
- line of therapy
- censoring status
- explicit event definition (PFS vs TTP vs TTNT vs early-progression landmark)

## Endpoint definitions to support
| Endpoint | Event | Registry key | Primary claim |
|---|---|---|---|
| Overall survival | death | `open_gdc_os` | no (technical validation) |
| Progression-free survival | progression or death | `controlled_commpass_pfs` | yes |
| Time to next treatment | next-line start | `time_to_next_treatment` | conditional (proxy) |
| Early progression (24 mo) | progression ≤24 mo landmark | `early_progression_24m` | conditional |

## Acquisition checklist
- [ ] Apply for MMRF Researcher Gateway / dbGaP controlled access (PFS, treatment lines).
- [ ] Confirm progression-date provenance and censoring rules.
- [ ] Re-derive the survival table with `pfs_time` / `pfs_event` populated.
- [ ] Set `endpoint.name: controlled_commpass_pfs` in the run config.
- [ ] Wire a second cohort for external validation; set
      `validation.external_validation_available: true` only then.
- [ ] Re-run `residual-report`; the claim gates open only when endpoint type and
      external validation justify a primary biological claim.

**Rule enforced in code:** the pipeline refuses to emit relapse/PFS language when
the active endpoint type is overall survival.
