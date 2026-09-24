---
id: 02-django-anti-slop
title: "Django Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Django Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules are inherited.

## 1. Django Boundaries

1. Inspect the URLconf, views, forms, models, migrations, and settings before editing.
2. Keep views responsible for HTTP coordination and authorization.
3. Use forms for browser input and serializers for API input.
4. Keep templates free of persistence and business decisions.
5. Use model validation for model-owned invariants.
6. Use services for workflows that span several models or external systems.
7. Keep settings in the existing settings module.
8. Reuse the central exception and logging behavior.
9. Keep migrations in the app that owns the model.
10. Colocate tests with the app or established test package.
11. Import other apps through public modules.
12. Keep management commands small and explicit.
13. Do not create a second ORM or validator.
14. Prefer the existing class-based or function-based style.
15. Keep URL modules thin and route names stable.

## 2. ORM and Transactions

16. Use `get()` when absence must raise.
17. Use `filter().first()` only when absence is expected.
18. Select explicit fields in sensitive or large queries.
19. Use `select_related` for foreign keys.
20. Use `prefetch_related` for reverse relations.
21. Avoid queries in loops and templates.
22. Keep `get_or_create` semantics visible at the caller.
23. Use `update_or_create` only with a stable uniqueness boundary.
24. Wrap multi-write operations in `transaction.atomic()`.
25. Use `select_for_update` when a read must precede a write.
26. Keep database constraints aligned with model validation.
27. Avoid queries from `__str__`, properties, and model getters.
28. Do not call external services during query evaluation.
29. Keep lazy relations explicit in services and serializers.
30. Add query-count tests for list and detail views.

### 2.1 N+1 Query

BAD:
```python
orders = Order.objects.all()
return [order.customer.email for order in orders]
```

GOOD:
```python
orders = Order.objects.select_related('customer')
return [order.customer.email for order in orders]
```

### 2.2 Non-Atomic Workflow

BAD:
```python
order = Order.objects.create(customer=customer, total=total)
LedgerEntry.objects.create(order=order, amount=total)
```

GOOD:
```python
with transaction.atomic():
    order = Order.objects.create(customer=customer, total=total)
    LedgerEntry.objects.create(order=order, amount=total)
```

## 3. Views, Forms, and Templates

31. Validate a form before calling a service.
32. Use `get_object_or_404` for required objects.
33. Authorize the object for ownership-sensitive actions.
34. Use POST for state-changing browser operations.
35. Preserve CSRF and secure-cookie settings.
36. Pass a bounded context to templates.
37. Use template autoescaping for untrusted content.
38. Never apply `safe` to user-controlled HTML.
39. Keep redirects to trusted local paths.
40. Use explicit JSON error shapes for API views.
41. Keep API and HTML view behavior distinct.
42. Do not call `save()` from a template.
43. Keep form objects small and named for the workflow.
44. Return a response for every branch.
45. Do not catch an exception and return success.

### 3.1 Unsafe Template Output

BAD:
```html
{{ comment.body|safe }}
```

GOOD:
```html
{{ comment.body }}
```

### 3.2 Validation Bypass

BAD:
```python
def update(request, pk):
    User.objects.filter(pk=pk).update(**request.POST.dict())
```

GOOD:
```python
form = UserForm(request.POST, instance=get_object_or_404(User, pk=pk))
if form.is_valid():
    form.save()
```

## 4. Signals

45. Register custom receivers during app initialization.
46. Keep receiver functions small and named.
47. Delegate work to an explicit service.
48. Make receivers idempotent for repeated events.
49. Test sender, payload, and failure behavior.
50. Avoid circular signal chains.
51. Do not make a signal the only required business step.
52. Use transaction-aware delivery for external notifications.
53. Keep signal documentation next to the receiver.
54. Do not connect the same receiver repeatedly.
55. Keep pre-save callbacks local and deterministic.
56. Avoid network calls in model callbacks.

### 4.1 Hidden Notification

BAD:
```python
post_save.connect(send_welcome, sender=User)
```

GOOD:
```python
def enqueue_welcome(sender, instance, **kwargs):
    enqueue_welcome_email(instance.pk)
```

## 5. Migrations and Operations

57. Generate a migration for every schema change.
58. Review generated operations before applying them.
59. Keep data migrations explicit and bounded.
60. Add indexes with the model change.
61. Do not call live services from `RunPython`.
62. Make destructive changes reversible where practical.
63. Test migrations on the supported database engine.
64. Keep fixtures deterministic and free of secrets.
65. Validate required settings at startup.
66. Do not commit local settings files.
67. Keep query and response errors redacted.
68. Preserve request correlation in logs.
69. Do not expose SQL or filesystem paths.
70. Add a regression test for every fixed view or model.

### 5.1 Migration Side Effect

BAD:
```python
def forwards(apps, schema_editor):
    external_client.fetch()
```

GOOD:
```python
def forwards(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.filter(status='new').update(status='pending')
```

## Domain-Specific Anti-Patterns

### A. Query in Template

BAD:
```html
{% for order in request.user.order_set.all %}
```

GOOD:
```html
{% for order in orders %}
```

### B. Signal as Workflow Owner

BAD:
```python
post_save.connect(create_invoice, sender=Invoice)
```

GOOD:
```python
def create_invoice(invoice):
    with transaction.atomic():
        InvoiceLine.objects.bulk_create(invoice.lines)
```

### C. Query Hidden in a Signal

BAD:
```python
post_save.connect(lambda order: ExternalClient.create(order.pk), sender=Order)
```

GOOD:
```python
def enqueue_order_created(order_id): ExternalQueue.publish(order_id)
```

## 6. Response to Violation
1. Name the Django app boundary and preserve its validation, error, and response contracts.
2. Add a focused test and run the repository formatter, linter, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
