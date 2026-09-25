---
id: 02-nestjs-anti-slop
title: "NestJS Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-backend-anti-slop]
category: domain
domain_type: framework
version: 2
---

# NestJS Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`, and
`domains/delivery/02-backend-anti-slop.md`. Rules already covered in
those files are NOT repeated here.

This file covers rules specific to NestJS: modules, providers,
decorators, guards, interceptors, pipes, exception filters, and the
framework's dependency injection model. It does NOT cover
framework-agnostic backend rules (see `02-backend-anti-slop.md`),
architecture rules (see `02-architecture-anti-slop.md`), TypeScript
rules (see `02-typescript-anti-slop.md`), or database rules in
detail (see `02-database-anti-slop.md`).

NestJS provides structure through decorators and dependency
injection. The structure is a strength when used as designed, and a
liability when bypassed. Every rule here reinforces the design.

## 1. Stack Assumptions

This layer assumes:

- NestJS 10 or later.
- TypeScript strict mode.
- Express or Fastify adapter (the rules do not depend on which).
- `class-validator` and `class-transformer` for DTOs.

If the project uses an older NestJS version, some APIs differ.
Match the project's version.

## 2. Framework Lifecycle Contracts

NestJS enforces five contracts on the developer. Every rule below
enforces one or more of these.

### 2.1 Request Pipeline Order

A request flows through: middleware → guards → interceptors
(before) → pipes → route handler → interceptors (after) →
exception filters (if thrown) → response.

Each stage has a defined role. Mixing roles causes silent bugs and
unpredictable behavior.

### 2.2 Dependency Injection Graph

NestJS builds a dependency graph at startup. Every provider is
instantiated in dependency order. A missing or circular dependency
fails at bootstrap, not at request time.

### 2.3 Module Encapsulation

A provider is only visible within its module and to modules that
import it via `exports`. This prevents accidental coupling across
features.

### 2.4 Decorator Metadata

Decorators attach metadata that the framework reads at runtime.
A decorator on the wrong target (method vs class vs parameter) is
silently ignored or produces a different behavior.

### 2.5 Scopes Propagate

A `REQUEST`-scoped provider causes every provider that depends on
it to become request-scoped. Scopes propagate up the injection
chain, adding overhead to every request.

## 3. Modules

### 3.1 One Module Per Feature

Each feature has its own module: `UsersModule`, `OrdersModule`,
`AuthModule`. The module encapsulates its controllers, services,
repositories, and DTOs.

### 3.2 Export Only What Other Modules Need

A module's `exports` array lists the providers that other modules
may inject. Exporting more exposes internals.

BAD:
```typescript
@Module({
  providers: [UsersService, UsersRepository, UsersMapper],
  exports: [UsersService, UsersRepository, UsersMapper],
})
export class UsersModule {}
```

GOOD:
```typescript
@Module({
  providers: [UsersService, UsersRepository, UsersMapper],
  exports: [UsersService],
})
export class UsersModule {}
```

The module's internals stay internal. Only the service is the
public API.

### 3.3 No Circular Module Dependencies

Circular module dependencies indicate a design problem. Extract
shared logic into a third module, or use events.

BAD:
```typescript
// users.module.ts
@Module({ imports: [forwardRef(() => OrdersModule)] })
export class UsersModule {}

// orders.module.ts
@Module({ imports: [forwardRef(() => UsersModule)] })
export class OrdersModule {}
```

GOOD: Extract `SharedModule` with the shared service. Both modules
import it. No cycle.

### 3.4 `forwardRef` Is a Last Resort

`forwardRef` exists for genuine circular references that cannot be
refactored away. Using it as a habit hides a design problem.

When `forwardRef` is used, add a comment explaining why the cycle
is necessary.

### 3.5 `@Global()` Only for Truly Global Modules

`@Global()` makes a module's exports available everywhere without
importing. It hides the dependency graph.

Legitimate uses: `ConfigModule`, `LoggerModule`, `DatabaseModule`.
Everything else imports explicitly.

### 3.6 Dynamic Modules Follow the Convention

`forRoot` is called once, in the root module, for global
configuration. `forFeature` is called in each feature module for
resource registration.

BAD: `TypeOrmModule.forRoot()` in a feature module.

GOOD: `TypeOrmModule.forRoot()` in `AppModule`,
`TypeOrmModule.forFeature([User])` in `UsersModule`.

### 3.7 Shared Module for Cross-Cutting Services

