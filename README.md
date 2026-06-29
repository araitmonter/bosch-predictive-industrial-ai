# Responsible Industrial AI for Bosch Manufacturing Quality

**Predictive Quality, Data Architecture, AI Governance and Executive Decision Intelligence for Smart Manufacturing**

This portfolio project demonstrates how an enterprise manufacturing organization could design, govern, and operationalize predictive quality AI using the Kaggle **Bosch Production Line Performance** dataset. The objective is not to reproduce a Kaggle leaderboard exercise. The objective is to show how a Chief Data Officer, Chief AI Officer, COO, Head of Manufacturing, or Quality Director could evaluate and deploy a risk-scoring capability responsibly.

The visual and writing style is inspired by Bosch's corporate identity through a red, black, white, and steel-gray executive design language. It does not use Bosch logos or copyrighted brand assets.

## Business Problem

Manufacturing defects create avoidable inspection cost, scrap, warranty exposure, rework, capacity loss, and customer risk. Traditional quality control often detects failures after substantial production value has already been added. A predictive quality capability can prioritize inspection and operational response earlier in the production flow.

In this project, each component is treated as an operational decision unit. The model estimates the probability that a component will experience an internal manufacturing failure. The output is framed as a **quality risk score** with decision bands:

| Risk Band | Decision Intent |
|---|---|
| Low risk: pass | Continue normal flow |
| Medium risk: monitor | Track in quality operations |
| High risk: inspect | Route to targeted inspection |
| Critical risk: escalate | Escalate to quality leadership |

## Dataset

The project uses the Kaggle competition dataset **Bosch Production Line Performance**. The source files include numeric, categorical, and date features for training and test components. The target variable is `Response`, where positive cases represent internal manufacturing failures.

The dataset is anonymized. Feature names encode line, station, and feature identifiers, but not the underlying physical test or sensor meaning. This is realistic for a public dataset but creates a major governance constraint: high-impact features must be mapped back to real production stations before deployment.

## AI Opportunity

The opportunity is to move from reactive inspection to **risk-based quality operations**:

- Prioritize scarce inspection capacity toward higher-risk components.
- Reduce false negatives by tuning thresholds around manufacturing risk appetite.
- Create transparent governance around model limitations and monitoring controls.
- Connect model output to executive decision intelligence, not only data science metrics.

## Solution Architecture

The target architecture follows an enterprise medallion pattern:

`Production Line Sensors / Test Stations -> Raw Data Ingestion -> Bronze Data Lake -> Data Quality & Validation -> Silver Manufacturing Data -> Gold Feature Store -> ML Training Pipeline -> Model Registry -> Risk Scoring API -> Executive + Quality Operations Dashboards -> Monitoring + Governance Controls`

See [governance/data_architecture_blueprint.md](governance/data_architecture_blueprint.md) for the full architecture blueprint.

## Modeling Approach

The predictive model is designed as a **manufacturing quality risk scorer**:

- Baseline model for reference.
- Gradient boosting model using LightGBM or XGBoost when available.
- Stratified validation to preserve the rare-failure target structure.
- Class imbalance handling through positive-class weighting and threshold optimization.
- Metrics: precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, and false-negative rate.
- Threshold selection based on business trade-offs, not default 0.50 classification.

## Governance Layer

The repository includes governance artifacts expected in an enterprise AI program:

- Model card.
- Data card.
- AI risk register.
- AI operating model and RACI.
- Explainability notes.
- Monitoring framework.
- Data readiness assessment.

These documents explicitly address model drift, data quality degradation, anonymized feature risk, human-in-the-loop controls, approval requirements, and retraining policy.

## Executive Dashboard

The Streamlit dashboard presents four executive pages:

1. Executive Overview.
2. Production Risk Intelligence.
3. AI Governance & Monitoring.
4. Strategic Recommendation.

It is intentionally styled as a restrained, industrial executive dashboard using red, black, white, gray, and subtle steel-blue accents.

## Final Deliverables

- `notebooks/01_data_readiness_assessment.ipynb`
- `notebooks/02_predictive_modeling.ipynb`
- `notebooks/03_explainable_ai.ipynb`
- `notebooks/04_model_monitoring_simulation.ipynb`
- `dashboard/app.py`
- `governance/*.md`
- `executive/*.md`
- `reports/technical_report.md`
- Modular Python source code under `src/`

## Key Limitations

- Public dataset features are anonymized, so root-cause interpretation is constrained.
- The sample execution path is designed for local portfolio use and does not replace full-scale distributed training.
- The model is not production-ready until validated against operational scoring time, station metadata, inspection capacity, cost curves, and live process drift.
- The dashboard is an executive prototype, not a validated operational control system.

## How To Run

1. Place the Kaggle ZIP files in `data/raw/`, or set:

```bash
export BOSCH_DATA_SOURCE_DIR="$HOME/Downloads/bosch-production-line-performance"
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Generate a local sample:

```bash
python -m src.make_sample
```

4. Train the model:

```bash
python -m src.train_model
```

5. Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

The project works with sampled data to avoid expanding multi-gigabyte raw files into the repository.

