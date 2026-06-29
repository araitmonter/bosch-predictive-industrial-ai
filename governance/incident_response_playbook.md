# Incident Response Playbook

## Incident Triggers

- False-negative rate exceeds approved tolerance.
- Prediction drift or feature-level PSI crosses red thresholds.
- Missingness increases beyond data quality limits.
- Dashboard or scoring API becomes unavailable during pilot operations.
- Quality team reports inconsistent or unusable risk bands.

## Example Incidents

- A station feed stops populating key features.
- The model escalates too many components for available inspection capacity.
- A process change shifts prediction distributions.
- Delayed labels show a material drop in recall.

## Immediate Actions

1. Confirm the affected model version, threshold, data window, and production scope.
2. Notify the quality manager, AI lead, data engineering lead, and product owner.
3. Pause threshold changes and restrict actioning to human-reviewed decisions.
4. Check data quality, feature availability, scoring logs, and recent process changes.

## Escalation Path

Quality analyst -> Quality manager -> Manufacturing lead -> AI lead -> CDO / CAIO -> Risk or compliance representative.

## Communication Requirements

Document the incident summary, affected time window, operational impact, temporary control, owner, next update time, and recovery criteria.

## Rollback Actions

- Revert to the prior model version or prior threshold.
- Disable automated score consumption by downstream workflows.
- Move to shadow mode until validation evidence is restored.

## Post-Incident Review

Within five business days, review root cause, control effectiveness, monitoring gaps, and any required changes to data contracts, threshold policy, or approval workflow.

