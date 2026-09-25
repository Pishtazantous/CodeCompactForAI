---
id: 02-angular-anti-slop
title: "Angular Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 2
---

# Angular Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`,
`domains/framework/02-architecture-anti-slop.md`, and
`domains/delivery/02-frontend-anti-slop.md`. Rules already covered
in those files are NOT repeated here.

This file covers rules specific to Angular 17+: standalone
components, signals, dependency injection, RxJS discipline, change
detection, routing, and reactive forms. It does NOT cover
framework-agnostic frontend rules (see `02-frontend-anti-slop.md`),
architecture rules (see `02-architecture-anti-slop.md`), TypeScript
rules (see `02-typescript-anti-slop.md`), or UI rules (see
`04-ui-design-system.md`).

Angular is a large framework with several valid modes (NgModules vs
standalone, RxJS vs signals, zone.js vs zoneless). This file
describes the modern mode (standalone, signals, standalone
`inject()`). Projects on older modes follow their existing
conventions.

## 1. Stack Assumptions

This layer assumes:

- Angular 17 or later.
- Standalone components (no new NgModules).
- TypeScript strict mode.
- `inject()` for dependency injection.

If the project uses NgModules, follow the existing structure. Do
not migrate without instruction. Rules in this file apply to new
standalone code; existing NgModule code follows its own style.

## 2. Framework Lifecycle Contracts

Angular enforces four contracts on the developer. Every rule below
enforces one or more of these.

### 2.1 Change Detection Runs on Events

By default (with zone.js), Angular runs change detection after every
event, timer, and promise. `ChangeDetectionStrategy.OnPush` limits
this to inputs, events from the component, and signals.

### 2.2 Component Lifecycle Order

Constructor runs first. Then `ngOnInit`, then the first render,
then `ngAfterViewInit`. `ngOnDestroy` runs when the component is
removed from the tree.

### 2.3 Dependency Injection Hierarchy

Providers are resolved through a hierarchical injector: component,
then route, then module (if any), then root. A provider at a lower
level shadows the higher one.

### 2.4 Signals Are Pull-Based

A signal notifies consumers when it changes. `computed` and `effect`
subscribe to signals they read. Signals are synchronous; RxJS is for
event streams and async work.

## 3. Standalone Components

### 3.1 Standalone by Default

New components are `standalone: true`.

```typescript
@Component({
  selector: "app-user-card",
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: "./user-card.component.html",
})
export class UserCardComponent {
  @Input({ required: true }) user!: User;
}
```

### 3.2 One Component Per File, Three Files Per Component

`user-card.component.ts`, `user-card.component.html`,
`user-card.component.css`. Colocate test in `.spec.ts`.

### 3.3 `ChangeDetectionStrategy.OnPush` Always

Every component uses `OnPush`.

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
})
```

Default change detection re-checks every component on every event.
`OnPush` checks only on input change, event, or signal. This is the
single biggest performance lever in Angular.

### 3.4 Component Size

A component over 250 lines (including template) is doing too much.
Split when each part has an independent responsibility.

## 4. Signals and RxJS

### 4.1 Signals for Synchronous State

```typescript
count = signal(0);
doubled = computed(() => this.count() * 2);

increment() {
  this.count.update(c => c + 1);
}
```

Signals for component state, derived values, and any synchronous
reactive value.

### 4.2 RxJS for Event Streams and Async Work

HTTP, WebSocket, form value changes, router events: RxJS. Signals
for state, RxJS for streams. They compose: `toSignal()` and
`toObservable()` bridge the two.

BAD:
```typescript
// RxJS for a simple counter
private count$$ = new BehaviorSubject(0);
count$ = this.count$$.asObservable();
increment() { this.count$$.next(this.count$$.value + 1); }
```

GOOD:
```typescript
count = signal(0);
increment() { this.count.update(c => c + 1); }
```

### 4.3 `effect()` for Side Effects Only

`effect()` runs when its signal dependencies change. Use it for
side effects (logging, storage, DOM integration), not for derived
state.

BAD:
```typescript
count = signal(0);
doubled = signal(0);
constructor() {
  effect(() => { this.doubled.set(this.count() * 2); });
}
```

GOOD:
```typescript
count = signal(0);
doubled = computed(() => this.count() * 2);
```

### 4.4 `computed()` Is Pure

A `computed` reads signals and returns a value. No side effects, no
I/O, no mutation. If it needs to write, it is not a computed.

### 4.5 `untracked()` for Intentional Non-Dependencies

When a signal is read inside an `effect` but should not trigger it,
wrap with `untracked()`:

```typescript
effect(() => {
  const value = this.count();
  const other = untracked(this.other);
  log(value, other);
});
```

Without `untracked`, reading `other` adds it as a dependency.

### 4.6 `toSignal()` for RxJS-to-Signal Conversion

```typescript
users = toSignal(this.http.get<User[]>("/api/users"), { initialValue: [] });
```

The signal updates when the observable emits. The `initialValue`
prevents `undefined` in the template.

### 4.7 Signals Are Not Replaced by RxJS Everywhere

Migrating a signal to `BehaviorSubject` "for consistency" is a
regression. Match the tool to the data flow.

## 5. Dependency Injection

### 5.1 `providedIn: "root"` for Singletons

```typescript
@Injectable({ providedIn: "root" })
export class UsersService { ... }
```

One instance for the whole app. This is the default for most
services.

### 5.2 `inject()` Over Constructor Injection

```typescript
export class UserCardComponent {
  private users = inject(UsersService);
}
```

`inject()` works in field initializers, in `computed`, in `effect`,
and in guards. It is clearer than constructor parameter lists and
requires no `@Injectable` order.

Constructor injection still works. Prefer `inject()` for new code.

### 5.3 Injection Tokens for Non-Class Dependencies

```typescript
export const API_URL = new InjectionToken<string>("API_URL");

