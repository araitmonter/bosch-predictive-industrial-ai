# Quality SLA

## Data Freshness

Source data for scoring should be available before the inspection decision point. Batch scoring windows and latency targets must be agreed with quality operations.

## Missingness Thresholds

- Green: missingness within baseline plus 5 percentage points.
- Amber: missingness exceeds baseline by 5 to 10 percentage points.
- Red: missingness exceeds baseline by more than 10 percentage points or affects required keys.

## Drift Monitoring

Monitor prediction drift and feature-level PSI. Amber PSI begins at 0.10. Red PSI begins at 0.25. Red drift requires review before threshold expansion.

## Model Performance Review Cadence

Review performance weekly during pilot operation and monthly after stabilization. False-negative monitoring depends on delayed labels from the quality process.

## Dashboard Availability

Pilot dashboard availability should align with quality review cadence. It is not a real-time production control system unless separately hardened and approved.

## Ownership

- Business owner: quality manager.
- Operational owner: manufacturing lead.
- Technical owner: AI lead.
- Data owner: data engineering lead.
- Governance owner: CDO / CAIO or delegated AI governance lead.