A `SharedModule` provides services used by multiple features
(logging helpers, common transformers). It imports nothing feature-
specific.

## 4. Providers and Dependency Injection

### 4.1 Constructor Injection

```typescript
@Injectable()
export class UsersService {
  constructor(private readonly repo: UsersRepository) {}
}
```

Constructor injection is explicit and testable. `@Inject()` is
needed only when the token is not a class.

### 4.2 `@Injectable()` on Every Provider

A class used as a provider has `@Injectable()`. Without it, NestJS
cannot resolve its dependencies and throws at bootstrap.

### 4.3 Custom Provider Tokens

For interfaces or non-class dependencies, use a symbol or string
token:

```typescript
export const USER_REPO = Symbol("USER_REPO");

@Module({
  providers: [{ provide: USER_REPO, useClass: PrismaUserRepo }],
})
export class UsersModule {}
```

Consumers inject via `@Inject(USER_REPO)`.

### 4.4 Avoid `REQUEST` Scope When Possible

A `REQUEST`-scoped provider causes the entire injection chain to be
recreated per request. This costs performance and complicates
testing.

Use `REQUEST` scope only when the provider genuinely needs
per-request state (the current user, a trace ID). Prefer
`AsyncLocalStorage` or explicit parameter passing.

### 4.5 No Service Locator

BAD:
```typescript
constructor(private moduleRef: ModuleRef) {}
someMethod() {
  const users = this.moduleRef.get(UsersService);
}
```

GOOD:
```typescript
constructor(private readonly users: UsersService) {}
```

`ModuleRef` is for dynamic resolution in rare cases (plugins,
runtime configuration). It is not a replacement for injection.

### 4.6 Provider Lifecycle Hooks

`OnModuleInit`, `OnModuleDestroy`, `OnApplicationShutdown`,
`OnApplicationBootstrap` run at defined times. Use them for setup
and cleanup, not for per-request logic.

## 5. Controllers

### 5.1 One Controller Per Resource

`UsersController` handles the `/users` routes. A second controller
for a sub-resource (`/users/:id/orders`) is separate.

### 5.2 Controllers Are Thin

A controller:

1. Receives a validated DTO.
2. Calls a service.
3. Returns the result.

No business logic. No database access. No orchestration.

BAD:
```typescript
@Post()
async create(@Body() dto: CreateUserDto) {
  const hashed = await bcrypt.hash(dto.password, 10);
  const user = await this.repo.save({ ...dto, password: hashed });
  await this.email.sendWelcome(user.email);
  return user;
}
```

GOOD:
```typescript
@Post()
async create(@Body() dto: CreateUserDto) {
  return this.users.create(dto);
}
```

### 5.3 No Cross-Controller Calls

A controller does not call another controller. If two resources
share logic, the logic belongs in a service.

### 5.4 Route Prefixes Without Leading Slash

`@Controller("users")` not `@Controller("/users")`. NestJS handles
the prefix.

### 5.5 Correct HTTP Method Decorator

`@Get`, `@Post`, `@Put`, `@Patch`, `@Delete`. Each maps to the
matching HTTP method. Using `@Post` for a delete is a contract
violation.

### 5.6 Response DTOs

Return a DTO, not an entity. Entities leak database schema
(columns, relations, internal IDs) to the API.

BAD:
```typescript
@Get(":id")
async get(@Param("id") id: string): Promise<User> {
  return this.users.findById(id);
}
```

GOOD:
```typescript
@Get(":id")
async get(@Param("id") id: string): Promise<UserResponseDto> {
  const user = await this.users.findById(id);
  return UserResponseDto.from(user);
}
```

## 6. DTOs and Validation

### 6.1 DTO for Every Input

Every request body, query, and param has a DTO class with
`class-validator` decorators.

```typescript
export class CreateUserDto {
  @IsEmail()
  email: string;

  @IsString()
  @MinLength(8)
  password: string;

  @IsEnum(Role)
  role: Role;
}
```

### 6.2 Global `ValidationPipe`

```typescript
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,
  forbidNonWhitelisted: true,
  transform: true,
  transformOptions: { enableImplicitConversion: true },
}));
```

- `whitelist`: strips unknown properties.
- `forbidNonWhitelisted`: rejects unknown properties with 400.
- `transform`: converts the plain object to the DTO class.

Without these options, unknown fields pass through and shape
validation is partial.

### 6.3 No `any` in Body

BAD:
```typescript
@Post()
async create(@Body() body: any) { ... }
```

