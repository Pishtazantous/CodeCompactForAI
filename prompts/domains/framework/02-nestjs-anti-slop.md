---
id: 02-nestjs-anti-slop
title: "NestJS Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# NestJS Anti-Slop Layer

Layered under the master, architecture, and backend layers. This file adds
rules for Nest modules, providers, dependency injection, guards, interceptors,
pipes, controllers, and application boundaries.

## 1. Stack Assumptions

1. Read the installed Nest major version before using version-specific APIs.
2. Use the repository's module style and bootstrap configuration.
3. Keep controllers thin and application services responsible for orchestration.
4. Treat the module graph as an explicit dependency contract.
5. Register cross-cutting providers in one deliberate place.
6. Do not add a second HTTP framework or DI container.
7. Keep domain rules independent from Nest decorators and request objects.
8. Match the repository's transport and persistence adapters.

## 2. Modules and Providers

1. A module owns a cohesive capability, not a folder of unrelated classes.
2. Export providers only when another module needs their public contract.
3. Use `forwardRef` only after proving a real circular dependency and
   documenting the better boundary to remove.
4. Keep module imports shallow; prefer explicit capability modules.
5. Register providers with the narrowest scope that satisfies their consumers.
6. Do not mark every provider as global by default.
7. Keep module initialization side effects explicit and idempotent.
8. Do not use a module as a generic service locator.
BAD:

```ts
@Module({ providers: [UserService, OrderService, EmailService], exports: [UserService] })
export class AppModule {}
```

GOOD:

```ts
@Module({
  imports: [UserModule, OrderModule],
  providers: [AppMailer],
})
export class AppModule {}
```

## 3. Dependency Injection

1. Inject an interface or token rather than a concrete external client where a
   boundary is needed.
2. Constructor injection is the default for providers.
3. Property injection is reserved for an existing framework requirement.
4. Use explicit factory providers for configuration and third-party clients.
5. Do not create clients inside request handlers.
6. Make provider lifetime match resource ownership.
7. Do not use `forwardRef` to conceal an import cycle.
8. Test the container with a focused unit test and an integration test for wiring.

BAD:

```ts
@Injectable()
export class UsersService {
  createDbClient() { return new Database(process.env.DATABASE_URL); }
}
```

GOOD:

```ts
@Injectable()
export class UsersService {
  constructor(private readonly db: Database) {}
}
```

## 4. Controllers and Routes

1. Controllers perform transport mapping, validation orchestration, and calls to
   application services.
2. Keep SQL, business rules, and queue implementation out of controllers.
3. Use explicit HTTP status codes and return DTOs, not database entities.
4. Validate route params, query values, and bodies at the boundary.
5. Avoid business conditionals in a controller.
6. Use route params only after validation and authorization.
7. Keep endpoint names stable and consistent with the domain language.
8. Do not return internal errors or stack traces.
9. Test authentication, authorization, validation, and not-found cases.

BAD:

```ts
@Get(":id")
async find(@Param("id") id: string) {
  return this.db.query(`select * from users where id = ${id}`);
}
```

GOOD:

```ts
@Get(":id")
async find(@Param("id", ParseUUIDPipe) id: string) {
  const user = await this.users.findOne(id);
  if (!user) throw new NotFoundException("User not found");
  return user;
}
```

## 5. Guards, Interceptors, and Pipes

1. Use guards for authorization and request context that must happen before a
   handler.
2. Use pipes for transformation and validation of handler inputs.
3. Use interceptors for response mapping, logging, metrics, and cross-cutting
   async behavior.
4. Keep one concern per guard, pipe, or interceptor.
5. Make ordering explicit when several cross-cutting providers apply.
6. Do not perform database writes in a guard.
7. Do not hide authorization in a generic interceptor.
8. Return stable error shapes and preserve correlation identifiers.
9. Clean up resources created by interceptors.

BAD:

```ts
@UseGuards(AuthGuard)
@UseInterceptors(DatabaseInterceptor)
@Post()
create(@Body() body: CreateUserDto) { return this.users.create(body); }
```

GOOD:

```ts
@UseGuards(AuthGuard)
@UsePipes(ValidationPipe)
@Post()
create(@Body() body: CreateUserDto) { return this.users.create(body); }
```

## 6. Modules and Lifecycle

1. Keep bootstrap configuration separate from feature modules.
2. Use `onModuleInit` and `onModuleDestroy` only for resource ownership.
3. Do not perform network or database calls in a constructor.
4. Make shutdown idempotent and release pools, queues, and subscriptions.
5. Avoid ambient request state; use request-scoped providers only when needed.
6. Do not make a stateless provider request-scoped without a concrete reason.
7. Validate configuration and report failures before accepting traffic.

## 7. Error Handling and Boundaries

1. Translate infrastructure errors into stable application errors.
2. Use an exception filter only for a real cross-cutting error contract.
3. Do not expose internal messages, paths, or stack traces.
4. Log once at the owning boundary, not once per layer.
5. Preserve correlation IDs through synchronous and asynchronous work.
6. Map domain failures to HTTP semantics explicitly.
7. Ensure an unhandled failure cannot leave a transaction open.
8. Test error filters without coupling tests to implementation details.

BAD:

```ts
try { return await this.repository.save(input); }
catch (error) { return { error }; }
```

GOOD:

```ts
try { return await this.repository.save(input); }
catch (error) { this.logger.error({ error, correlationId }); throw new ConflictException(); }
```

## 8. Domain-Specific Anti-Patterns

### 9.1 Controller God Object

BAD:

```ts
@Controller("orders")
export class OrdersController {
  find() {}
  create() {}
  refund() {}
  audit() {}
}
```

GOOD:

```ts
@Controller("orders")
export class OrdersController {
  constructor(private readonly orders: PlaceOrder) {}
  @Post() create(@Body() body: CreateOrderDto) { return this.orders.execute(body); }
}
```

### 9.2 Service Locator Injection

BAD:

```ts
constructor(private readonly moduleRef: ModuleRef) {}
```

GOOD:

```ts
constructor(private readonly users: UserReader) {}
```

### 9.3 Side Effects in Constructors

BAD:

```ts
constructor() { this.registry.sendHeartbeat(); }
```

GOOD:

```ts
async onModuleInit() { await this.registry.register(this.serviceName); }
async onModuleDestroy() { await this.registry.unregister(this.serviceName); }
```

## 10. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

State the rule and the corrected boundary. Do not add unrelated commentary.
