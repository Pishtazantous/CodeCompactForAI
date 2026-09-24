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

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Security and deployment behavior use the related layers.

## 1. Stack Assumptions

**1.1 Define the prediction contract.** Identify task, prediction horizon,
unit of inference, output schema, latency, and cost budget.

**1.2 Establish data boundaries.** Name training, validation, serving, and
label sources, including their time and access boundaries.

**1.3 Follow the existing lifecycle.** Reuse the repository's experiment,
registry, feature, deployment, and monitoring conventions.

## 2. Domain Contracts

**2.1 Training and serving use compatible features.** Pin feature definitions,
transforms, missing-value behavior, and schema versions across environments.

**2.2 Leakage is prohibited.** A feature or label must not contain information
that is unavailable at prediction time or directly encodes the target.

**2.3 Every model is reproducible.** Record code revision, data snapshot,
parameters, environment, seeds, and artifact digest.

**2.4 Evaluation is decision evidence.** Define metrics, slices, thresholds,
baseline, confidence limits, and failure costs before promotion.

**2.5 Version artifacts explicitly.** A model name without data, feature,
schema, and runtime versions is not deployable.

## 3. Domain-Specific Rules

**3.1 Detect skew continuously.** Compare feature distributions, missingness,
ranges, and categorical frequencies between training and serving windows.

**3.2 Guard labels and joins.** Audit join keys, event-time windows, deduping,
and negative sampling for target leakage and accidental duplication.

**3.3 Test temporal stability.** Use a time-based holdout for systems whose
future differs from the past; do not select only on a random split.

**3.4 Pin preprocessing.** Serialize transforms with the model or version them
under the same release contract.

**3.5 Calibrate uncertainty.** Report confidence or abstain when evaluation
supports it; never imply certainty from an uncalibrated score.

**3.6 Evaluate slices.** Include critical cohorts, rare outcomes, and known
failure modes, with privacy-safe sample sizes.

**3.7 Shadow material changes.** Compare candidate and incumbent predictions
before routing production traffic.

**3.8 Design fallback.** Return the existing safe policy when a model is
missing, stale, malformed, or outside its input contract.

**3.9 Monitor quality and operations.** Track drift, calibration, latency,
errors, saturation, and business outcomes with an owner and alert threshold.

**3.10 Retain rollback.** Keep the prior model, feature schema, and serving
configuration recoverable together.

**3.24 Make evaluation reproducible.** The dataset, code revision, seed, environment, metric, and threshold are recorded together.

**3.25 Monitor data quality separately.** Missingness, stale features, invalid labels, and unexpected cardinality have measurable alerts.

**3.26 Separate candidate traffic.** Shadow predictions and fallback decisions are attributable to a model and schema version.

**3.27 Test model failure.** Missing files, incompatible inputs, dependency outage, and stale artifacts select a safe policy.

**3.28 Review human override.** Manual changes require authorization, a reason, and an audit record distinct from model output.

**3.30 Version training decisions.** Record data, code, features, seed, environment, and metric for every candidate.

**3.31 Monitor quality and operations.** Drift, calibration, latency, errors, cost, and fallback have named thresholds.

**3.32 Test safe fallback.** Missing or stale inputs select a measured baseline without guessing or crashing.

**3.33 Keep model evidence complete.** Record data, code, features, seed, environment, metric, threshold, and artifact digest.

## 4. Domain-Specific Anti-Patterns

### 4.1 Random Split for Future Events

BAD:
```python
train, test = train_test_split(events, random_state=7)
```

GOOD:
```python
cutoff = events["event_time"].quantile(0.8)
train = events[events.event_time < cutoff]
test = events[events.event_time >= cutoff]
```

Evaluation respects decision time.

### 4.2 Serving Transform Omitted

BAD:
```python
model.predict(raw_request)
```

GOOD:
```python
features = pinned_transform.transform(raw_request)
model.predict(features, fallback=baseline)
```

Training and serving transformations are explicit.

### 4.3 Unversioned Model Artifact

BAD:
```bash
aws s3 cp model.bin s3://models/production/model
```

GOOD:
```bash
aws s3 cp model.bin s3://models/v3/data-2026-09/code-a1b2c3
```

The artifact identity carries its compatible versions.

**3.11 Detect feature contract failures.** Reject unknown, missing, or differently typed features at serving time rather than silently imputing them.

**3.12 Track label delay.** A label that becomes available after the prediction window has a separate definition and cannot be used as a premature feature.

**3.13 Compare candidate and baseline.** Every promotion report includes the incumbent, the candidate, a fixed evaluation set, and cost or latency impact.

**3.14 Protect training data.** Apply existing access, retention, and deletion controls to examples, features, prompts, and labels.

**3.15 Test degraded inputs.** Missing features, stale values, extreme values, and dependency outage must select a measured fallback rather than crash or guess.

**3.16 Version data and code.** Training data snapshots and code revisions are jointly recorded so a result can be reproduced or rejected.

**3.17 Define decision thresholds.** Promotion and rollback thresholds state their metric, window, baseline, and owner.

**3.18 Test worst-case inputs.** Include missing, stale, adversarial, extreme, and malformed values at the serving boundary.

**3.19 Separate offline and online loops.** Monitoring does not silently retrain or change a model without the release process and approval.

**3.20 Measure resource limits.** Inference memory, latency, throughput, and dependency cost are checked on the deployed runtime.

**3.21 Preserve human control.** A fallback, pause, or manual override is reachable when model confidence or operations cross the declared threshold.

**3.22 Record prediction latency.** Separate queue, feature, model, dependency, and response time so a regression has an owner.

**3.23 Define safe defaults.** When evaluation or a dependency is unavailable, the system keeps the incumbent or an approved policy.

## 5. Response to Violation

If a prior response violated this layer, identify the leakage, skew,
reproducibility, evaluation, or fallback defect and show the corrected
contract or check. Do not report model quality without an actual evaluation
result.