// In a provider:
{ provide: API_URL, useValue: "https://api.example.com" }

// In a consumer:
private apiUrl = inject(API_URL);
```

### 5.4 No Service Locator

BAD:
```typescript
constructor(private injector: Injector) {}
someMethod() {
  const users = this.injector.get(UsersService);
}
```

GOOD:
```typescript
private users = inject(UsersService);
```

Injecting `Injector` to fetch services at runtime hides
dependencies. Use it only for dynamic providers.

### 5.5 Component-Level Providers for Scoped Instances

A service provided at the component level has one instance per
component. Use this for state that belongs to a component subtree.

### 5.6 No Circular Dependencies

A circular dependency between services is a design smell. Extract
the shared logic or use an event.

### 5.7 `providedIn: "any"` Rare

`providedIn: "any"` creates a new instance per lazy-loaded module.
It is almost never what you want. Use `"root"` or component-level.

## 6. RxJS Discipline

### 6.1 Unsubscribe

Every subscription is cleaned up:

- `takeUntilDestroyed()` (Angular 16+).
- The `async` pipe in templates.
- Manual unsubscribe in `ngOnDestroy`.

```typescript
private destroyRef = inject(DestroyRef);

ngOnInit() {
  this.users.getUsers()
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(users => this.users.set(users));
}
```

`takeUntilDestroyed()` is the modern pattern. Without it, the
subscription outlives the component and leaks.

### 6.2 `async` Pipe in Templates

```html
@if (users$ | async; as users) {
  @for (user of users; track user.id) {
    <app-user [user]="user" />
  }
}
```

The `async` pipe subscribes and unsubscribes automatically.

### 6.3 No Nested Subscriptions

BAD:
```typescript
this.users.getUser(id).subscribe(user => {
  this.orders.getOrders(user.id).subscribe(orders => { ... });
});
```

GOOD:
```typescript
this.users.getUser(id).pipe(
  switchMap(user => this.orders.getOrders(user.id)),
).subscribe(orders => { ... });
```

Nested subscriptions are hard to cancel and hard to reason about.

### 6.4 `switchMap` for Cancellable Sequential Work

A new emission cancels the previous inner observable. Use it for
search, typeahead, and route param changes.

### 6.5 `mergeMap` for Parallel Independent Work

Each emission triggers an inner observable that runs in parallel.
Use it when order does not matter and all results are needed.

### 6.6 `concatMap` for Ordered Sequential Work

Emissions are processed one at a time, in order. Use it when order
matters.

### 6.7 `exhaustMap` for Ignoring While Busy

New emissions are ignored while an inner observable is in flight.
Use it for form submissions.

### 6.8 `catchError` at the Boundary

Handle errors at the boundary of the data flow, not in the middle.

BAD:
```typescript
this.http.get<User>("/api/user").subscribe({
  next: user => this.user.set(user),
  error: err => console.error(err),
});
```

GOOD:
```typescript
this.http.get<User>("/api/user").pipe(
  catchError(err => {
    this.logger.error("fetch user failed", err);
    return of(null);
  }),
).subscribe(user => this.user.set(user));
```

### 6.9 No `subscribe()` in Constructors

Constructors run before inputs are set and before the view is
initialized. Use `ngOnInit`, `afterNextRender`, or `takeUntilDestroyed`
with a proper lifecycle entry point.

### 6.10 `shareReplay` for Shared Observables

An HTTP observable that multiple subscribers use is shared:

```typescript
users$ = this.http.get<User[]>("/api/users").pipe(shareReplay(1));
```

Without it, each subscription triggers a new request.

### 6.11 `firstValueFrom` and `lastValueFrom`

To convert an observable to a promise, use `firstValueFrom` or
`lastValueFrom`. Do not use `toPromise()` (deprecated).

### 6.12 No Manual `Subject` for State

BAD:
```typescript
private users$$ = new BehaviorSubject<User[]>([]);
users$ = this.users$$.asObservable();
```

GOOD:
```typescript
users = signal<User[]>([]);
```

`BehaviorSubject` is for event streams, not for state. Signals are
the modern state primitive.

## 7. Routing

### 7.1 Standalone Routes

```typescript
export const routes: Routes = [
  {
    path: "users",
    loadComponent: () =>
      import("./users/users.component").then(m => m.UsersComponent),
  },
];
```

### 7.2 Lazy Loading by Default

Every feature route lazy-loads. `loadComponent` for a single
component, `loadChildren` for a group.

Eager loading a feature route that is rarely visited slows the
initial load.

### 7.3 Functional Guards

```typescript
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.isAuthenticated() || router.createUrlTree(["/login"]);
};
```

Functional guards over class-based guards. Fewer classes, easier
composition.

### 7.4 Functional Resolvers

```typescript
export const userResolver: ResolveFn<User> = (route) => {
  const id = route.paramMap.get("id");
  if (!id) throw new Error("missing id");
  return inject(UsersService).getUser(id);
};
```

Resolvers fetch data before the route activates. The route does not
render with missing data.

### 7.5 Route Params Are Strings

`route.snapshot.paramMap.get("id")` returns `string | null`.
Convert and validate before use.

BAD:
```typescript
const id = route.snapshot.paramMap.get("id"); // string | null
this.users.getUser(id); // type error or runtime failure
```

GOOD:
```typescript
const id = route.snapshot.paramMap.get("id");
if (!id) return;
this.users.getUser(id);
```

### 7.6 No Route Logic in Components

A component does not redirect except in response to a user action.
Authorization and redirect logic live in guards.

## 8. Forms

### 8.1 Reactive Forms Over Template-Driven

BAD:
```html
<input [(ngModel)]="email" />
```

GOOD:
```typescript
form = this.fb.nonNullable.group({
  email: ["", [Validators.required, Validators.email]],
});
```
```html
<input formControlName="email" />
```

Reactive forms are testable, typed, and explicit. Template-driven
forms rely on two-way binding and are hard to test.

### 8.2 Typed Forms

```typescript
form = this.fb.nonNullable.group({
  email: ["", [Validators.required, Validators.email]],
  age: [0, [Validators.min(0)]],
});
```

`nonNullable` prevents `null` values from creeping into the form
state.

### 8.3 Validators in the Form, Not the Template

```typescript
email: ["", [Validators.required, Validators.email]],
```

Validators belong with the control definition, not scattered in the
template. This makes the validation rules a single source of truth.

### 8.4 Display Errors Near the Field

```html
<input formControlName="email" />
@if (form.controls.email.invalid && form.controls.email.touched) {
  <p class="error">{{ getEmailError() }}</p>
}
```

Errors appear next to the field, not in a global toast.

### 8.5 No `valueChanges` Without Cleanup

A `valueChanges` subscription needs `takeUntilDestroyed()` or the
`async` pipe.

### 8.6 No Direct `setValue` in Render

`form.setValue` in a template expression causes infinite loops.
Update the form in an event handler.

## 9. Templates

### 9.1 New Control Flow Syntax

Angular 17+ uses `@if`, `@for`, `@switch` instead of `*ngIf`,
`*ngFor`, `*ngSwitch`.

```html
@if (user) {
  <p>{{ user.name }}</p>
} @else {
  <p>Loading...</p>
}

