---
id: 02-observability-anti-slop
title: "Observability Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: concern
version: 1
---
# Observability Anti-Slop Layer
Layered under `_universal/00-master-anti-slop.md`. Universal rules and
general security prohibitions on sensitive data are not repeated here.
This layer requires evidence that production behavior can be explained
without adding noise to the logging baseline.
## 1. Applicability
Send this layer when a change affects any of these surfaces:
- a deployed service, worker, job, or long-running process;
- an operational interface such as metrics, traces, dashboards, or
  alerts;
- error paths, latency-sensitive flows, queues, or external dependencies;
- shared infrastructure where local diagnosis needs production context;
- a release whose failure would be invisible until a user reports it.
A static content build or isolated local utility may use the logging
baseline without this layer. If a change adds no signals, no dashboards,
and no production dependency, do not manufacture telemetry.
## 2. Observability Contract
### 2.1 Start With an Operational Question
1. State the failure or decision the signal must support.
2. Name the service boundary and user-visible consequence.
3. Choose the narrowest signal that can answer the question.
4. Define expected ownership, retention, and access needs.
5. Reject a signal that has no query, dashboard, alert, or investigation
   workflow attached to it.
Instrumentation without a use is cost without diagnostic value.
### 2.2 Correlate Without Coupling
1. Propagate a stable request, job, or trace identifier across boundaries.
2. Add only high-value domain dimensions to logs and traces.
3. Use metrics for aggregates and traces for individual delayed paths.
4. Keep identifiers bounded and compliant with the logging baseline.
5. Do not use a trace as a request dump or a metric as a log archive.
## 3. Logging Baseline References
### 3.1 Inherit the Project's Logging Rules
1. Use the logging baseline in the active delivery and language layers.
2. Use the repository's configured logger, not an ad hoc console sink.
3. Preserve structured fields and established level semantics.
4. Apply the baseline redaction rules to every new field.
5. Do not introduce a second logger, formatter, or sink.
The baseline governs logger selection, level choice, context fields,
redaction, and production output. This layer adds correlation,
diagnostic value, cardinality control, and cross-signal use.
### 3.2 Useful Event Fields
1. Include the stable event name or code, not a novel sentence per call.
2. Include outcome, duration, and relevant bounded dimensions.
3. Include correlation, trace, and deployment identifiers when available.
4. Record errors with the project's error serializer and cause chain.
5. Log the decision or transition, not every internal function call.
### 3.3 Safe Logging
1. Never log credentials, tokens, session values, or raw payment data.
2. Treat personal data and tenant content as fields requiring an explicit
   policy decision.
3. Sanitize user-controlled line breaks before emitting text.
4. Bound the size of message fields and child collections.
5. Use opaque identifiers instead of email addresses when identity is not
   required for the investigation.
## 4. Metrics
### 4.1 Instrument a Service Contract
1. Measure request rate, errors, and duration for synchronous entry points.
2. Measure queue depth, age, processing duration, and dead-letter outcomes
   for asynchronous work.
3. Count business transitions when operators act on them.
4. Use histograms or distributions when latency tails matter.
5. Record saturation for bounded pools, workers, and external clients.
### 4.2 Control Cardinality
1. Do not use raw user, request, order, or error messages as labels.
2. Bound route templates rather than complete paths.
3. Allowlist status families and error categories.
4. Remove labels with unbounded or rarely useful values.
5. Review a metric's label set before publishing or renaming it.
High-cardinality telemetry can make a monitoring system the outage.
### 4.3 Rate Calculations
1. State the counter and window in dashboard and alert definitions.
2. Avoid dividing cumulative counters without a defined reset policy.
3. Define zero-denominator behavior for rate calculations.
4. Separate workload changes from service failures in interpretation.
5. Compare rates only over equivalent windows and comparable traffic.
## 5. Traces
### 5.1 Trace Valuable Boundaries
1. Propagate trace context across supported network and queue boundaries.
2. Create spans for remote calls, queues, database operations, and
   expensive computation where duration explains failure.
3. Name spans with stable, low-cardinality operations.
4. Attach relevant error status, retry count, and bounded attributes.
5. Sample according to risk and policy, not randomly without a reason.
### 5.2 Use Traces Deliberately
1. Use a trace to follow one slow or failed operation across services.
2. Use metrics to detect that a population is affected.
3. Use logs for detailed local evidence within the trace window.
4. Do not add tracing to every internal function by default.
5. Do not place request bodies, secrets, or large payloads in span attributes.
A trace is sampled evidence, not a complete audit log.
## 6. SLOs
### 6.1 Define User-Centered Indicators
1. Choose a service-level indicator tied to user-visible reliability.
2. Define the measurement window, population, and valid event.
3. State whether the contract is availability, latency, correctness,
   freshness, or another measurable property.