GOOD:
```typescript
@Post()
async create(@Body() dto: CreateUserDto) { ... }
```

### 6.4 `PartialType` for Update DTOs

```typescript
export class UpdateUserDto extends PartialType(CreateUserDto) {}
```

Reuses the create validation rules with all fields optional.

### 6.5 `OmitType` for Excluding Fields

```typescript
export class CreateUserDto extends OmitType(UserDto, ["id", "createdAt"]) {}
```

Explicitly exclude fields that should not be set by the client.

### 6.6 Nested Validation With `@ValidateNested`

```typescript
export class CreateOrderDto {
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items: OrderItemDto[];
}
```

Without `@Type`, class-transformer does not know the nested type
and validation is skipped.

### 6.7 Query DTOs Need Validation Too

BAD:
```typescript
@Get()
async list(@Query("page") page: string) { ... }
```

GOOD:
```typescript
export class ListUsersQueryDto {
  @IsInt()
  @Min(1)
  @Type(() => Number)
  page: number = 1;
}

@Get()
async list(@Query() query: ListUsersQueryDto) { ... }
```

Query strings are always strings. Convert explicitly with `@Type`
or `ParseIntPipe`.

## 7. Guards

### 7.1 Guards for Authorization

A guard returns `true` (allow) or `false`/throws (deny). It runs
before the route handler. Auth and role checks live in guards.

### 7.2 `@UseGuards` at the Right Level

- On a single handler: applies only to that route.
- On a controller: applies to all routes in the controller.
- Global via `APP_GUARD`: applies to every route.

Global guards need a `@Public()` decorator for routes that should
skip them.

### 7.3 Custom `@Public()` Decorator

```typescript
export const IS_PUBLIC_KEY = "isPublic";
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private reflector: Reflector) {}
  canActivate(context: ExecutionContext): boolean {
    const isPublic = this.reflector.getAllAndOverride<boolean>(
      IS_PUBLIC_KEY,
      [context.getHandler(), context.getClass()],
    );
    if (isPublic) return true;
    // ... auth check
  }
}
```

This pattern avoids sprinkling auth checks in every controller.

### 7.4 No Business Logic in Guards

A guard checks permission. It does not create resources, send
emails, or modify state. Side effects belong in the handler or an
interceptor.

### 7.5 Return, Do Not `throw` Unless Denying

A guard returns `true` on success. Throwing `UnauthorizedException`
from a guard is valid for denial but should not be used as control
flow for the success path.

## 8. Interceptors and Pipes

### 8.1 Interceptors for Cross-Cutting Concerns

Logging, timing, response transformation, caching, timeouts.

```typescript
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler) {
    const now = Date.now();
    return next.handle().pipe(
      tap(() => console.log(`${Date.now() - now}ms`)),
    );
  }
}
```

### 8.2 No Business Logic in Interceptors

An interceptor wraps the handler. It does not replace it. If it
needs the request body, consider whether the logic belongs in the
service.

### 8.3 `ParseUUIDPipe` for UUIDs

BAD:
```typescript
@Get(":id")
async get(@Param("id") id: string) {
  if (!/^[0-9a-f-]{36}$/.test(id)) throw new BadRequestException();
  // ...
}
```

GOOD:
```typescript
@Get(":id")
async get(@Param("id", ParseUUIDPipe) id: string) { ... }
```

### 8.4 `ParseIntPipe` for Numeric Params

```typescript
@Get(":page")
async list(@Param("page", ParseIntPipe) page: number) { ... }
```

### 8.5 Custom Pipes for Reusable Transformations

A pipe transforms input to a typed value. If the transformation is
reusable, extract it. If it is a one-off, an interceptor or a DTO
transformer may fit better.

### 8.6 Interceptors Order Matters

Request-side interceptors run in registration order. Response-side
interceptors run in reverse. Document the order when multiple are
registered.

## 9. Exception Filters

### 9.1 Central Error Handling

A global exception filter catches `HttpException` and formats the
response consistently.

```typescript
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const res = ctx.getResponse<Response>();
    const status = exception instanceof HttpException
      ? exception.getStatus()
      : 500;
    res.status(status).json({
      success: false,
      error: { message: "Internal server error" },
    });
  }
}
```

### 9.2 No Stack Traces to the Client

In production, the response contains no stack trace. Stack traces
go to logs only.

### 9.3 Use NestJS HTTP Exceptions

