---
id: 02-ml-system-anti-slop
title: "ML System Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md", "domains/delivery/02-data-pipeline-anti-slop.md"]
category: domain
domain_type: delivery
version: 2
---

# ML System Anti-Slop Layer

This file defines behavioral contracts specific to machine learning systems. It sits in the delivery layer, below the universal anti-slop rules and alongside data pipeline patterns. It covers data leakage, train/serve skew, reproducibility, evaluation hygiene, model versioning, and production deployment. It does not cover general data pipeline rules (see `02-data-pipeline-anti-slop.md`) or LLM-specific rules (see `02-llm-system-anti-slop.md`).

A machine learning system is a contract between data and predictions. Every transformation, seed, and artifact is a guarantee of reproducibility and reliability.

## Scope

This file applies to classical ML (scikit-learn, XGBoost, LightGBM), deep learning (PyTorch, TensorFlow, JAX), feature stores (Feast, Tecton), experiment trackers (MLflow, Weights & Biases, Neptune), model registries, and serving frameworks (TorchServe, Triton, BentoML, Ray Serve). The principles are framework-agnostic. The examples use Python and common library syntax where illustrative.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A machine learning system commits to seven contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Data Integrity | Training data is free from leakage, temporal skew, and duplication. | ML-001 to ML-006 |
| Feature Parity | Features are computed identically in training and serving, using point-in-time data. | ML-007 to ML-011 |
| Reproducibility | Every training run can be exactly recreated from its artifacts and seeds. | ML-012 to ML-016 |
| Evaluation Hygiene | Models are evaluated on held-out data using task-appropriate metrics and slices. | ML-017 to ML-023 |
| Artifact Immutability | Models and datasets are versioned, registered, and never overwritten. | ML-024 to ML-027 |
| Serving Reliability | Inference is validated, budgeted, and degrades gracefully. | ML-028 to ML-033 |
| Drift Management | Data, concept, and prediction drift are monitored with explicit retraining triggers. | ML-034 to ML-038 |

## Data Discipline

### ML-001 — Data Leakage Prevention

**MUST**

Data leakage MUST be prevented. Leakage sources include target-derived features, future information, duplicate rows split across train and test, global statistics computed on the full dataset before splitting, and time-based leakage. Leakage causes models to perform well offline and fail in production.

### ML-002 — Split-Before-Compute Discipline

**MUST**

Every statistic (mean, std, min, max) computed for normalization or imputation MUST be computed on the training set only, after splitting. Computing statistics on the full dataset before splitting leaks test set information into the training process.

Example (illustrative, Python):

BAD:
```python
mean = df["feature"].mean()
df["feature"] = df["feature"] - mean
train, test = train_test_split(df)
```

GOOD:
```python
train, test = train_test_split(df)
mean = train["feature"].mean()
train["feature"] = train["feature"] - mean
test["feature"] = test["feature"] - mean
```

### ML-003 — Temporal Split Discipline

**MUST**

For temporal or time-series data, splits MUST be time-based. The test set MUST be strictly after the training set. A random split on time-series data is a form of leakage.

### ML-004 — Group Split Discipline

**MUST**

When rows belong to groups (a user, a session, a document), splits MUST be by group. Splitting within a group leaks information across the split boundary.

Example (illustrative):

BAD: Random split where the same user appears in train and test.
GOOD: `GroupKFold` or a manual group-based split.

### ML-005 — Pre-Split Deduplication

**MUST**

Duplicate rows or near-duplicates MUST be removed or handled with a deduplication-aware splitter before splitting. Duplicates leak between splits and inflate evaluation metrics.

### ML-006 — Split Validation

**MUST**

After splitting, the splits MUST be validated for class balance, distribution of key features, and absence of ID overlap across splits.

## Feature Engineering

### ML-007 — Train/Serve Feature Parity

**MUST**

The feature pipeline in training and the feature pipeline at serving MUST be the same code, or verified to produce identical results on the same input. Train/serve skew is a primary cause of production failure.

### ML-008 — Point-in-Time Correctness

**MUST**

A feature computed for a training example MUST use only data available at that example's timestamp. Computing features with data from after the example date is leakage.

### ML-009 — Feature Store Usage

**SHOULD**

When multiple models share features, a feature store (e.g., Feast, Tecton) SHOULD be used to provide point-in-time correct values for training, low-latency values for serving, and consistent definitions across models. Without a feature store, training and serving definitions drift.

### ML-010 — Raw ID Feature Prohibition

**MUST NOT**

Raw high-cardinality IDs (user ID, order ID, session ID) MUST NOT be used as features. The model memorizes the training set's specific IDs and fails on new ones. Embeddings or aggregated features MUST be used instead.