4. Exclude planned maintenance only when the policy defines it.
5. Record the owner and the decision enabled by each SLO.
### 6.2 Error Budgets
1. Set a target from product and operational constraints, not aspiration.
2. Define allowed-error-rate and burn thresholds.
3. Use multi-window burn alerts for fast and slow consumption.
4. Connect budget exhaustion to a decision, such as release freeze or
   reliability work.
5. Review unreliable indicators before using them to block changes.
An SLO without an operational decision is documentation.
## 7. Alerts
### 7.1 Alert on User-Conditioned Symptoms
1. Prefer pages for urgent, actionable user-impact conditions.
2. Use ticket or dashboard signals for investigation that can wait.
3. Include the affected service, scope, threshold, and runbook in the
   alert definition.
4. Make alerts deduplicated and routed to an owning team.
5. Test alert delivery through controlled exercises.
### 7.2 Prevent Alert Fatigue
1. Every alert must justify why immediate human action is required.
2. Remove alerts that duplicate another signal without adding urgency.
3. Tune noisy thresholds after cause analysis, not by arbitrary delay.
4. Group related symptoms to avoid a storm from one incident.
5. Track acknowledgement, resolution, and false-positive outcomes.
Repeated pages are evidence that the alert design is wrong. Silencing an
alert without a new decision is not a repair.
## 8. Domain-Specific Rules
### 8.1 Observability Rules
1. Define the operational question before adding a signal.
2. Follow the active delivery and language logging baselines.
3. Add structured logs, bounded metrics, and useful traces according to
   failure mode.
4. Define SLOs from user-visible indicators and connect alerts to action.
5. Review cardinality, noise, and alert outcomes as production costs.
6. Correlate signals without copying payloads between them.
## Domain-Specific Anti-Patterns
### 9.1 Request Payload Logging
BAD:
```javascript
console.log("request received", request);
```
The request dump bypasses bounded fields and the project logger.
GOOD:
```javascript
logger.info({
  event: "request.received",
  requestId: context.requestId,
  route: "orders.create",
});
```
The logger records bounded, structured diagnostic context.
### 9.2 Unbounded Metric Labels
BAD:
```python
metrics.increment("requests", labels={"path": request.full_path, "user": user.email})
```
Full paths and email addresses create unbounded label cardinality.
GOOD:
```python
metrics.increment(
    "requests",
    labels={"route": "orders.create", "status": "2xx"},
)
```
Route and status dimensions keep the time-series count bounded.
### 9.3 Trace Everything and Store Payloads
BAD:
```python
with tracer.start_as_current_span("handle_order") as span:
    span.set_attribute("request.body", str(request.json()))
    process_order(request)
```
Request bodies and customer data create unsafe span attributes.
GOOD:
```python
with tracer.start_as_current_span("order.submit") as span:
    span.set_attribute("order.id", order.id)
    span.set_attribute("order.item_count", len(order.items))
    process_order(order)
```
The trace carries stable, non-sensitive operation context.
### 9.4 Percentage Alerts Without Windows
BAD:
```yaml
alert: HighErrorRate
expr: failed_requests / total_requests > 0.01
for: 0m
```
A single sample without a window creates noisy pages.
GOOD:
```yaml
alert: FastBurn
expr: error_ratio_5m > 14.4 * 0.001
for: 2m
labels:
  severity: page
annotations:
  runbook: order-submit-reliability
```
The alert connects a measured window to severity and an operational action.
### 9.5 Metrics as Logs
BAD:
```javascript
logger.info(`processing order ${order.id}`);
logger.info(`processing item ${item.id}`);
```
One event per object makes aggregation and storage expensive.
GOOD:
```javascript
metrics.increment("orders.submitted");
logger.info({ event: "order.submitted", orderId: order.id });
```
Metrics aggregate the population while one event records the transition.
## 10. Response to Violation
If a previous response violated this layer:
```text
In the previous response, [specific observability rule] was violated. Correction:
[bounded, actionable signal or configuration]
```
State the affected SLO or investigation path when known. Do not add
more telemetry while removing a violation.
