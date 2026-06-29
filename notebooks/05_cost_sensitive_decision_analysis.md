# 05 Cost-Sensitive Decision Analysis

## Purpose

Define how inspection cost, false-positive cost, and false-negative cost should influence threshold selection for manufacturing quality risk scoring.

## Cost of False Negatives

False negatives represent components that are predicted as low enough risk to avoid action but later fail. In manufacturing quality, this is usually the most important operating risk because missed failures can create rework, scrap, warranty exposure, or downstream process disruption.

## Cost of False Positives

False positives route components to inspection or monitoring even when they would not fail. This can consume inspection capacity, slow production flow, and reduce trust in the model if volumes are too high.

## Cost of Inspection

Inspection cost includes labor, equipment time, queueing, production delay, and administrative handling. The threshold should be tested against realistic inspection capacity.

## Threshold Trade-Off Analysis

The implementation should compare candidate thresholds by recall, false-negative rate, precision, and inspection rate. A cost table can then estimate expected cost under different false-negative and false-positive assumptions.

## Recommended Next Step

Replace illustrative cost assumptions with validated plant-specific values. Use those assumptions to select a threshold jointly approved by quality, operations, and AI governance owners.