### ML-011 — Explicit Null Handling

**MUST**

Every feature's null policy (drop, impute with fixed value, impute with train mean, or treat as separate category) MUST be explicitly defined. Null handling MUST NOT be left to the library's silent default.

## Training

### ML-012 — Training Reproducibility

**MUST**

A training run MUST be reproducible. Random seeds MUST be fixed, data version pinned, code version pinned, and environment pinned (Docker image or lockfile). Without these, performance claims are unfalsifiable.

### ML-013 — Global Seed Setting

**MUST**

All relevant random seeds MUST be set at the start of the training script.

Example (illustrative, Python):
```python
random.seed(42)
numpy.random.seed(42)
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
os.environ["PYTHONHASHSEED"] = "42"
```

Some GPU operations may remain non-deterministic. This limitation MUST be documented.

### ML-014 — Dataset Versioning

**MUST**

The dataset MUST be a versioned artifact (via DVC, a dataset hash, or a table snapshot). Relying on "the file that was on disk that day" is prohibited.

### ML-015 — Hyperparameter Logging

**MUST**

Every training run MUST log its hyperparameters to an experiment tracker. A model that cannot be reproduced cannot be debugged.

### ML-016 — Baseline First Discipline

**MUST**

Before training a complex model, the simplest possible baseline (logistic regression, decision tree, heuristic) MUST be trained. The complex model's value MUST be measured against this baseline.

## Evaluation

### ML-017 — Task-Appropriate Metrics

**MUST**

The evaluation metric MUST match the task. Accuracy MUST NOT be used as the default for imbalanced classification. Appropriate metrics include precision, recall, F1, AUC-PR for imbalanced classification; MAE, RMSE, R² for regression; NDCG, MAP for ranking; and MAPE, MASE for forecasting.

### ML-018 — Held-Out Test Set

**MUST**

The test set MUST be used exactly once for final evaluation. Tuning hyperparameters or making architectural decisions on the test set is leakage.

### ML-019 — Confidence Interval Reporting

**SHOULD**

A single number on a test set is an estimate. Confidence intervals or bootstrap estimates SHOULD be reported to quantify evaluation uncertainty.

### ML-020 — Slice-Based Evaluation

**MUST**

The model MUST be evaluated on meaningful slices (user cohort, geography, device type, class). A model with high overall accuracy but poor performance on a critical slice is not ready for production.

### ML-021 — Fairness Metric Reporting

**SHOULD**

Where relevant, fairness metrics (demographic parity, equal opportunity, predictive parity) SHOULD be reported across protected groups, regardless of legal requirements.

### ML-022 — Error Analysis

**MUST**

The worst errors MUST be analyzed. A model's failure mode is often obvious in misclassified examples and invisible in aggregate metrics.

### ML-023 — Test Set Isolation

**MUST NOT**

Unit tests in CI MUST NOT access the test set. Model evaluation MUST be a separate, deliberate step.

## Model Versioning and Registry

### ML-024 — Model Artifact Metadata

**MUST**

Every model MUST be a versioned artifact containing the version number, training data version, code version, evaluation metrics, and hyperparameters.

### ML-025 — Model Registry Usage

**MUST**

A model registry (e.g., MLflow, SageMaker Model Registry) MUST be used to track which model is in production, which is in staging, and the history of promotions and rollbacks.

### ML-026 — Artifact Immutability

**MUST NOT**

A registered model version MUST NEVER be overwritten. A new training run MUST produce a new version.

### ML-027 — Model Signature Definition

**MUST**

A registered model MUST include an input/output signature defining expected feature types and the output schema. Serving endpoints MUST validate against it.

## Serving

### ML-028 — Train/Serve Parity Testing

**MUST**

The feature pipeline in training and serving MUST be explicitly tested to ensure it produces the same values for the same input.

### ML-029 — Inference Latency Budget

**MUST**

A model's inference latency MUST be measured and have a defined budget (e.g., milliseconds for real-time, minutes for batch).

### ML-030 — Batch vs Real-Time Separation

**MUST**

Batch inference MUST be used for reporting and offline scoring. Real-time inference MUST be used for user-facing predictions. The wrong paradigm MUST NOT be forced for a given use case.

### ML-031 — Graceful Degradation

**MUST**

If the model service is down, the system MUST fall back to a heuristic, a cached prediction, or a default. The calling service MUST NOT crash.

### ML-032 — Serving Input Validation

**MUST**

The serving endpoint MUST validate inputs against the model's signature. Unexpected inputs MUST produce a clear error, not a silent wrong prediction.

### ML-033 — Serving Telemetry Monitoring

