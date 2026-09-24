---
id: 02-angular-anti-slop
title: "Angular Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-frontend-anti-slop]
category: domain
domain_type: framework
version: 1
---
# Angular Anti-Slop Layer

Layered under the master, architecture, and frontend layers. This file adds
rules for standalone components, modules, dependency injection, RxJS, signals,
templates, and change detection.

## 1. Stack Assumptions

1. Read the installed Angular major version before choosing standalone, signals,
   or control-flow APIs.
2. Follow the repository's module bootstrap style for existing code.
3. Use Angular Router and HttpClient as the only routing and HTTP boundaries.
4. Keep change detection assumptions explicit.
5. Do not mix signals and RxJS for the same state without a clear adapter.
6. Use the project's strictness and template type-checking settings.
7. Keep feature boundaries aligned with the application architecture.
8. Do not migrate standalone components to NgModules during unrelated work.

## 2. Standalone Components and Modules

1. Prefer standalone components for new code when the repository version and
   style support them.
2. Import exactly the providers and directives a standalone component uses.
3. Keep NgModules for existing module-based boundaries and shared declarations.
4. Do not create an NgModule that only re-exports one component.
5. Keep providers at the narrowest injector scope that works.
6. Avoid `providedIn: "root"` for stateful feature services.
7. Keep lazy routes self-contained with their providers and guards.
8. Do not declare the same component in multiple modules.

BAD:

```ts
@Component({ selector: "app-button", template: "<button>Save</button>" })
export class ButtonComponent {}

@NgModule({ declarations: [ButtonComponent], exports: [ButtonComponent] })
export class ButtonModule {}
```

GOOD:

```ts
@Component({
  selector: "app-button",
  standalone: true,
  template: "<button type=\"button\">Save</button>",
})
export class ButtonComponent {}
```

## 3. Templates and Inputs

1. Type inputs, outputs, and view queries explicitly.
2. Use signals for local component state when supported by the project.
3. Keep template expressions small and side-effect free.
4. Do not call a service with side effects from a template expression.
5. Use the new control-flow syntax only when the repository version supports it.
6. Keep track expressions stable and semantic for reorderable collections.
7. Use `OnPush` when the component benefits from explicit change detection.
8. Do not mutate inputs in place.
9. Use `ng-container` only when structure requires it.
10. Keep labels, error associations, and focus behavior in the component.

## 4. Change Detection

1. Do not add manual `detectChanges` as a substitute for a clear state model.
2. Keep `OnPush` components pure with respect to their inputs and signals.
3. Avoid functions that create new objects in hot template paths when a stable
   signal or computed value is available.
4. Treat async pipe results as immutable views; do not mutate them.
5. Move expensive derivation to a memoized signal or pure pipe only when needed.
6. Profile before optimizing change detection globally.
7. Do not mix event-driven updates with unrelated polling.
8. Keep async operations cancellation-aware.

BAD:

```ts
@Component({ changeDetection: ChangeDetectionStrategy.Default })
export class Dashboard {
  items = this.service.items;
  visibleItems() { return this.items.filter(item => item.active); }
}
```

GOOD:

```ts
@Component({ changeDetection: ChangeDetectionStrategy.OnPush })
export class Dashboard {
  readonly items = input.required<Item[]>();
  readonly visibleItems = computed(() => this.items().filter(item => item.active));
}
```

## 5. Dependency Injection

1. Inject services through the constructor or the repository's token.
2. Provide services at feature or route scope when they are not global.
3. Use an InjectionToken for stable non-class contracts.
4. Do not use `Injector.get` as a service locator in components.
5. Keep providers close to their consumers and avoid duplicate instances.
6. Do not put mutable application state in a root service without ownership.
7. Test provider dependencies in integration tests.
8. Use `inject()` only where the repository's style and version support it.

## 6. RxJS Discipline

1. Model asynchronous state explicitly with the repository's stream or signal
   pattern.
2. Do not subscribe manually when `async` pipe or an Angular lifecycle adapter
   owns the subscription.
3. Unsubscribe every manual subscription in the same component or service.
4. Use `switchMap` for replaceable navigation requests.
5. Use `concatMap` for ordered writes when ordering is a business invariant.
6. Use `exhaustMap` for actions that must ignore duplicate submissions.
7. Handle errors at the boundary that can recover or display them.
8. Do not nest subscriptions to model simple state transitions.
9. Share a stream only when multiple consumers need the same source.
10. Name streams by meaning, not by the operator used to create them.

BAD:

```ts
search$.pipe(map(value => this.service.search(value))).subscribe(results => this.results = results);
```

GOOD:

```ts
readonly results$ = this.search$.pipe(
  switchMap(value => this.service.search(value)),
  catchError(error => { this.errors.report(error); return of([]); }),
);
```

## 7. State and Data

1. Keep server data in the repository's data service or query boundary.
2. Keep URL state in the router and local UI state in the component.
3. Use signals for local derived state when the project's Angular version makes
   that the simpler choice.
4. Do not duplicate server entities in a global signal store.
5. Handle loading, empty, error, and stale states separately.
6. Cancel obsolete requests when route parameters change.
7. Do not subscribe in a loop or fetch one collection per row.
8. Use typed HTTP responses and validate dynamic route data.

## 8. Routing

1. Use route guards for authorization and navigation policy.
2. Keep data loading in resolvers, component providers, or the repository's
   established pattern.
3. Validate route parameters before constructing requests.
4. Use router links instead of string navigation.
5. Test guards for unauthenticated, unauthorized, and expired-session cases.
6. Keep lazy feature routes independently loadable.
7. Preserve return URLs only after validation.

## 9. Domain-Specific Anti-Patterns

### 9.1 Manual Subscription Leak

BAD:

```ts
ngOnInit() { this.service.events.subscribe(event => this.apply(event)); }
```

GOOD:

```ts
readonly events$ = this.service.events$;
```

### 9.2 Root Mutable Service

BAD:

```ts
@Injectable({ providedIn: "root" })
export class FeatureState { items: Item[] = []; }
```

GOOD:

```ts
@Injectable()
export class FeatureState { readonly items = signal<Item[]>([]); }
```

### 9.3 Side Effect in Getter

BAD:

```ts
get total() { this.analytics.track("total-viewed"); return this.items.length; }
```

GOOD:

```ts
readonly total = computed(() => this.items().length);
```

## 10. Response to Violation

If a previous response violated this file, use this structure:

```text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

State the violated rule and correction. Do not add unrelated explanation.
