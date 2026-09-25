---
id: 02-mobile-anti-slop
title: "Mobile Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: delivery
version: 3
---

# Mobile Anti-Slop Layer

This file defines behavioral contracts specific to mobile applications. It sits in the delivery layer, below the universal anti-slop rules and above framework-specific patterns. It covers app lifecycle, permissions, offline behavior, secure storage, push notifications, platform conventions, and store compliance. It does not cover general frontend rules (see `02-frontend-anti-slop.md`), framework-specific rules for React Native or Flutter (see framework files), language rules (see language files), or accessibility and performance in detail (see concern files).

A mobile app runs on a device the user carries. It is suspended, resumed, killed by the OS, and restarted at unpredictable times. The OS is hostile to long-running processes.

## Scope

This file applies to native iOS (Swift, SwiftUI, UIKit), native Android (Kotlin, Jetpack Compose, XML views), and cross-platform frameworks (React Native, Flutter, .NET MAUI, Kotlin Multiplatform). The examples use React Native and Swift syntax where illustrative. Platform-specific framework rules live in framework files. Platform-specific language rules live in language files.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A mobile app commits to seven contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| State Survival | State survives backgrounding, process death, and restart. | MOB-001, MOB-002, MOB-056 |
| Permission Honesty | Only request used permissions, explain why, handle denial gracefully. | MOB-007 to MOB-012 |
| Offline Tolerance | Works without network, queues writes, shows state. | MOB-013 to MOB-019 |
| Secure Storage | Secrets in Keychain/Keystore, PII encrypted, cleaned on logout. | MOB-021 to MOB-023, MOB-055 |
| Store Compliance | Follows Apple/Google guidelines, no private APIs. | MOB-044 to MOB-049 |
| Battery Discipline | No background polling, respects OS battery modes. | MOB-037, MOB-069 |
| Platform Convention | Follows HIG/Material, safe areas, touch targets, system gestures. | MOB-038 to MOB-043 |

## App Lifecycle

### MOB-001 — Save State on Background

**MUST**

When the app moves to the background, user-visible state MUST be persisted before the OS terminates the process. Saving only on explicit user action causes data loss if the user backgrounds the app without tapping save.

Example (illustrative, Swift):

BAD:
```swift
func saveButtonTapped() { saveDocument() }
```

GOOD:
```swift
func scenePhaseDidChange(to phase: ScenePhase) {
    if phase == .background { saveDocument() }
}
```

### MOB-002 — Handle All Launch Types

**MUST**

Every launch (cold, warm, or hot) MUST be handled. The app MUST NOT assume it boots into a known screen. Navigation state and user-visible data MUST be restored on every launch.

### MOB-003 — Handle Interruptions

**MUST**

Phone calls, incoming messages, and system dialogs interrupt the app. Audio MUST be paused, animations stopped, and timers paused. They MUST resume on return.

### MOB-004 — OS Lifecycle Compliance

**MUST NOT**

The app MUST NOT fight the OS. Preventing the user from backgrounding the app, using hacks to extend background execution beyond the platform's allowance, or keeping the screen awake without a user-visible reason is prohibited.

### MOB-005 — Deep Link Handling

**MUST**

A deep link MUST open a specific screen, not the home screen. The link carries a route and parameters that the app MUST validate and resolve.

### MOB-006 — Android Back Button

**MUST**

The Android back button MUST work on every screen. A screen without a back path traps the user. Back MUST close modals and return to the previous screen.

## Permissions

### MOB-007 — Contextual Permission Request

**MUST**

Permissions MUST be requested when the user takes an action that requires them, never on first launch. A permission prompt before any interaction is denied at a higher rate, and on iOS a denial is one-shot.

### MOB-008 — Pre-Permission Explanation

**SHOULD**

A pre-permission screen explaining why the app needs the permission SHOULD be shown before the OS prompt. The OS prompt is one-shot on iOS; once denied, re-prompting requires a trip to Settings.

### MOB-009 — Graceful Denial Handling

**MUST**

Every permission can be denied. Every feature behind a permission MUST have a fallback or a clear message with a path to Settings. A blank screen on denial is prohibited.

### MOB-010 — Minimum Permission Scope

**MUST**

The minimum required scope MUST be requested: "when in use" location instead of "always", limited photo access instead of full library, specific contacts instead of full address book.

### MOB-011 — Manifest Hygiene

**MUST**

Every permission in the manifest is a signal to the user and store reviewers. Unused permissions MUST be removed.

### MOB-012 — iOS Purpose Strings

**MUST**

iOS requires a purpose string for each permission in `Info.plist`. Generic descriptions ("This app needs camera access") are rejected. Specific ones ("To scan QR codes") MUST be used.