`NotFoundException`, `BadRequestException`, `UnauthorizedException`,
`ForbiddenException`, `ConflictException`. Do not throw a generic
`Error` from a controller. NestJS cannot map it to a status code.

### 9.4 Never Catch in a Controller

BAD:
```typescript
@Get(":id")
async get(@Param("id") id: string) {
  try {
    return await this.users.findById(id);
  } catch (e) {
    throw new InternalServerErrorException();
  }
}
```

GOOD:
```typescript
@Get(":id")
async get(@Param("id") id: string) {
  const user = await this.users.findById(id);
  if (!user) throw new NotFoundException();
  return user;
}
```

Let the service throw domain errors. The global filter maps them.

### 9.5 Distinguish Operational From Programmer Errors

A missing user is a 404. A null pointer is a 500. The filter maps
known exception types; unknown exceptions become 500 and are logged.

## 10. Configuration

### 10.1 `ConfigService` Over `process.env`

BAD:
```typescript
const secret = process.env.JWT_SECRET;
```

GOOD:
```typescript
constructor(private config: ConfigService) {}

const secret = this.config.getOrThrow<string>("JWT_SECRET");
```

`ConfigService` validates that the variable exists, throws a clear
error if it does not, and is testable.

### 10.2 `ConfigModule.forRoot({ isGlobal: true })`

`isGlobal: true` makes `ConfigService` available everywhere without
importing `ConfigModule` in every feature module. This is the
intended use of `@Global()`.

### 10.3 Validate Environment at Startup

```typescript
ConfigModule.forRoot({
  isGlobal: true,
  validationSchema: Joi.object({
    DATABASE_URL: Joi.string().required(),
    JWT_SECRET: Joi.string().min(32).required(),
  }),
})
```

Invalid configuration fails at bootstrap, not at first request.

### 10.4 Never Commit `.env`

`.env` is gitignored. `.env.example` lists the required variables
with placeholder values.

## 11. Database and Persistence

### 11.1 Repository Pattern Over Direct ORM in Services

A service calls a repository. The repository owns the ORM calls.

BAD:
```typescript
@Injectable()
export class UsersService {
  constructor(private prisma: PrismaService) {}
  findAll() { return this.prisma.user.findMany(); }
}
```

GOOD:
```typescript
@Injectable()
export class UsersRepository {
  constructor(private prisma: PrismaService) {}
  findAll() { return this.prisma.user.findMany(); }
}

@Injectable()
export class UsersService {
  constructor(private repo: UsersRepository) {}
  findAll() { return this.repo.findAll(); }
}
```

The repository isolates the ORM. A change to the ORM does not
propagate to every service.

### 11.2 No `eager: true` on Relations

TypeORM's `eager: true` loads the relation on every query. This is
an N+1 waiting to happen. Load relations explicitly per query.

### 11.3 Transactions in the Service

A multi-step write operation runs in a transaction. The transaction
boundary is defined by the service, not the controller.

```typescript
async transfer(from: string, to: string, amount: number) {
  await this.repo.transaction(async (tx) => {
    await tx.debit(from, amount);
    await tx.credit(to, amount);
  });
}
```

### 11.4 No Entity Returned From a Service

The service returns a domain object or a DTO. The entity stays
inside the repository layer.

### 11.5 Migrations, Not `synchronize: true`

BAD:
```typescript
TypeOrmModule.forRoot({ synchronize: true })
```

GOOD:
```typescript
TypeOrmModule.forRoot({ synchronize: false, migrations: [...] })
```

`synchronize: true` drops and recreates columns based on the entity
definitions. In production, this destroys data.

## 12. Testing

### 12.1 `TestingModule` for Unit Tests

```typescript
const module = await Test.createTestingModule({
  providers: [
    UsersService,
    { provide: UsersRepository, useValue: mockRepo },
  ],
}).compile();
```

Override the repository with a mock. Test the service in isolation.

### 12.2 `supertest` for E2E

```typescript
const app = await createTestApp();
await request(app.getHttpServer())
  .post("/users")
  .send({ email: "a@b.com", password: "secret123" })
  .expect(201);
```

E2E tests use the full NestJS pipeline (guards, pipes, filters).

### 12.3 Mock Only External Dependencies

Mock the repository, the email service, and the external API. Do
not mock the service under test.

### 12.4 `jest` Configuration With `moduleNameMapper`

Match the project's path aliases (`@/`, `src/`) in `jest.config.js`.
Otherwise imports fail in tests.

