---
id: 02-flutter-anti-slop
title: "Flutter Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop, 02-mobile-anti-slop]
category: domain
domain_type: framework
version: 1
---

# Flutter Anti-Slop Layer

Layered under the master, architecture, and mobile delivery layers. This
file covers widget composition, state, platform channels, and performance
conventions specific to Flutter.

## 1. Stack Assumptions

1. Use the Dart and Flutter versions declared by the project.
2. Confirm whether the application uses the project's navigation and state packages.
3. Keep domain and data code independent of Flutter widgets.
4. Use existing package and platform conventions before adding a dependency.
5. Confirm target platform versions before using a platform API.
6. Treat generated code as build output, not as an application layer.
7. Keep release, profile, and debug behavior distinct.
8. Verify platform-channel behavior on physical devices when applicable.
9. Do not assume web, desktop, and mobile support are interchangeable.
10. Read the existing analysis and lint settings before introducing patterns.

## 2. Project Structure

11. Organize features using the existing feature or layer structure.
12. Keep widgets, controllers, repositories, and models in their owning layers.
13. Keep platform channels behind a capability service.
14. Keep routes separate from reusable widgets and domain services.
15. Do not import `BuildContext` into domain or data code.
16. Use the existing barrel exports and naming convention.
17. Do not create a second navigation abstraction.
18. Put reusable design primitives in the existing design system layer.
19. Keep platform-specific implementations in named adapters.
20. Avoid folders that exist only to represent a pattern.

## 3. Widget Discipline

21. A widget describes UI and composition, not a complete use case.
22. Keep `build` free of network, storage, and permission side effects.
23. Use small private widgets for repeated structure, not arbitrary splitting.
24. Give widgets explicit constructor parameters and immutable inputs where possible.
25. Use `const` where it is valid and does not obscure necessary ownership.
26. Do not read a provider, router, or controller in a way that hides rebuilds.
27. Give keys stable meaning; do not use random keys to silence exceptions.
28. Keep layout constraints and overflow behavior intentional.
29. Use semantic labels for meaningful controls and images.
30. Do not use a `setState` in a build method to correct derived UI.
31. Keep gesture behavior owned by the smallest appropriate widget.
32. Do not use a monolithic `build` with unrelated conditional branches.
33. Preserve focus and accessibility when replacing a widget tree.
34. Use project navigation APIs for route transitions and deep links.
35. Test loading, empty, error, and populated states for each screen.

## 4. State and Data Flow

36. Keep ephemeral presentation state local to its widget or controller.
37. Keep durable records in the data layer, not in a widget field.
38. Use immutable models at the application boundary when practical.
39. Give a state object explicit loading and error semantics.
40. Do not copy a server value into several providers without an owner.
41. Rebuild state from a single authoritative stream or future.
42. Cancel subscriptions and controllers when their owner is disposed.
43. Do not use `notifyListeners` for unrelated changes.
44. Treat asynchronous results as stale until their identity is checked.
45. Keep retry actions separate from automatic refresh behavior.
46. Avoid a global provider for values used by one feature.
47. Use selectors when broad provider rebuilds are measured as harmful.
48. Never perform persistence work directly in a `build` method.

## 5. Platform Channels

49. Define a typed method and event contract for each channel.
50. Keep channel names and argument maps centralized and versioned.
51. Validate arguments and results in Dart and native code.
52. Return structured errors with a stable code and safe message.
53. Move expensive work off the platform UI thread.
54. Use streams or callbacks with one documented cancellation path.
55. Do not send unbounded binary data through a channel.
56. Keep platform implementations interchangeable behind a service.
57. Handle missing plugins and unsupported OS versions explicitly.
58. Never call a channel from a widget build method.
59. Do not expose arbitrary method dispatch to untrusted input.
60. Verify channel behavior in release mode and on each target platform.

## 6. Performance Conventions

61. Profile before adding caches, isolates, or custom painters.
62. Keep build methods focused on tree construction.
63. Avoid rebuilding large subtrees when a local state change is unrelated.
64. Use lazy lists for large or unbounded collections.
65. Keep item extent information accurate when list virtualization requires it.
66. Avoid expensive work in constructors, layout callbacks, and painters.
67. Use `const` for stable widget subtrees and immutable values.
68. Use image dimensions, caching policy, and decoding deliberately.
69. Avoid `setState` during a frame or an unbounded animation loop.
70. Keep isolate boundaries suitable for CPU-bound pure work only.
71. Treat `RepaintBoundary` as a measured optimization, not a default.
72. Recheck frame and memory behavior after each performance change.

## 7. Domain-Specific Anti-Patterns

### 7.1 Widget owns the application

BAD:
```dart
class ProfilePage extends StatefulWidget {
  @override
  void initState() {
    super.initState();
    http.post(profileUri);
  }
}
```

GOOD:
```dart
class ProfilePage extends StatelessWidget {
  const ProfilePage({required this.controller, super.key});

  final ProfileController controller;
}
```

### 7.2 State set from a disposed context

BAD:
```dart
Future<void> load() async {
  final data = await repository.read();
  context.read<ProfileState>().set(data);
}
```

GOOD:
```dart
Future<void> load() async {
  final data = await repository.read();
  if (!mounted) return;
  controller.set(data);
}
```

### 7.3 Untyped platform channel

BAD:
```dart
final result = await channel.invokeMethod(action, args);
```

GOOD:
```dart
final result = await channel.invokeMethod<ProfileResult>('loadProfile', args);
```

### 7.4 Rebuilding the application for one value

BAD:
```dart
class AppState extends ChangeNotifier {
  void setName(String value) { name = value; notifyListeners(); }
}
```

GOOD:
```dart
class NameField extends StatefulWidget {
  const NameField({required this.onChanged, super.key});
}
```

## 8. Response to Violation

76. Fetch the widget, controller, repository, and platform service before editing.
77. Move the side effect to the layer that owns the capability.
78. Preserve the existing state-management and navigation patterns.
79. Replace broad channel dispatch with a typed contract.
80. Add focused widget and service tests for changed behavior.
81. Check disposal, cancellation, and error rendering.
82. Profile only after a concrete performance symptom is identified.
83. State changed files, unchanged files, and unresolved platform risk.
84. Never claim device or release verification without running it.
85. Do not refactor unrelated widgets while fixing one flow.
86. Report missing generated files or package versions instead of guessing.
87. Keep the change small enough to review and reverse.
88. Make unsupported platforms visible in the product contract.
89. Use the repository's lint, analyzer, and test commands before completion.
90. Leave no incomplete examples or omitted implementation markers.
