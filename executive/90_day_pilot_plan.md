# 90-Day Pilot Plan

| Phase | Weeks | Objective | Output |
|---|---:|---|---|
| Data validation | 1-2 | Validate source data, missingness, leakage risk, and feature reliability | Data readiness sign-off |
| Offline validation | 3-5 | Evaluate model performance on historical data and define candidate thresholds | Model validation report |
| Shadow mode | 6-8 | Run predictions without influencing production decisions | Drift, threshold, and operational impact report |
| Controlled pilot | 9-12 | Use risk bands to support inspection prioritization under human supervision | Executive pilot decision report |

## Success Criteria

- Data quality gates operate reliably across source files and feature families.
- Offline validation meets agreed minimum recall and false-negative tolerances.
- Shadow-mode predictions remain stable enough for controlled workflow testing.
- Quality teams confirm that risk bands are understandable and operationally usable.
- Inspection workload remains within approved capacity limits.

## Governance Controls

- Human review for high and critical risk decisions.
- Weekly threshold and drift review.
- Documented override process.
- Model version tracking for all pilot scores.
- Rollback procedure if monitoring thresholds are breached.

## Required Stakeholders

- COO or manufacturing operations lead.
- Chief Quality Officer or quality director.
- CDO / CAIO.
- AI lead.
- Data engineering lead.
- Data steward.
- Quality manager.
- Risk or compliance representative.
- Product owner for the pilot workflow.

## Go / No-Go Criteria

Proceed only if event-time validation, feature availability, inspection capacity, and governance ownership are confirmed. Stop or extend shadow mode if false negatives exceed risk tolerance, drift is material, or quality teams cannot act on the risk bands with confidence.

