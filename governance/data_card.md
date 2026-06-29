# Data Card

## Data Source

Kaggle Bosch Production Line Performance dataset containing anonymized production-line measurements and tests.

## Granularity

One row per component ID per file after joining numeric, categorical, and date feature sets.

## Data Types

- Numeric sensor and test measurements.
- Categorical station/test outcomes.
- Date or process-sequence timing features.
- Binary response target in training data.

## Known Limitations

- Feature meanings are anonymized.
- Business station metadata is unavailable.
- Production cost, inspection cost, and downstream warranty outcomes are absent.
- Public competition data may not reflect current process conditions.

## Anonymization Constraints

Anonymization protects operational details but limits explainability. Before deployment, high-impact anonymized features must be mapped to real stations, tests, owners, and quality procedures.

## Data Quality Risks

- High sparsity.
- Rare target.
- Potential time-based leakage.
- Process changes not represented in the historical extract.
- Incomplete lineage from raw station event to curated model feature.

## Recommended Owners

- Data owner: Manufacturing data product owner.
- Data steward: Quality analytics steward.
- Technical owner: Data engineering lead.
- Business owner: Quality manager or manufacturing lead.

## Retention Assumptions

Retention should align with quality audit requirements, warranty risk, regulatory obligations, and internal manufacturing traceability policies.

## Lineage Assumptions

Deployment requires lineage from source station systems through ingestion, transformation, feature store, model version, dashboard, and final operational decision.
