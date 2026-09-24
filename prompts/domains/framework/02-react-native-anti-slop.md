---
id: 02-react-native-anti-slop
title: "React Native Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-react-anti-slop, 02-mobile-anti-slop]
category: domain
domain_type: framework
version: 1
---

# React Native Anti-Slop Layer

Layered under the master, architecture, React, and mobile delivery layers.
This file covers React Native bridges, platform modules, persistence,
hooks, and native event handling. General React, architecture, lifecycle,
permission, and offline rules are not repeated here.

## 1. Stack Assumptions

1. Use the React Native and React versions already declared by the project.
2. Confirm bare React Native versus Expo before choosing native APIs.
3. Confirm the minimum iOS and Android versions for every native module.
4. Treat JavaScript, TypeScript, and native code as separate boundaries.
5. Use the project's navigation, state, storage, and logging dependencies.
6. Do not add a native module when an existing supported package suffices.
7. Keep platform-specific files explicit with `.ios.` and `.android.` suffixes.
8. Read the native manifest and project configuration before adding capability.
9. Test behavior on the platform where the code actually executes.
10. Do not assume emulator behavior represents device behavior.

## 2. Project Structure

11. Keep screens, components, hooks, navigation, services, and native modules
    separate according to the existing feature or layer layout.
12. Put native code in the platform project, not in a JavaScript service.
13. Put bridge adapters beside the feature that owns the capability.
14. Keep storage and synchronization behind a repository interface.
15. Keep platform imports out of domain and reusable presentation code.
16. Use the existing naming and export conventions for new modules.
17. Do not create a second navigation, state, or persistence abstraction.
18. Keep configuration and capability checks in one explicit module.
19. Make ownership of listeners and subscriptions visible at the call site.
20. Do not bury a platform workaround in unrelated business code.

## 3. Component and Module Discipline

21. Keep render components declarative and free of native side effects.
22. Use a screen for route-level composition, not data orchestration.
23. Extract a native call into a named adapter with a typed result.
24. Every bridge method must document its input and failure behavior.
25. Return serializable values from bridge calls and events.
26. Use explicit loading, empty, error, and stale states where relevant.
27. Keep list items stable with existing keys and bounded rendering rules.
28. Avoid `any` at JavaScript, native, and bridge boundaries.
29. Do not invoke `Alert`, storage, or permissions during render.
30. Keep platform checks close to the platform adapter, not scattered in JSX.

## 4. Hooks and State Flow

31. Custom hooks must own a coherent behavior, not a collection of helpers.
32. A hook that starts work must return or expose its cancellation path.
33. Subscription effects must clean up listeners on dependency change.
34. Never use an effect to compute state that can be derived during render.
35. Keep transient input state local and durable records in the data layer.
36. Do not store a server object in state and mutate it in place.
37. Treat a response from a native call as data until validation succeeds.
38. Handle stale async responses with a request identity or cancellation.
39. Avoid state updates after an unmounted screen or stale operation.
40. Use a reducer when transitions are ordered or depend on previous state.
41. Do not duplicate one value in context, navigation, and local state.
42. Measure bridge calls and list rendering before adding optimization.
43. Keep platform event payloads narrow and versioned.
44. Every retry must preserve the operation identity and user intent.
45. Do not report success until the durable write has completed.

## 5. Native Bridge Discipline

46. Keep native method names and argument shapes stable across releases.
47. Validate bridge arguments in native code before using them.
48. Use typed errors with machine-readable codes for expected failures.
49. Keep callback invocation on the correct native thread and bridge queue.
50. Do not pass large binary objects through the bridge unnecessarily.
51. Move expensive native work off the UI thread and return completion.
52. Handle native completion, cancellation, and listener removal separately.
53. Version event payloads when a consumer can outlive the old payload.
54. Do not expose arbitrary filesystem, shell, or URL execution to JS.
55. Never bypass platform APIs with a hidden private API.
56. Keep capability checks beside the operation that needs the capability.
57. Treat missing native module registration as a startup or test failure.
58. Add a release-build test for the native path, not only Metro development.

## 6. Offline and Persistence

59. Use the project's durable storage API and its existing migration policy.
60. Store records in a repository, not directly from a screen.
61. Make writes atomic or recoverable after process interruption.
62. Keep pending mutations identifiable, bounded, and retryable.
63. Separate draft state from committed server state.
64. Never use an in-memory object as proof that a write is durable.
65. Read migration definitions before changing a stored shape.
66. Keep cached records explicitly disposable and size-bounded.
67. On schema failure, preserve recoverable data and report the failure.
68. Do not silently reset a user's durable data to make rendering work.
69. Make background synchronization cancellable and restartable.
70. Keep the mobile delivery layer responsible for generic offline policy.

## 7. Platform-Specific Modules

71. Use a platform matrix to record behavior differences before coding.
72. Keep platform code behind a common capability contract.
73. Do not silently choose a weaker implementation on one platform.
74. Show an explicit fallback when a capability is unavailable.
75. Test Android and iOS adapters independently where both exist.
76. Keep Android manifest and iOS entitlement changes synchronized.
77. Do not infer device capability from screen size or user agent.
78. Use the platform channel only for data the web layer cannot provide.
79. Keep deep-link and notification parsing outside generic components.
80. Verify release signing, permissions, and bundle settings together.

## 8. Domain-Specific Anti-Patterns

### 8.1 Bridge as an unrestricted RPC server

BAD:
```typescript
await NativeModules.Bridge.invoke({ action: "delete", args: input });
```

GOOD:
```typescript
await bridge.deleteDocument({ id, version });
```

### 8.2 Persistence hidden in a screen

BAD:
```typescript
await AsyncStorage.setItem("draft", JSON.stringify(draft));
```

GOOD:
```typescript
await documentRepository.saveDraft(draft, operationId);
```

### 8.3 Effect without ownership

BAD:
```typescript
useEffect(() => {
  const subscription = nativeEvents.subscribe(onEvent);
  if (disabled) return;
}, [disabled]);
```

GOOD:
```typescript
useEffect(() => {
  const subscription = nativeEvents.subscribe(onEvent);
  return () => subscription.remove();
}, [onEvent]);
```

### 8.4 Platform branching throughout JSX

BAD:
```tsx
{Platform.OS === "ios" ? <IOSSave /> : <AndroidSave />}
```

GOOD:
```tsx
<DocumentSave capability={saveCapability} />
```

## 9. Response to Violation

81. Stop before adding a workaround when the bridge contract is unclear.
82. Fetch the native module, manifest, and existing adapter definitions.
83. Identify the owning layer and keep the change at that boundary.
84. Replace broad dynamic calls with typed, validated operations.
85. Add a focused test for success, expected failure, and cancellation.
86. Verify persistence with a process restart and a release build.
87. Report incompatible platform behavior instead of hiding it.
88. Keep the diff limited to the requested capability and its contract.
89. State the files changed, files unchanged, and remaining uncertainty.
90. Do not claim native verification until the relevant command was run.
