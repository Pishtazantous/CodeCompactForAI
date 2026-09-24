---
id: 02-spring-anti-slop
title: "Spring Boot Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Spring Boot Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules remain inherited.

## 1. Spring Boundaries

1. Use the project's Java, Spring Boot, and build conventions.
2. Prefer constructor injection for required collaborators.
3. Keep controllers and REST endpoints at the transport edge.
4. Keep domain rules in services without Spring MVC types.
5. Use Bean Validation for transport shape and range.
6. Use typed configuration with startup validation.
7. Reuse the existing security and exception handlers.
8. Keep JPA entities out of public response DTOs.
9. Register beans through explicit configuration or existing scanning.
10. Keep resources in beans with explicit lifecycle.
11. Use the existing test slice or integration style.
12. Do not add a second persistence or validation framework.
13. Keep the diff limited to the Spring layer.
14. Report assumptions not confirmed from the repository.

## 2. Beans and Scopes

15. Use singleton beans for stateless or synchronized services.
16. Use request scope only for request-local state.
17. Never store current-user data in a singleton.
18. Use qualifiers only when multiple bindings are required.
19. Avoid field injection and service location.
20. Keep bean dependencies acyclic.
21. Use `@Configuration` classes for explicit wiring.
22. Keep bean methods small and named by capability.
23. Use lifecycle callbacks for resources that need cleanup.
24. Do not call a remote service during bean construction.
25. Test scoped and singleton behavior separately.

### 2.1 Mutable Singleton

BAD:
```java
@Service
public class RequestContext {
    private String userId;
}
```

GOOD:
```java
@Service
public class RequestContextService {
    public UserId userId(Principal principal) {
        return new UserId(principal.getName());
    }
}
```

### 2.2 Service Locator

BAD:
```java
@Service
public class OrderService {
    public void place() {
        context.getBean(PaymentGateway.class).charge();
    }
}
```

GOOD:
```java
@Service
public class OrderService {
    public OrderService(PaymentGateway gateway) { this.gateway = gateway; }
    public void place() { gateway.charge(); }
}
```

## 3. Controllers and Annotations

26. Use `@RestController` for JSON and `@Controller` for MVC views consistently.
27. Keep route paths and versions stable.
28. Apply `@Valid` or `@Validated` at the request boundary.
29. Use explicit response DTOs and status codes.
30. Keep exception mapping in `@RestControllerAdvice`.
31. Do not expose stack traces or SQL details.
32. Use method security or the existing authorization policy.
33. Avoid annotation combinations with unclear behavior.
34. Use `@Transactional` only where transaction semantics are understood.
35. Do not wrap long external calls in a transaction.
36. Use `@Async` only with an executor and failure policy.
37. Test validation and security at the endpoint.

### 3.1 Entity Response

BAD:
```java
@GetMapping("/{id}")
public User get(@PathVariable Long id) {
    return userRepository.findById(id).orElseThrow();
}
```

GOOD:
```java
@GetMapping("/{id}")
public UserResponse get(@PathVariable Long id) {
    return userService.findResponse(id);
}
```

## 4. JPA and Hibernate

38. Map entities explicitly and keep lazy loading visible.
39. Use projections or fetch joins to prevent N+1 queries.
40. Keep transactions around persistence operations.
41. Use optimistic locking for concurrent updates.
42. Use database constraints for durable invariants.
43. Keep flush and clear explicit in batch processing.
44. Never serialize lazy proxies directly.
45. Select explicit fields for large queries.
46. Do not call external services from entity callbacks.
47. Keep migrations separate from application code.
48. Add repository and transaction tests.

### 4.1 Lazy Loading in Serialization

BAD:
```java
record UserView(String email, String planName) {}
```

GOOD:
```java
record UserView(String email, String planName) {
    static UserView from(User user) {
        return new UserView(user.getEmail(), user.getPlan().getName());
    }
}
```

## 5. Configuration, Middleware, and Errors

49. Bind configuration to typed options.
50. Validate required properties at startup.
51. Use the established authentication filter chain.
52. Use middleware or filters for request-wide concerns only.
53. Preserve correlation IDs in structured logs.
54. Map domain exceptions centrally.
55. Do not catch `Exception` and return success.
56. Bound connection pools and external timeouts.
57. Make scheduled work idempotent.
58. Protect actuator endpoints when exposed.
59. Keep secrets out of properties and logs.
60. Run the repository build, static checks, and tests.

### 5.1 Hidden Remote Call

BAD:
```java
@PostConstruct
void warmCache() { client.fetchAll(); }
```

GOOD:
```java
@PostConstruct
void configure() { client.setTimeout(Duration.ofSeconds(2)); }
```

## Domain-Specific Anti-Patterns

### A. Field Injection

BAD:
```java
@Service
public class UserService {
    @Autowired private UserRepository repository;
}
```

GOOD:
```java
@Service
public class UserService {
    public UserService(UserRepository repository) { this.repository = repository; }
}
```

### B. Entity as DTO

BAD:
```java
public record UserResponse(User user) {}
```

GOOD:
```java
public record UserResponse(String id, String email) {}
```

### C. Transaction Around Remote I/O

BAD:
```java
@Transactional public void pay() { gateway.charge(); order.save(); }
```

GOOD:
```java
public void pay() { gateway.charge(); repository.save(order); }
```

## 6. Response to Violation
1. Name the Spring bean or persistence boundary and preserve its contracts.
2. Add a focused test and run the repository formatter, analyzer, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
