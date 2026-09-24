---
id: 02-llm-system-anti-slop
title: "LLM System Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 1
---
# LLM System Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules are not
repeated. Security controls use the related security layer.

## 1. Stack Assumptions

**1.1 Define the model boundary.** Identify provider or local model, model
version, context policy, tool permissions, data residency, and latency tier.

**1.2 Separate prompt from policy.** Treat system instructions, retrieved
content, user text, and tool output as distinct trust zones.

**1.3 Follow the existing client.** Reuse the repository's provider adapter,
retrieval, tracing, caching, and streaming abstractions.

## 2. Domain Contracts

**2.1 Untrusted text is data.** Instructions found in retrieved documents or
tool output cannot override system policy or tool permissions.

**2.2 Output is untrusted.** Validate model output against the required
schema before actions, SQL, HTML, or tool calls consume it.

**2.3 Budget every call.** Set input, output, retrieval, tool, retry, and
latency limits. A loop must have a hard termination condition.

**2.4 Tool calls are authorized.** Allowlist tools, validate arguments again
at execution, and keep user confirmation for consequential actions.

**2.5 Fail closed on uncertainty.** Use a bounded fallback, safe refusal, or
human path when the model or dependency fails.

## 3. Domain-Specific Rules

**3.1 Pin prompts and model settings.** Version system instructions, model,
temperature settings, tokenizer assumptions, and tool schemas.

**3.2 Minimize context.** Retrieve only authorized, relevant content and
record the source identifiers without exposing private data unnecessarily.

**3.3 Evaluate before release.** Maintain representative cases for refusal,
injection, tool misuse, groundedness, format compliance, and task success.

**3.4 Bound streaming.** Flush partial output, stop on cancellation, limit
buffer size, and distinguish a complete response from a truncated stream.

**3.5 Handle provider failure.** Retry only transient, idempotent operations;
honor rate limits and use a compatible fallback when configured.

**3.6 Redact telemetry.** Logs and traces include request IDs and safe
metadata, not raw secrets, private documents, or unnecessary prompts.

**3.7 Control tool loops.** Track calls, elapsed time, token spend, and
permissions per request. Never allow an agent to grant itself authority.

**3.8 Make output typed.** Require structured output where possible and
reject invalid types, extra fields, and ambiguous references.

**3.9 Test adversarial boundaries.** Include indirect injection, encoded
instructions, poisoned retrieval, malformed tool output, and long context.

**3.10 Provide user-visible status.** A fallback, refusal, or incomplete
answer is not presented as a confident complete result.

**3.24 Define completion states.** Separate complete, cancelled, truncated, refused, failed, and fallback responses.

**3.25 Enforce output boundaries.** Validate structured fields and action parameters before they reach business code.

**3.26 Keep context minimal.** Remove irrelevant or unauthorized content before each model call and preserve only safe lineage.

**3.27 Test hostile tool output.** Tool results, retrieved text, and encoded user content remain data even when they contain instructions.

**3.28 Bound recovery.** Retry only safe transient work and preserve cancellation, budget, and authorization state.

**3.30 Validate model boundaries.** Typed output, tool arguments, and completion state are checked before business use.

**3.31 Bound context and tools.** Retrieval, tool results, retries, tokens, time, and call count have explicit limits.

**3.32 Preserve safe recovery.** Cancellation, provider failure, and authorization loss stop work and select a declared fallback.

**3.33 Keep model evidence safe.** Record versions, budgets, tool calls, and outcomes without prohibited prompt content.

## 4. Domain-Specific Anti-Patterns

### 4.1 Retrieved Text as Instruction

BAD:
```python
answer = model(f"Document: {retrieved}\nAnswer: {question}")
```

GOOD:
```python
answer = model(system=policy, context=retrieved, query=question)
```

Retrieved content is untrusted context, not authority.

### 4.2 Unbounded Agent Loop

BAD:
```python
while True:
    result = run_tool(plan.next())
```

GOOD:
```python
for _ in range(MAX_TOOL_STEPS):
    if plan.is_complete():
        break
    plan.step(run_tool(plan.next()))
```

The request has a hard resource boundary.

### 4.3 Parsing a Partial Stream as Final

BAD:
```python
result = json.loads(stream_text)
```

GOOD:
```python
result = parse_complete_response(stream_with_termination)
```

Only a completed, validated response becomes an action.

**3.11 Separate model and application logs.** Correlate model calls with request IDs, token counts, latency, and outcome without recording unnecessary prompt content.

**3.12 Define refusal behavior.** A refusal, low-confidence result, and provider error are distinct states with appropriate UI and automation behavior.

**3.13 Make retrieval access-aware.** Apply document permissions before retrieval and again when a selected passage would be exposed.

**3.14 Version tool schemas.** Tool names, required fields, and authorization semantics change through the same compatibility review as application APIs.

**3.15 Test cancellation.** Stop generation, close streams, release reservations, and avoid billing or side effects after a cancelled request.

**3.16 Bound tool results.** Truncate, summarize, or reject oversized tool output before it enters the next model context.

**3.17 Keep citations authoritative.** A citation or retrieval result is not a fact until the application checks its source and scope.

**3.18 Rate limit by authority.** Apply quotas to the authenticated user or workload, not only to an untrusted client identifier.

**3.19 Test multilingual and encoded input.** Verify policy, normalization, token budgets, and output validation for supported languages and encodings.

**3.20 Isolate evaluation data.** Keep private, recent, or adversarial cases out of training and tune only from declared evaluation splits.

**3.21 Make incidents diagnosable.** Record model, prompt, tool, retrieval, and fallback versions without recording prohibited content.

**3.22 Define safe defaults.** When evaluation or a dependency is unavailable, the system keeps a bounded refusal or approved non-LLM path.

**3.23 Record response completeness.** Mark truncated, cancelled, and fallback responses so automation never treats them as complete.

## 5. Response to Violation

If a prior response violated this layer, name the trust-zone, evaluation,
budget, tool, streaming, or fallback issue and show the corrected boundary.
Do not expose sensitive prompts or claim evaluations were run without evidence.