## Offline and Network

### MOB-013 — Network Failure Paths

**MUST**

Mobile networks drop (tunnels, elevators, planes). Every network call MUST have a failure path that does not crash the app.

### MOB-014 — Caching Strategy

**SHOULD**

Static assets SHOULD be bundled or downloaded once. API responses SHOULD be cached with a clear expiry. User data SHOULD use local persistence for offline reads.

### MOB-015 — Offline Write Queueing

**MUST**

A user action that fails due to network MUST be queued and retried when the connection returns. The user's input MUST NOT be lost.

Example (illustrative, TypeScript):

BAD:
```typescript
async function sendMessage(text: string) {
  await api.post("/messages", { text }); // throws when offline
}
```

GOOD:
```typescript
async function sendMessage(text: string) {
  const message = { text, status: "pending" };
  await db.messages.insert(message);
  syncQueue.enqueue(message);
}
```

### MOB-016 — Error Type Distinction

**MUST**

"No connection" and "server returned 500" MUST be distinguished. The user cannot fix a server error by reconnecting.

### MOB-017 — Exponential Backoff

**MUST**

Mobile data is metered, and battery is limited. Retries MUST use exponential backoff with a ceiling and jitter (e.g., 1s, 2s, 4s, 8s, capped at 60s). Aggressive polling (e.g., every 100ms) is prohibited.

### MOB-018 — Connectivity State Indicator

**SHOULD**

A visible offline indicator SHOULD be shown. A user who cannot tell whether the app is offline blames the app.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### MOB-019 — Request Cancellation on Exit

**MUST**

A request started on screen A that completes after the user leaves A is wasted. It MUST be cancelled via the framework's abort mechanism.

See MAS-040 in `_universal/00-master-anti-slop.md`.

## Storage and Secrets

### MOB-020 — Storage Selection

**MUST**

The correct storage mechanism MUST be used: `UserDefaults`/`SharedPreferences` for preferences, SQLite/Room/Core Data for structured data, file system for large files, and Keychain/Keystore for secrets.

### MOB-021 — Secure Secret Storage

**MUST NOT**

Tokens, passwords, and keys MUST go in Keychain (iOS) or Keystore (Android). They MUST NEVER be stored in plain `UserDefaults` or `SharedPreferences`.

Example (illustrative, React Native):

BAD:
```typescript
await AsyncStorage.setItem("token", jwt); // plain text
```

GOOD: Use `react-native-keychain` or the platform's secure API.

### MOB-022 — PII Encryption at Rest

**MUST**

If the app stores PII or financial data, it MUST be encrypted before writing. The device filesystem is not a safe place for plaintext.

### MOB-023 — Logout Cleanup

**MUST**

On logout, session tokens, user-specific cached data, user-specific preferences, and downloaded content tied to the account MUST be cleared. Otherwise the next user sees the previous user's data.

### MOB-024 — Storage Schema Migration

**MUST**

When the persisted schema changes, a migration MUST be provided. Reading new fields directly from old data causes crashes on launch for existing users after an update.

### MOB-025 — React Native Storage API

**MUST NOT**

