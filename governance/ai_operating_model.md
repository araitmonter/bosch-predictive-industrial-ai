# AI Operating Model

## Operating Principle

Predictive quality AI should be managed as a governed manufacturing capability, not a standalone analytics model. Accountability must cover data, model, decision policy, monitoring, and business outcomes.

## Role Responsibilities

| Role | Responsibilities |
|---|---|
| CDO | Owns data strategy, governance standards, lineage expectations, and enterprise AI accountability. |
| COO / Manufacturing Lead | Owns operational adoption, production risk appetite, and escalation policy. |
| AI Lead | Owns model development, validation, explainability, and performance monitoring. |
| Data Engineer | Owns ingestion, pipelines, feature generation, data quality automation, and observability. |
| Data Steward | Owns metadata, feature definitions, station mapping, and data issue resolution. |
| Quality Manager | Owns inspection workflow, false-negative risk, feedback labels, and operational response. |
| Risk / Compliance | Reviews model risk, auditability, approval evidence, and control effectiveness. |
| Product Owner | Owns roadmap, user requirements, dashboard adoption, and value tracking. |

## RACI

| Activity | CDO | COO / Manufacturing | AI Lead | Data Engineer | Data Steward | Quality Manager | Risk / Compliance | Product Owner |
|---|---|---|---|---|---|---|---|---|
| Data architecture approval | A | C | C | R | R | C | C | C |
| Data quality gates | A | C | C | R | R | C | C | C |
| Feature-store design | C | C | A | R | R | C | C | C |
| Model training and validation | C | C | A/R | C | C | C | C | C |
| Threshold policy | C | A | R | C | C | R | C | C |
| Dashboard adoption | C | A | C | C | C | R | C | R |
| Model approval | A | A | R | C | C | C | R | C |
| Monitoring operations | A | C | R | R | R | R | C | C |
| Retraining decision | A | C | R | C | C | C | C | R |
| Incident response | C | A | R | R | R | R | C | C |

