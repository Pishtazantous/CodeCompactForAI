---
id: 02-ml-system-anti-slop
title: "ML System Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---

# ML System Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file covers rules specific to machine learning systems: data
leakage, train/serve skew, reproducibility, evaluation hygiene, model
versioning, and production deployment. General data pipeline rules
live in `domains/delivery/02-data-pipeline-anti-slop.md`. LLM-specific
rules live in `domains/delivery/02-llm-system-anti-slop.md`.

## 1. Stack Assumptions

This layer applies to:

- Classical ML (scikit-learn, XGBoost, LightGBM)
- Deep learning (PyTorch, TensorFlow, JAX)
- Feature stores (Feast, Tecton)
- Experiment trackers (MLflow, Weights & Biases, Neptune)
- Model registries
- Serving frameworks (TorchServe, Triton, BentoML, Ray Serve)

The principles are framework-agnostic.

## 2. Data Discipline

### 2.1 No Data Leakage

The single most common cause of a model that looks great offline and
fails in production. Leakage sources:

- Target-derived features (a feature computed from the target).
- Future information (a feature computed after the prediction time).
- Duplicate rows split across train and test.
- Global statistics computed on the full dataset before splitting.
- Time-based leakage (shuffling time-series data).

### 2.2 Split Before You Compute

BAD: Compute the mean of the full dataset, then split into train/test.
GOOD: Split first, compute the mean on the train set, apply it to
both.

Every statistic (mean, std, min, max) computed for normalization or
imputation is computed on train only.

### 2.3 Time-Based Splits for Temporal Data

BAD: A random split on a time-series dataset.
GOOD: Train on older data, test on newer data.

For a forecasting model, the test set must be strictly after the
training set. A random split is a form of leakage.

### 2.4 Group Splits for Clustered Data

When rows belong to groups (a user, a session, a document), split by
group. Splitting within a group leaks information across the split.

BAD: Random split where the same user appears in train and test.
GOOD: `GroupKFold` or a manual group-based split.

### 2.5 Deduplicate Before Splitting

Duplicate rows (or near-duplicates) leak between splits. Deduplicate
or use a deduplication-aware splitter.

### 2.6 Validate the Split

After splitting, check:

- Class balance per split.
- Distribution of key features per split.
- No overlap of IDs across splits.

## 3. Feature Engineering

### 3.1 Features Computed the Same Way in Train and Serve

Train/serve skew is the second most common cause of production
failure. The feature pipeline in training and the feature pipeline at
serving must be the same code, or verified to produce identical
results on the same input.

### 3.2 Point-in-Time Correctness

A feature computed for a training example uses only data available at
that example's timestamp. Computing `total_orders_last_30_days` with
data from after the example date is leakage.

### 3.3 Feature Store When Multiple Models Share Features

A feature store (Feast, Tecton) provides:

- Point-in-time correct feature values for training.
- Low-latency feature values for serving.
- Consistent definitions across models.

Without a feature store, the training code and the serving code drift.

### 3.4 No ID Features Unless Justified

A user ID, an order ID, or a session ID as a raw feature encodes the
training set's specific IDs. The model memorizes them and fails on
new IDs.

Use embeddings or aggregated features instead.

### 3.5 Null Handling Is Explicit

Every feature's null policy is defined:

- Drop the row.
- Impute with a fixed value.
- Impute with the train mean (see section 2.2).
- Treat null as a separate category.

The choice affects the model's behavior. Do not leave it to the
library's default silently.

## 4. Training

### 4.1 Reproducibility

A training run is reproducible:

- Random seeds fixed for every library.
- Data version pinned (DVC, a dataset hash, a snapshot).
- Code version pinned (git SHA).
- Environment pinned (Docker image or a lockfile).

Without these, "the model was better yesterday" is unfalsifiable.

### 4.2 Seed Everything

Python: `random.seed`, `numpy.random.seed`, `torch.manual_seed`,
`torch.cuda.manual_seed_all`, `PYTHONHASHSEED`.

Some GPU operations are still non-deterministic. Document the
limitation.

### 4.3 Version the Dataset

The dataset is a versioned artifact, not "the file that was on disk
that day". Use DVC, a table snapshot, or a hash.

### 4.4 Hyperparameters Are Logged

Every run logs its hyperparameters. A model that cannot be
reproduced cannot be debugged.

### 4.5 Baseline First

Before a complex model, train the simplest possible baseline
(logistic regression, a decision tree, a heuristic). The complex
model's value is measured against it.

BAD: A 12-layer transformer with no baseline.
GOOD: A baseline, then a transformer with a documented improvement.

## 5. Evaluation

### 5.1 The Right Metric for the Task

- Classification with balanced classes: accuracy.
- Classification with imbalanced classes: precision, recall, F1,
  AUC-PR.
- Regression: MAE, RMSE, R².
- Ranking: NDCG, MAP, MRR.
- Forecasting: MAPE, sMAPE, MASE.

Do not default to accuracy. It hides failure on the minority class.

### 5.2 Evaluation on a Held-Out Set

The test set is used once. Tuning on the test set is leakage.

### 5.3 Confidence Intervals

A single number on a test set is an estimate. Report the confidence
interval or a bootstrap estimate.

### 5.4 Slice-Based Evaluation

Evaluate the model on meaningful slices:

- By user cohort.
- By geography.
- By device type.
- By class.

A model with 90% overall accuracy and 40% on a critical slice is not
ready.

### 5.5 Fairness Metrics

Where relevant, report:

- Demographic parity.
- Equal opportunity.
- Predictive parity.

Even if the project has no legal requirement, knowing the model's
behavior across groups matters.