**MUST**

Prediction distribution, input feature distribution, latency percentiles, and error rate MUST be monitored. Alerts MUST fire when metrics drift beyond thresholds.

## Monitoring and Drift

### ML-034 — Data Drift Monitoring

**MUST**

Input distribution changes MUST be monitored by tracking per-feature statistics (mean, std, quantiles, null rate) against the training baseline.

### ML-035 — Concept Drift Monitoring

**MUST**

When ground truth is available (even delayed), the model's live performance MUST be monitored to detect changes in the relationship between inputs and target.

### ML-036 — Prediction Drift Monitoring

**MUST**

The distribution of predictions (mean, variance, class balance) MUST be monitored over time.

### ML-037 — Statistical Drift Thresholds

**MUST**

Drift alerts MUST use statistical tests (KS test, PSI, KL divergence) with thresholds tuned to the domain, rather than arbitrary percentage changes.

### ML-038 — Explicit Retraining Triggers

**MUST**

Retraining triggers MUST be explicitly defined (scheduled, on drift alert, or on performance drop). Retraining MUST NOT rely on ad-hoc human memory.

## AI-Specific ML Discipline

### ML-060 — Library API Verification

**MUST**

Before using a machine learning library API (e.g., a specific scikit-learn estimator, PyTorch layer, or XGBoost parameter), the assistant MUST verify the method or parameter exists in the installed version. Invented APIs or deprecated parameters produce runtime errors or silent fallbacks to defaults.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### ML-061 — Existing Pipeline Discovery

**MUST**

Before creating a new feature transformation, model architecture, or training loop, the assistant MUST search the project for an existing equivalent. Inventing parallel feature definitions or training scripts creates train/serve skew and maintenance burden.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### ML-062 — Algorithm Complexity Restraint

**SHOULD**

The assistant SHOULD NOT introduce complex model architectures (e.g., deep ensembles, custom attention mechanisms) when a simpler baseline (e.g., logistic regression, XGBoost) has not been established and proven insufficient.

See MAS-038 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### ML-039 — Notebook-to-Production Prohibition

**MUST NOT**

A model trained in an interactive notebook and copy-pasted into a production script is prohibited. The training code MUST be importable, and the same functions MUST run in training and serving.

### ML-040 — Training Set Evaluation Prohibition

**MUST NOT**

Reporting performance on the training set (e.g., `model.score(X_train, y_train)`) as the model's true performance is prohibited. Evaluation MUST occur on a held-out set.

### ML-041 — Feature Definition Drift

**MUST NOT**

Multiple models using slightly different definitions of the same concept (e.g., `user_lifetime_value`) without a centralized feature store or registry is prohibited. Definitions MUST NOT drift.

### ML-042 — Silent Model Update Prohibition

**MUST NOT**

Deploying a new model version without announcement is prohibited. Downstream consumers MUST be warned of changed predictions.

### ML-043 — Model Rollback Capability

**MUST**

A path back to the previous model version MUST be maintained. The previous model MUST remain registered and deployable in case the new model performs worse in production.

### ML-044 — Accuracy and Drift Monitoring

**MUST NOT**

Monitoring only latency without monitoring accuracy or drift is prohibited. A model that is fast and wrong is a failure.

### ML-045 — Class Imbalance Metric Discipline

**MUST NOT**

Using accuracy as the sole metric for highly imbalanced datasets (e.g., fraud detection) is prohibited. Appropriate metrics (AUC-PR, Recall) MUST be used.

### ML-046 — Cryptographic Data Versioning

**MUST**

Datasets MUST be versioned using a hash, a DVC pointer, or a table snapshot with a timestamp. Versioning by filename (e.g., `data_v2_final_final.csv`) is prohibited.

### ML-047 — Model Binary Git Prohibition

**MUST NOT**

Large model binaries (e.g., `model.pkl`) MUST NOT be committed to Git. Models MUST be stored in a registry or object storage and referenced by version.

### ML-048 — Framework-Agnostic Model Export

**SHOULD**

Models SHOULD be exported in a framework-agnostic format (e.g., ONNX) or the serving environment MUST be strictly pinned to the training environment to prevent library version mismatches.

### ML-049 — Pre-Deployment Model Comparison

**MUST NOT**

Deploying a retrained model without comparing it to the current production model is prohibited. The new model MUST be evaluated against the baseline.

### ML-050 — Production Model Overwrite Prohibition

**MUST NOT**

Overwriting a production model file in place (e.g., `cp new_model.pkl production_model.pkl`) is prohibited. A versioned registry with a promotion step MUST be used.

## Response to Violation

When a rule in this file is violated, report:

Violation: ML-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.