`localStorage` does not exist in React Native and MUST NOT be used. `AsyncStorage` (or the project's storage library) MUST be used.

## Push Notifications

### MOB-026 — Push Token Registration Lifecycle

**MUST**

The push token is tied to the user session. It MUST be registered after login and unregistered on logout.

### MOB-027 — Push Token Refresh

**MUST**

Push tokens change. The platform provides a callback. The server MUST be updated on change. Registering the token once and never updating it is prohibited.

Example (illustrative, Swift):
```swift
func application(_ application: UIApplication,
    didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
    let token = deviceToken.map { String(format: "%02x", $0) }.joined()
    Task { await api.registerDeviceToken(token) }
}
```

### MOB-028 — Push Notification Restraint

**MUST NOT**

A notification is an interruption. It MUST only be used for time-sensitive information, user-relevant updates, or actions the user explicitly opted into. Marketing notifications without explicit consent are prohibited.

### MOB-029 — Push Deep Linking

**MUST**

Tapping a notification MUST open a specific screen, not the home screen. The payload MUST carry the navigation target.

### MOB-030 — Push State Handling

**MUST**

A notification received while the app is in the foreground MUST be handled differently from one received in the background. Both paths MUST be tested.

### MOB-031 — Android Notification Channels

**MUST**

Android requires a channel for notifications. Without a channel, notifications are silently dropped. Channels MUST be defined.

## Performance on Real Devices

### MOB-032 — Low-End Device Testing

**MUST**

The simulator runs on the development machine, which is faster than any real phone. Testing MUST occur on the lowest-supported device.

### MOB-033 — Cold Start Optimization

**SHOULD**

A cold start over 2 seconds is slow. Startup SHOULD be profiled. Non-essential modules SHOULD be lazy-loaded.

### MOB-034 — Memory Leak Prevention

**MUST**

Mobile memory is limited. A leak that takes days to surface on desktop crashes the app in minutes on a low-end device. Memory MUST be managed and leaks prevented.

See MAS-040 in `_universal/00-master-anti-slop.md`.

### MOB-035 — App Size Discipline

**MUST**

Unused assets MUST be removed. Vector assets SHOULD be used. Apps MUST be split by device architecture (Android App Bundle, iOS App Thinning). Every dependency's size MUST be reviewed before adding.

### MOB-036 — UI Thread Non-Blocking

**MUST NOT**

A synchronous operation over 16 ms drops frames. I/O, database access, and heavy computation MUST NOT block the main thread.

Example (illustrative, Swift):

BAD:
```swift
let data = try Data(contentsOf: largeFileURL) // blocks main thread
```

GOOD:
```swift
let data = try await Task.detached {
    try Data(contentsOf: largeFileURL)
}.value
```

### MOB-037 — Battery Saving Compliance

**MUST NOT**

The app MUST NOT poll in the background. The platform's push mechanisms MUST be used. Network requests MUST be batched. The OS's battery-saving modes MUST be respected.

## Platform Conventions

### MOB-038 — Platform Design Language

**MUST**

iOS uses Human Interface Guidelines. Android uses Material Design. An iOS-looking app on Android or vice versa MUST NOT be built. Swipe-back navigation (iOS) and the back button (Android) MUST both work on their respective platforms.

### MOB-039 — Safe Area Respect

**MUST**

Notches, dynamic islands, and home indicators MUST be respected. The platform's safe area APIs MUST be used. Drawing under the status bar or the home indicator (e.g., fixed header at `top: 0`) is prohibited.

### MOB-040 — Touch Target Sizing

**MUST**

Touch targets MUST be minimum 44x44 points on iOS, 48x48 dp on Android. Small targets cause mis-taps.

### MOB-041 — System Gesture Non-Interference

**MUST NOT**

The app MUST NOT interfere with system gestures (swipe from edge, pull down for control center). A custom gesture that conflicts with the system is a bug.

### MOB-042 — Dynamic Type and Font Scaling

**MUST**

A user who increased the system font size expects the app to respect it. Layouts MUST NOT break when text is scaled to 200%.

### MOB-043 — System Dark Mode Support

**MUST**

If the OS is in dark mode, the app MUST respect it (or explicitly opt out with a user setting). Hardcoded light-only styling is a convention violation.

## App Store Compliance

### MOB-044 — In-App Purchase Compliance

**MUST**

Apple and Google require their in-app purchase systems for digital goods. Linking to an external payment page for digital goods violates the guidelines and MUST NOT be done.

### MOB-045 — Placeholder Content Prohibition

**MUST NOT**

Reviewers reject apps with "Lorem ipsum" or obviously unfinished content. Every screen in the build MUST be production-ready.

### MOB-046 — Privacy Manifest Accuracy

**MUST**

Both stores require a privacy disclosure listing the data collected and its use. The manifest MUST match the actual behavior.

### MOB-047 — Account Deletion Path

**MUST**

Apple and Google require apps with account creation to offer account deletion in-app. The deletion path MUST be discoverable.

### MOB-048 — Private API Prohibition

**MUST NOT**

Using private iOS APIs or reflection into system frameworks causes rejection and crashes on OS updates. They MUST NOT be used.

### MOB-049 — Age Rating Accuracy

**MUST**

The age rating MUST match the content. A mislabeled app is removed.

## AI-Specific Mobile Discipline

### MOB-074 — Native Module Verification

**MUST**

Before using a native bridge, platform API, or third-party native module, the assistant MUST verify it exists in the project's native code or standard SDK. Invented native modules produce runtime crashes that are invisible in the JavaScript/Dart layer.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### MOB-075 — Platform API Version Verification

**MUST**

Before using a platform API, the assistant MUST verify its availability for the project's minimum supported OS version. Using APIs introduced in newer OS versions without availability checks causes crashes on older devices.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### MOB-076 — Existing Component Discovery

**MUST**

Before creating a new native/custom view or complex UI component, the assistant MUST search the project for an existing equivalent. Inventing parallel components creates visual inconsistency across screen sizes.

See MAS-035 in `_universal/00-master-anti-slop.md`.

## Anti-Patterns

### MOB-050 — Hard-Coded Layouts

**MUST NOT**

Fixed positions that assume a specific viewport (e.g., 390x844) are prohibited. Constraint-based or flex layouts that adapt MUST be used.

### MOB-051 — Missing Loading States

**MUST NOT**

A frozen screen with no feedback on slow operations looks like a crash and is prohibited.

See MAS-037 in `_universal/00-master-anti-slop.md`.

### MOB-052 — Silent Sync Failures

**MUST NOT**

Silent failures in data sync paths (e.g., `try { ... } catch (e) {}`) are prohibited. The failure MUST be logged, the retry queued, and the user informed if user-visible.

### MOB-053 — Synchronous Network on Main Thread

**MUST NOT**

Synchronous network calls on the main thread (e.g., `URLSession.sendSynchronousRequest`, `HttpURLConnection` without a thread) block the UI and are prohibited.

### MOB-054 — Permanent Badge Counts

**MUST NOT**

A badge count that never decreases is prohibited. Users see a permanent notification indicator. Badges MUST be cleared appropriately.

### MOB-055 — Secrets in Bundle

**MUST NOT**

An API key in the app binary is extractable by anyone who downloads the app. Secrets MUST NOT be stored in the bundle. A server-side proxy MUST be used.

### MOB-056 — App State Restoration

**MUST**

A user who backgrounds the app and returns to a reset screen is a poor experience. iOS and Android both provide restoration APIs. State MUST be restored.

### MOB-057 — Unjustified Background Location

**MUST NOT**

Background location is heavily audited. Requesting it without a documented user benefit causes rejection and distrust. It MUST NOT be requested without justification.

### MOB-058 — Incorrect Permission Type

**MUST NOT**

Requesting broad permissions (e.g., `READ_CONTACTS`) when only one contact is needed is prohibited. The system contact picker, which requires no permission, MUST be used.

### MOB-059 — Resumable Downloads

**MUST**

A download that fails on a network switch MUST NOT be retried from scratch. The platform's resumable download API MUST be used.

### MOB-060 — Deprecated WebViews

**MUST NOT**

`UIWebView` is deprecated and removed. `WKWebView` MUST be used.

### MOB-061 — Android 13+ Push Permission

**MUST**

Android 13 introduced `POST_NOTIFICATIONS` as a runtime permission. Not handling it means notifications are silently blocked. It MUST be handled.

### MOB-062 — Android Memory Pressure Handling

**MUST**

Android signals memory pressure via `onTrimMemory`. Not responding means the OS kills the app harder. The signal MUST be handled.

### MOB-063 — Crash Reporting

**MUST**

A crash without a report is a bug the developer never sees. The platform's or a third-party crash reporter MUST be used.

### MOB-064 — Complex Data in Key-Value Storage

**MUST NOT**

`SharedPreferences`/`UserDefaults` is for small key-value pairs. Complex data MUST NOT be stored there; it belongs in a database.

### MOB-065 — Certificate Pinning for Sensitive Apps

**SHOULD**

An app handling financial or health data without certificate pinning is vulnerable to MITM on untrusted networks. Certificate pinning SHOULD be implemented. See the security concern file for details.

### MOB-066 — Accessibility Services Testing

**MUST**

TalkBack and VoiceOver MUST be tested. A custom widget without accessibility labels is invisible to screen readers.

See MAS-039 in `_universal/00-master-anti-slop.md`.

### MOB-067 — Rating Prompt Strategy

**SHOULD**

Asking for a review at the wrong moment (during onboarding, after a crash) is ineffective and annoying. `SKStoreReviewController` or the Play In-App Review API SHOULD be used at a positive moment.

### MOB-068 — Screen Density Assets

**MUST**

Assets that only ship in one density appear blurry or oversized on other devices. Multiple densities or vector assets MUST be provided.

### MOB-069 — Background Task Timing

**MUST**

iOS gives the app a few seconds to save state before termination. Long work there is killed. `beginBackgroundTask` MUST be used for extended work.

### MOB-070 — Time Zone Changes

**MUST**

A user who travels across time zones sees wrong times unless the app uses the system time zone or an explicit one. Time zone changes MUST be handled.

### MOB-071 — Device Time Trust Prohibition

**MUST NOT**

A user can change the device clock. Device time MUST NOT be used for security decisions (token expiry, session duration). Server time MUST be used.

### MOB-072 — Localization First

**MUST NOT**

Strings hardcoded in code are prohibited. Localization added at the end costs ten times more. Strings MUST be externalized from the start.

### MOB-073 — Screenshot Protection for Sensitive Screens

**SHOULD**

Financial apps SHOULD blur or block screenshots on sensitive screens. The platform provides APIs for this.

## Response to Violation

When a rule in this file is violated, report:

Violation: MOB-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.