---
id: 02-rails-anti-slop
title: "Ruby on Rails Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Ruby on Rails Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules remain inherited.

## 1. Rails Conventions

1. Use the project's Rails, Ruby, and test conventions.
2. Prefer resources, strong parameters, and model validation already in use.
3. Keep controllers focused on HTTP coordination and authorization.
4. Use services for workflows spanning records and external systems.
5. Keep Active Record concerns focused and named by capability.
6. Keep views and helpers presentation-only.
7. Use the established error and authentication handling.
8. Keep credentials and environment configuration out of code.
9. Keep routes and controller names aligned with the resource.
10. Use existing component or engine boundaries.
11. Do not create a parallel service tree for one feature.
12. Reuse shared helpers only when the project already has them.
13. Keep tests close to the behavior they verify.
14. Do not add gems without explicit approval.

## 2. Active Record

15. Use `find` when absence must raise.
16. Use `find_by` when absence is an expected branch.
17. Select explicit fields for sensitive and large queries.
18. Use joins or preload to prevent N+1 queries.
19. Use transactions for multi-record writes.
20. Use constraints for invariants outside callbacks.
21. Use `update!` when failure must stop work.
22. Keep scopes composable and free of hidden writes.
23. Do not call external services from a model getter.
24. Do not make model callbacks the workflow owner.
25. Keep lazy associations explicit in serializers and views.
26. Add query-count tests for collection endpoints.
27. Avoid `save!` with unrelated attributes.
28. Keep optimistic locking behavior explicit.

### 2.1 N+1 Query

BAD:
```ruby
orders.map { |order| order.customer.email }
```

GOOD:
```ruby
Order.includes(:customer).map { |order| order.customer.email }
```

### 2.2 Hidden Callback Side Effect

BAD:
```ruby
after_create :send_welcome_email
```

GOOD:
```ruby
after_create_commit :enqueue_welcome_email
```

## 3. Controllers and Views

29. Use strong parameters at the action boundary.
30. Authorize the record and action, not only the route.
31. Return an explicit HTML or JSON response.
32. Set status codes for non-default outcomes.
33. Keep redirects within trusted local paths.
34. Use the established flash and error format.
35. Pass explicit locals to partials.
36. Avoid database calls in helpers and views.
37. Do not mutate records from a template.
38. Keep form objects for multi-step input.
39. Protect cookie-authenticated writes with CSRF.
40. Keep view and API action behavior separate.
41. Test missing and unauthorized records.

### 3.1 Unsafe View Helper

BAD:
```ruby
def user_link(user)
  link_to user.email, user_path(user) + params[:next].to_s
end
```

GOOD:
```ruby
def user_link(user)
  link_to user.email, user_path(user)
end
```

## 4. Callbacks and Jobs

42. Keep callbacks local and deterministic.
43. Keep before-save callbacks free of network I/O.
44. Make callback order explicit.
45. Use callbacks for model invariants, not orchestration.
46. Use after-commit delivery for external effects.
47. Make jobs idempotent and retryable.
48. Do not assume a job runs once.
49. Keep job arguments minimal and serializable.
50. Use the existing queue adapter.
51. Bound retries and payload size.
52. Do not enqueue required work without handling failure.
53. Test callback rollback and job retry.
54. Keep external work out of transactions.

### 4.1 Callback Work

BAD:
```ruby
after_update :deliver_invoice
```

GOOD:
```ruby
after_update_commit :enqueue_invoice
```

## 5. Middleware, Errors, and Operations

55. Use middleware for request-wide concerns.
56. Keep authorization in policies or the established security layer.
57. Map exceptions through the central handler.
58. Do not expose Active Record errors or stack traces.
59. Preserve correlation IDs in structured logs.
60. Use transactions around required writes.
61. Keep external calls behind adapters.
62. Validate configuration during boot.
63. Keep secrets in credentials or the project secret store.
64. Use pagination for collection responses.
65. Keep migrations separate from application behavior.
66. Do not use a global model variable.
67. Test error, auth, and transaction paths.
68. Run project checks after editing.
69. Keep the diff limited to Rails.
70. Report unverified assumptions.

### 5.1 Broad Error Rescue

BAD:
```ruby
rescue StandardError
  head :ok
end
```

GOOD:
```ruby
rescue OrderError => error
  render_error(error)
end
```

## Domain-Specific Anti-Patterns

### A. Fat Controller

BAD:
```ruby
def create
  ActiveRecord::Base.transaction do
    order = Order.create!(order_params)
    charge(order)
    redirect_to order
  end
end
```

GOOD:
```ruby
def create
  order = Orders::Create.call(order_params, current_user)
  redirect_to order
end
```

### B. Unscoped Relation

BAD:
```ruby
def show
  @order = Order.find(params[:id])
end
```

GOOD:
```ruby
def show
  @order = current_user.orders.find(params[:id])
end
```

### C. External I/O in Active Record

BAD:
```ruby
def deliver; HTTParty.post(payment_url, body: amount); end
```

GOOD:
```ruby
def deliver; PaymentGateway.new.charge(self); end
```

## 6. Response to Violation
1. Name the Rails boundary and preserve its authorization, response, and error contracts.
2. Add a focused test and run the repository formatter, linter, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
