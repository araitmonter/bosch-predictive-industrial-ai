# Business Case Simulation

This document provides an illustrative scenario model for evaluating the potential value of predictive quality risk scoring. The assumptions are hypothetical and are not Bosch operational figures.

| Scenario | Inspection Capacity | Recall Target | Expected Operational Effect | Cost Assumption | Executive Interpretation |
|---|---:|---:|---|---:|---|
| Conservative | 5% of components | 60% | Focus inspection on the highest-risk components | Illustrative | Low-disruption pilot |
| Base case | 10% of components | 75% | Balance defect capture and inspection workload | Illustrative | Recommended starting point |
| Aggressive | 15% of components | 85% | Maximize defect capture with higher inspection load | Illustrative | Use if quality risk appetite is low |

## Decision Variables

- Inspection capacity as a percentage of components.
- Minimum recall target.
- Accepted false-negative risk.
- Cost of inspection.
- Cost of missed defects.
- Operational tolerance for escalations.

## Cost Drivers

- Additional inspection labor or automated inspection utilization.
- Scrap, rework, warranty, or customer-impact cost from missed failures.
- Production delay from inspection routing.
- Data engineering and monitoring effort required to run the pilot.

## Sensitivity Analysis Concept

The business case should be evaluated across a range of false-negative cost, false-positive cost, and inspection-capacity assumptions. A threshold that looks attractive under one cost ratio may be impractical if inspection capacity is constrained.

## How Executives Should Use This Model

Use the simulation to define risk appetite and pilot boundaries. The model should inform a decision on inspection prioritization strategy, not serve as proof of financial impact. Actual value estimates require plant-specific cost data, validated labels, and operational workflow measurements.