@for (item of items; track item.id) {
  <app-item [item]="item" />
}
```

The new syntax is clearer and does not require importing directives.

### 9.2 `track` in `@for`

Every `@for` has a `track` expression. Without it, the list
re-renders entirely on every change.

BAD:
```html
@for (item of items; track $index) { ... }
```

GOOD:
```html
@for (item of items; track item.id) { ... }
```

`$index` is acceptable only for static lists.

### 9.3 No Method Calls in Templates

BAD:
```html
<div>{{ formatDate(user.createdAt) }}</div>
```

The method runs on every change detection cycle.

GOOD:
```html
<div>{{ formattedDate() }}</div>
```
```typescript
formattedDate = computed(() => formatDate(this.user().createdAt));
```

### 9.4 `@defer` for Heavy Content

```html
@defer (on viewport) {
  <app-heavy-chart />
} @placeholder {
  <p>Chart loading...</p>
}
```

Defer non-critical content. The initial render is faster.

### 9.5 No Complex Expressions in Templates

Extract to `computed` or a component method. Templates are not the
place for logic.

### 9.6 Attribute Directives Over Component Wrappers

A directive that adds behavior is lighter than a component that
wraps. Use `@Directive` when no template is needed.

## 10. Change Detection

### 10.1 `OnPush` Everywhere

See 3.3. Default change detection is a performance liability.

### 10.2 Signals for Local State

Signals trigger change detection only for the components that read
them. This is more efficient than zone.js triggering globally.

### 10.3 Zoneless When Available

Angular 18+ supports zoneless change detection with signals. Prefer
it when the project uses it. Zoneless removes zone.js from the
bundle and reduces change detection overhead.

### 10.4 No `NgZone.run` as a Fix

Running code inside `NgZone.run` because "otherwise it does not
update" is a symptom, not a fix. The real issue is usually that the
state change is outside Angular's knowledge. Use signals.

### 10.5 `markForCheck` Only When Necessary

`ChangeDetectorRef.markForCheck` is needed when mutating state
outside Angular's knowledge. With `OnPush` and signals, it is rarely
needed. When used, comment why.

## 11. Anti-Patterns

### 11.1 Default Change Detection

A component without `OnPush` re-checks on every event in the app.

### 11.2 `BehaviorSubject` for Component State

Covered in 6.12. Signals are the state primitive.

### 11.3 Nested Subscriptions

Covered in 6.3.

### 11.4 Subscription Without Cleanup

Covered in 6.1.

### 11.5 `subscribe()` in Constructor

Covered in 6.9.

### 11.6 Service Locator

Covered in 5.4.

### 11.7 Mutating Inputs

BAD:
```typescript
@Input() user!: User;
someMethod() { this.user.name = "new"; }
```

GOOD: Emit an event or use two-way binding.

### 11.8 Method Calls in Templates

Covered in 9.3.

### 11.9 `*ngIf` in New Code

The new control flow syntax is the default in Angular 17+.

### 11.10 `@for` Without `track`

Covered in 9.2.

### 11.11 Global Mutable Service State

BAD:
```typescript
@Injectable({ providedIn: "root" })
export class UsersService {
  users: User[] = []; // mutable global state
}
```

GOOD:
```typescript
@Injectable({ providedIn: "root" })
export class UsersService {
  private usersSignal = signal<User[]>([]);
  users = this.usersSignal.asReadonly();
  setUsers(users: User[]) { this.usersSignal.set(users); }
}
```

### 11.12 `any` in HTTP Responses

BAD:
```typescript
this.http.get<any>("/api/user").subscribe(u => u.name.toUpperCase());
```

GOOD:
```typescript
this.http.get<User>("/api/user").subscribe(u => u.name.toUpperCase());
```

### 11.13 No Route Guards

An authenticated route without a guard. Redirect logic sprinkled in
components.

### 11.14 Eager Loading Every Route

Covered in 7.2.

### 11.15 Direct DOM Manipulation

BAD:
```typescript
document.getElementById("x")!.textContent = "new";
```

GOOD: `@ViewChild` with a template ref, or signals, or a binding.

### 11.16 `Renderer2` in New Code

`Renderer2` is for SSR-safe DOM manipulation. For most cases,
template bindings or `@ViewChild` are clearer. Use `Renderer2` only
when the DOM element is not in the template.

### 11.17 `NgZone.run` Everywhere

Covered in 10.4.

### 11.18 Ignoring Strict Mode

`strict: true` in `tsconfig.json` is required. It catches null
errors and property initialization issues.

### 11.19 `NgModule` for New Code

Covered in 1.

### 11.20 Zone.js in Zoneless Projects

Mixing zones and zoneless change detection causes subtle bugs. Pick
one.

### 11.21 Ignoring `takeUntilDestroyed`

Angular 16+ provides `takeUntilDestroyed()`. Use it.

### 11.22 Signals for Event Streams

Signals are for state. Streams of events (typing, scrolling,
WebSocket messages) are RxJS. Use the right tool.

### 11.23 RxJS for Simple State

Covered in 4.2.

### 11.24 Testing Implementation

BAD: Testing that a method was called.

GOOD: Testing that the DOM reflects the expected state.

### 11.25 No `TestBed` Cleanup

`TestBed` leaks between tests if not reset. Use the default
teardown or `TestBed.resetTestingModule()`.

### 11.26 Template-Driven Forms for Complex Forms

Covered in 8.1.

### 11.27 `subscribe()` Without an Error Handler

An HTTP error without a handler crashes the app or is silently
swallowed.

### 11.28 `Subject` Without Completion

A `Subject` that is never completed leaks subscribers. Complete or
unsubscribe.

### 11.29 `firstValueFrom` on a Non-Completing Observable

`firstValueFrom` waits for the first value. On an observable that
never emits, it hangs forever.

### 11.30 Manual Change Detection

`ChangeDetectorRef.detectChanges()` called manually is a code smell.
Use signals or fix the state flow.

## 12. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