### 12.5 No `TestBed` for Unit Tests

A service test does not need `TestBed` unless it uses the DI
container. Instantiate the service directly with mocks for the
common case.

## 13. Anti-Patterns

### 13.1 Business Logic in Controllers

Covered in 5.2.

### 13.2 Circular Module Imports

Covered in 3.3.

### 13.3 `forwardRef` as a Habit

Covered in 3.4.

### 13.4 Missing `@Injectable()`

A provider without the decorator fails at bootstrap with a
confusing error.

### 13.5 No DTO Validation

Covered in 6.

### 13.6 `@Body() body: any`

Covered in 6.3.

### 13.7 Direct Repository Access in Controllers

Covered in 5.2.

### 13.8 Global Modules Everywhere

Covered in 3.5.

### 13.9 `process.env` in Services

Covered in 10.1.

### 13.10 `synchronize: true` in Production

Covered in 11.5.

### 13.11 Missing `ParseUUIDPipe`

Covered in 8.3.

### 13.12 Returning Entities Directly

Covered in 5.6.

### 13.13 No Interceptor for Logging

Scattered `console.log` in controllers. Use an interceptor.

### 13.14 Catching Everything in a Controller

Covered in 9.4.

### 13.15 Untyped `@Query()`

BAD:
```typescript
@Get()
async list(@Query() query: any) { ... }
```

GOOD: A DTO with validation.

### 13.16 No `ValidationPipe` Globally

Without a global pipe, DTOs are not validated. The DTO classes
exist but do nothing.

### 13.17 Eager Loading Everything

Covered in 11.2.

### 13.18 No Transaction Management

A multi-step write without a transaction. Partial failures leave
the database inconsistent.

### 13.19 Middleware vs Guards Confusion

Middleware runs before the route handler and has no access to the
handler's metadata. Guards have access to the metadata and the
handler. Authorization belongs in guards, not middleware.

### 13.20 Logging `req.body`

Request bodies contain PII, tokens, and passwords. Log the shape,
not the values.

### 13.21 No Health Check

A NestJS app without `/health`. Use `@nestjs/terminus` for liveness
and readiness probes.

### 13.22 No Graceful Shutdown

`app.enableShutdownHooks()` is required for `OnApplicationShutdown`
to fire. Without it, in-flight requests are cut off on deploy.

### 13.23 Missing `Helmet`

`app.use(helmet())` sets security headers. Without it, the API is
vulnerable to common browser-based attacks.

### 13.24 No Global Prefix

`app.setGlobalPrefix("api/v1")` for a consistent API prefix.
Without it, routes are inconsistent and hard to route externally.

### 13.25 Unhandled Promise Rejections

An async provider method that is not awaited. Errors disappear
silently.

### 13.26 `ModuleRef.get` as Service Locator

Covered in 4.5.

### 13.27 `REQUEST` Scope Everywhere

Covered in 4.4. The performance cost is high.

### 13.28 No `class-transformer` for Nested DTOs

Missing `@Type(() => NestedDto)` skips nested validation.

### 13.29 `@UseGuards` Without Documentation

A controller-level guard that is not documented. Reviewers cannot
tell what the controller requires.

### 13.30 `Logger` From `@nestjs/common` Only

BAD: `console.log`, `console.error` in a service.

GOOD: `Logger` from `@nestjs/common`, or the project's logger.

### 13.31 Passing `ExecutionContext` to Services

The service does not know about the HTTP layer. Pass extracted
values, not the context.

### 13.32 `HttpException` With a Plain String

BAD: `throw new HttpException("not found", 404)`.

GOOD: `throw new NotFoundException()`.

Specific exception classes set the right status and message
structure.

### 13.33 Custom Decorators That Hide Dependencies

A custom `@CurrentUser()` decorator that reads from the request.
This is fine. A decorator that injects a service or performs I/O
is not.

### 13.34 No `class-validator` Custom Messages

Default messages are English and technical. Custom messages match
the project's user-facing language and clarity.

### 13.35 Skipping `E2E` Tests for Auth

Auth is the most security-sensitive part of a NestJS app. E2E tests
cover login, token refresh, guard rejection, and password reset.

### 13.36 Circular Providers

A service that injects another service that injects the first. Use
events or a third service.

### 13.37 No `ValidationPipe` on WebSocket

WebSocket gateways also need validation. Use a pipe or a custom
`@MessageBody()` decorator with validation.

## 14. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
