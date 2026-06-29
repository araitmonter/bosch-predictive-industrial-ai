# Model Card

## Model Purpose

The model estimates the probability that a manufactured component will experience an internal failure. It supports risk-based inspection, monitoring, and escalation decisions.

## Intended Users

- Quality managers.
- Manufacturing operations leaders.
- Industrial AI product owner.
- Data science and ML engineering teams.
- AI governance and risk stakeholders.

## Business Decision Supported

The model supports whether a component should pass normal flow, be monitored, receive targeted inspection, or be escalated to quality leadership.

## Input Data

Anonymized numeric, categorical, and date features from the Bosch production-line dataset, joined by component `Id`.

## Target Variable

`Response`: binary indicator of internal manufacturing failure.

## Metrics

Primary metrics:

- Recall.
- False-negative rate.
- PR-AUC.
- Precision.
- F1.

Secondary metrics:

- ROC-AUC.
- Inspection rate.
- Prediction distribution by risk band.

## Decision Threshold

Thresholds should be selected using manufacturing risk appetite. False negatives carry higher operational risk than false positives, but false positives consume inspection capacity.

## Limitations

- Features are anonymized.
- The public dataset does not provide station-level business definitions.
- Validation must mirror the real operational scoring time.
- Cost data is not available, so business value is a hypothesis.

## Risks

- Missed failures.
- Excess inspection load.
- Model drift.
- Data quality degradation.
- Misinterpretation of anonymized feature importance.
- Over-automation without quality manager review.

## Approval Requirements

Deployment requires approval from manufacturing leadership, quality leadership, AI governance, data ownership, and risk/compliance.

## Monitoring Requirements

Monitor recall, false-negative rate, missing-rate trends, drift, prediction distribution, inspection volume, and override behavior.

## Retraining Policy

Retrain when PSI exceeds agreed thresholds, missing rates materially degrade, recall drops below minimum operating levels, or process changes alter station behavior.

## Human-In-The-Loop Recommendation

High and critical risk scores should trigger human review. The model should recommend action, not autonomously stop production, unless explicitly approved through operational risk governance.

