# Technical Report

## Objective

Build a governed predictive quality risk-scoring prototype using the Bosch Production Line Performance dataset.

## Data

The dataset includes separate numeric, categorical, and date files. Training data contains the `Response` target in the numeric file. Local execution uses a station-diverse sample to keep the repository portable while preserving the project structure required for full-scale execution.

## Modeling

The recommended model is gradient boosting with class imbalance handling. LightGBM is preferred for wide sparse tabular data. The code falls back to scikit-learn gradient boosting when LightGBM is unavailable.

## Validation

Validation uses stratification because the positive class is rare. The report emphasizes recall, false-negative rate, PR-AUC, and inspection-rate trade-offs.

## Explainability

SHAP is recommended where available. Permutation importance is included as a model-agnostic fallback. Anonymized feature names are a material governance limitation.

## Monitoring

Monitoring includes missing-rate trends, PSI drift proxy, prediction distribution drift, recall, false-negative rate, and retraining triggers.

## Production Considerations

This project is a governed prototype. Production deployment requires station metadata, event-time validation, data contracts, model registry controls, human-in-the-loop workflow design, and ongoing monitoring.

