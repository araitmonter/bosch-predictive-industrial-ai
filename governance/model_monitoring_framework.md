# Model Monitoring Framework

## Monitoring Objective

Monitoring ensures the predictive quality model remains reliable as production processes, equipment, suppliers, materials, and data pipelines change.

## Metrics

| Metric | Purpose | Alert Logic |
|---|---|---|
| Data quality score | Measures overall feature completeness and validity. | Amber below 85; red below 75. |
| Missing rate | Detects sensor, station, or ingestion degradation. | Amber above baseline +5%; red above baseline +10%. |
| PSI or drift proxy | Detects distribution shift. | Amber above 0.10; red above 0.25. |
| Model recall | Measures failure capture. | Amber below target; red below minimum operating threshold. |
| False-negative rate | Measures missed failure risk. | Red when above agreed risk appetite. |
| Prediction distribution drift | Detects change in risk-score mix. | Alert when high-risk volume changes materially. |
| Retraining alert | Combines drift, quality, and performance rules. | Trigger model review or retraining workflow. |

## Simulated Scenarios

The monitoring notebook simulates:

- Increased missing values.
- Prediction distribution drift.
- Performance degradation.
- Threshold sensitivity.
- Retraining trigger.

## Governance Workflow

1. Daily automated checks.
2. Weekly quality operations review.
3. Monthly AI governance review.
4. Retraining recommendation when thresholds are breached.
5. Approval before replacing the production model.

## Production Requirement

Performance monitoring requires delayed outcome labels. Until labels are available, drift and data quality monitoring should be treated as early-warning indicators, not proof of model failure.