### 5.6 Error Analysis

Look at the worst errors. A model's failure mode is often obvious in
the misclassified examples, and invisible in the aggregate metric.

### 5.7 No Test Set in CI

A unit test does not touch the test set. Model evaluation is a
separate, deliberate step.

## 6. Model Versioning and Registry

### 6.1 Every Model Has a Version

A model is a versioned artifact:

- Version number or timestamp.
- Training data version.
- Code version.
- Metrics from evaluation.
- Hyperparameters.

### 6.2 Registry

A model registry (MLflow, SageMaker Model Registry, Weights & Biases)
tracks:

- Which model is in production.
- Which model is in staging.
- The history of promotions and rollbacks.

### 6.3 Immutable Artifacts

A model version, once registered, is never overwritten. A new
training run produces a new version.

### 6.4 Signatures

A registered model includes an input/output signature: the expected
feature types and the output schema. Serving validates against it.

## 7. Serving

### 7.1 Train/Serve Parity

The feature pipeline in training and the feature pipeline at serving
produce the same values for the same input. Test this.

### 7.2 Latency Budget

A model's inference latency is measured and has a budget. A
100 ms budget is different from a 1-second budget.

- Batch inference: minutes to hours.
- Real-time inference: milliseconds to hundreds of milliseconds.
- Streaming: tens of milliseconds.

### 7.3 Batch vs Real-Time

Batch inference for reporting and offline scoring. Real-time
inference for user-facing predictions. Do not force one where the
other fits.

### 7.4 Graceful Degradation

If the model service is down:

- Fall back to a heuristic, a cached prediction, or a default.
- Never crash the calling service.

### 7.5 Input Validation at Serving

The serving endpoint validates inputs against the model's signature.
An unexpected input produces a clear error, not a silent wrong
prediction.

### 7.6 Monitoring

- Prediction distribution over time.
- Input feature distribution over time.
- Latency percentiles.
- Error rate.

An alert when any drifts beyond a threshold.

## 8. Monitoring and Drift

### 8.1 Data Drift

The input distribution changes. Monitor per-feature statistics
(mean, std, quantiles, null rate) against the training baseline.

### 8.2 Concept Drift

The relationship between inputs and target changes. Monitor the
model's live performance when ground truth is available (even
delayed).

### 8.3 Prediction Drift

The distribution of predictions changes. Monitor mean, variance, and
class balance.

### 8.4 Alert Thresholds

Drift alerts use statistical tests (KS test, PSI, KL divergence) with
thresholds tuned to the domain.

### 8.5 Retraining Trigger

Define what triggers retraining:

- Scheduled (weekly, monthly).
- On drift alert.
- On performance drop below a threshold.

Do not retrain "when someone remembers".

## 9. ML-Specific Anti-Patterns

### 9.1 Data Leakage

Covered in 2.1. The most damaging ML mistake.

### 9.2 Train/Serve Skew

Covered in 3.1.

### 9.3 Notebook-to-Production

A model trained in a Jupyter notebook, then copy-pasted into a
production script. The two drift immediately.

GOOD: The training code is importable, and the same functions run in
training and serving.

### 9.4 No Seed

Covered in 4.2.

### 9.5 Accuracy as the Only Metric

Covered in 5.1.

### 9.6 Evaluating on the Training Set

BAD: `model.score(X_train, y_train)` reported as the model's
performance.
GOOD: Performance on a held-out set.

### 9.7 Hyperparameter Tuning on the Test Set

Covered in 5.2.

### 9.8 No Baseline

Covered in 4.5.

### 9.9 Feature Store Not Used When It Should Be

Two models with two slightly different definitions of
`user_lifetime_value`. The definitions drift. Predictions are
inconsistent.

### 9.10 Silent Model Updates

A new model version deployed without announcement. Downstream
consumers see changed predictions with no warning.

### 9.11 No Rollback

A model that performs worse in production than offline has no path
back to the previous version. Keep the previous model registered and
deployable.

### 9.12 Monitoring Only Latency

A model is fast and wrong. Monitoring latency without monitoring
accuracy or drift misses the actual problem.

### 9.13 Ignoring Class Imbalance

A fraud detection model with 99.9% accuracy that never predicts
fraud. Accuracy is meaningless here.

### 9.14 Raw IDs as Features

Covered in 3.4.

### 9.15 Global Statistics From Full Data

Covered in 2.2.

### 9.16 Random Split on Time-Series

Covered in 2.3.

### 9.17 No Confidence Intervals

Covered in 5.3.

### 9.18 Data Versioning by Filename

BAD: `data_v2_final_final.csv`.
GOOD: A hash, a DVC pointer, or a table snapshot with a timestamp.

### 9.19 No Error Analysis

Covered in 5.6.

### 9.20 Model in the Repository

BAD: A 2 GB `model.pkl` committed to Git.
GOOD: The model in a registry or object storage, referenced by
version.

### 9.21 Serving a Notebook's Model Object Directly

A pickled scikit-learn model that depends on a specific version of
scikit-learn. Upgrading the library breaks the model.

GOOD: Export the model in a framework-agnostic format (ONNX) or pin
the serving environment to the training environment.

### 9.22 No Input Validation at Serving

Covered in 7.5.

### 9.23 Fallback Crashes

Covered in 7.4.

### 9.24 Retraining Without Evaluation

A new model trained and deployed without comparing to the current
production model. The new one may be worse.

### 9.25 Overwriting the Production Model

BAD: `cp new_model.pkl production_model.pkl`.
GOOD: A versioned registry with a promotion step.

## 10. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
