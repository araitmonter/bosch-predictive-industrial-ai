# Threshold Policy

## Purpose

Define how model decision thresholds are selected, approved, monitored, and changed for quality risk scoring.

## Approval

Thresholds require approval from the quality owner, manufacturing operations lead, AI lead, and risk or compliance representative. The CDO / CAIO should approve threshold governance for any pilot that influences operational decisions.

## Review Cadence

Review thresholds weekly during pilot phases and monthly after stabilization. Review immediately after material process changes, data quality incidents, or observed performance degradation.

## False Negative Increase

If false negatives increase above the agreed tolerance, pause threshold expansion, review recent drift and data quality, and route high-risk decisions through mandatory human review. Retraining or rollback should be considered if degradation persists.

## Inspection Capacity Overload

If the threshold creates more inspection volume than the quality team can handle, raise the threshold temporarily, add sampling rules, or limit actioning to the highest-risk bands. The trade-off must be documented.

## Human Override Process

Quality managers may override model recommendations. Overrides must capture component ID, model version, score, risk band, reason, owner, and final action.

## Rollback Criteria

Rollback to the prior threshold or prior model when false-negative risk, drift, missingness, or operational load exceeds approved limits.

## Documentation Requirements

Every threshold change must record the validation evidence, expected inspection rate, recall target, approvers, effective date, and rollback plan.

