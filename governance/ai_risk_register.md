# AI Risk Register

| Risk | Severity | Likelihood | Business Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| False negatives | High | Medium | Defective components may pass normal flow, increasing warranty, scrap, rework, or customer risk. | Optimize for recall, monitor false-negative rate, maintain human review for borderline cases. | Quality Manager |
| False positives | Medium | High | Excess inspection load and production friction. | Calibrate thresholds by capacity and cost, monitor inspection rate. | Manufacturing Lead |
| Model drift | High | Medium | Model performance degrades after process, supplier, equipment, or material changes. | PSI monitoring, performance monitoring, retraining triggers. | AI Lead |
| Data quality degradation | High | Medium | Missing or corrupted station data produces unreliable scores. | Data quality gates, station-level alerts, ingestion SLAs. | Data Engineer |
| Lack of explainability | Medium | High | Stakeholders may not trust or correctly act on scores. | SHAP/permutation importance, local explanations, governance notes. | AI Lead |
| Feature anonymity | High | High | High-impact predictors cannot be operationally mapped to root causes. | Map anonymized features to real stations before deployment. | Data Steward |
| Over-automation | High | Medium | Automated decisions may interrupt production without approved controls. | Human-in-the-loop policy and approval workflow. | COO / Manufacturing Lead |
| Operational misuse | Medium | Medium | Dashboard may be treated as a deterministic quality verdict. | User training, decision policy, audit logging. | Product Owner |
| Governance gaps | High | Medium | Model lacks clear accountability, approval, monitoring, or retirement process. | AI operating model, model card, risk review cadence. | CDO |

