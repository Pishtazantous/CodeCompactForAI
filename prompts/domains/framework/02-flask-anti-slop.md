---
id: 02-flask-anti-slop
title: "Flask Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Flask Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`, the architecture layer, and `domains/delivery/02-backend-anti-slop.md`. General backend rules remain inherited.

## 1. Factory and Blueprints

1. Use the application factory already present in the project.
2. Initialize extensions once through the factory.
3. Register each blueprint once with a unique name and prefix.
4. Keep route handlers short and resource-oriented.
5. Keep templates beside the blueprint or in the established template package.
6. Import blueprints through public route modules.
7. Use the existing validator and error handler.
8. Keep configuration in the project settings module.
9. Keep application setup separate from request handling.
10. Use teardown or shutdown hooks for request resources.
11. Do not initialize an extension at module import time.
12. Keep test configuration built through the factory.
13. Do not add a second web framework.
14. Keep URL converters explicit and bounded.
15. Use the established response envelope.

### 1.1 Global Database Engine

BAD:
```python
engine = create_engine(DATABASE_URL)
```

GOOD:
```python
def create_app():
    app.extensions['db'] = Database(engine)
    return app
```

### 1.2 Blueprint Factory Leak

BAD:
```python
@users_bp.route('/<int:id>')
def show(id):
    return str(queries.load(id))
```

GOOD:
```python
@users_bp.get('/<int:user_id>')
def show(user_id):
    return jsonify(queries.load_user(user_id))
```

## 2. Request and Context

16. Use `current_app` for configuration, not domain state.
17. Do not retain request data on the application object.
18. Keep request-scoped sessions in the request lifecycle.
19. Use `g` only for request-local values with a clear owner.
20. Do not retain a context beyond the request or test context.
21. Validate JSON, form, query, path, and cookie input.
22. Reject unknown fields when the API contract is closed.
23. Use safe redirect targets from a local allowlist.
24. Keep CSRF protection enabled for cookie-authenticated writes.
25. Use explicit status codes.
26. Return one response for each branch.
27. Do not call a database from a template.
28. Keep Jinja autoescaping enabled.
29. Avoid the `safe` filter on untrusted content.
30. Preserve the existing error renderer.

### 2.1 Template Query

BAD:
```html
{% for order in user.orders.all() %}
```

GOOD:
```html
{% for order in orders %}
```

### 2.2 Application State

BAD:
```python
app.config['CURRENT_USER'] = user
```

GOOD:
```python
g.current_user = authenticate(request)
```

## 3. Extensions and Lifecycle

31. Give every extension an application and teardown owner.
32. Use extension initializers in the factory.
33. Do not create a second engine inside a blueprint.
34. Close connections and clients on teardown.
35. Avoid network calls during factory construction.
36. Register CLI commands through the extension owner.
37. Keep request-local state out of extension globals.
38. Use the project logger and correlation mechanism.
39. Map exceptions centrally.
40. Do not expose internal messages in JSON errors.
41. Keep upload paths and filenames validated.
42. Bound request body and upload sizes.
43. Use pagination for collection endpoints.
44. Test factory, blueprint, extension, and teardown behavior.

### 3.1 Import-Time Initialization

BAD:
```python
mail = Mail()
mail.init_app(app)
```

GOOD:
```python
def create_app():
    app = Flask(__name__)
    mail.init_app(app)
    return app
```

## 4. Persistence and Errors

45. Use the existing ORM or query layer.
46. Select explicit fields in large queries.
47. Eager load relationships needed by a response.
48. Use transactions for multi-write operations.
49. Keep external services behind adapters.
50. Do not catch `Exception` and return success.
51. Keep authorization explicit on resource operations.
52. Use the project response status convention.
53. Preserve correlation IDs in safe logs.
54. Do not log credentials or full request bodies.
55. Validate required configuration at startup.
56. Keep redirects within a trusted path set.
57. Test invalid, missing, unauthorized, and not-found paths.
58. Keep the diff limited to Flask boundaries.
59. Report unverified runtime assumptions.
60. Run project checks after editing.

### 4.1 Swallowed Error

BAD:
```python
try:
    create_order(data)
except Exception:
    return jsonify({'ok': True})
```

GOOD:
```python
try:
    order = create_order(data)
except OrderError as exc:
    return handle_domain_error(exc)
```

## Domain-Specific Anti-Patterns

### A. Shared Extension Global

BAD:
```python
mail.messages = []
```

GOOD:
```python
def enqueue_welcome(user_id):
    queue.enqueue('welcome', user_id)
```

### B. Unbounded Collection

BAD:
```python
@users_bp.get('/')
def index():
    return jsonify([user.to_dict() for user in User.query.all()])
```

GOOD:
```python
@users_bp.get('/')
def index():
    return jsonify(paginate(User.query))
```

### C. Database Owned by Blueprint

BAD:
```python
def list_users(): return jsonify(User.query.all())
```

GOOD:
```python
def list_users(): return jsonify(UserRepository.page(limit=50))
```

## 6. Response to Violation
1. Name the Flask factory or blueprint boundary and preserve its contracts.
2. Add a focused test and run the repository formatter, linter, and tests.
3. Report unverified assumptions; change no unrelated files and create no commit.
