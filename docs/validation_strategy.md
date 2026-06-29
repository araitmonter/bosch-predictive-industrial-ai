# Validation Strategy

## Why the random split is only a baseline

The Bosch dataset contains production-line measurements, station identifiers, and process-timing features. A stratified random split is useful for a fast baseline because it preserves the rare failure rate in train and validation data. It is not enough to estimate operational performance.

In a live scoring setting, the model scores components before future outcomes are known. Random splits can mix similar process periods across train and validation data and make performance look more stable than it would be after a line change, maintenance event, supplier shift, or measurement drift.

## Why leakage matters

Production-line data can contain fields that are close to the failure event or encode downstream process timing. Date and process-sequence features are especially useful, but they need review. A feature that is recorded after the decision point should not be used for a score that is supposed to support that decision.

The project includes `leakage_feature_audit()` to flag target-like names and date/process-sequence fields for review. The audit is intentionally conservative; flagged fields are not automatically removed because the public dataset does not include the actual station event times.

## Lightweight implementation in this repo

The training pipeline uses an ID-based ordered holdout when `Id` is available. This is not a full time-aware validation design, but it is a better default than a purely random split for a lightweight local prototype.

For production use, validation should use actual event timestamps:

- Train on earlier production periods.
- Validate on later production periods.
- Ensure each feature is available before the scoring decision.
- Track performance by line, station, shift, supplier, and product family.
- Re-run validation after process or equipment changes.

