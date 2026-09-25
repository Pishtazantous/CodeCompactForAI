---
id: 02-mobile-anti-slop
title: "Mobile Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: delivery
version: 2
---

# Mobile Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
generic security, dependency addition, output format) are NOT
repeated here.

This file covers rules specific to mobile applications: app
lifecycle, permissions, offline behavior, secure storage, push
notifications, platform conventions, and store compliance. It does
NOT cover general frontend rules (see `02-frontend-anti-slop.md`),
framework-specific rules for React Native or Flutter (see the
framework files), language rules (see the language files), or
accessibility and performance in detail (see the concern files).

A mobile app runs on a device the user carries. It is suspended,
resumed, killed by the OS, and restarted at unpredictable times. The
OS is hostile to long-running processes. The rules below reflect
that reality.

## 1. Stack Assumptions

This file applies to:

- Native iOS (Swift, SwiftUI, UIKit).
- Native Android (Kotlin, Jetpack Compose, XML views).
- Cross-platform (React Native, Flutter, .NET MAUI, Kotlin
  Multiplatform).

The examples use React Native and Swift syntax. The principles are
platform-agnostic. Platform-specific framework rules (React Native
hooks, Flutter widgets, SwiftUI property wrappers) live in the
framework files. Platform-specific language rules (Swift optionals,
Kotlin nullability) live in the language files.

## 2. Delivery Contracts

A mobile app commits to seven contracts. Every section below
enforces one or more of these.

### 2.1 State Survival

Any state the user can see survives backgrounding, process death,
and restart. Data is persisted before the app moves to the
background, not after.

### 2.2 Permission Honesty

The app requests only the permissions it uses and explains why. A
denied permission has a graceful fallback.

### 2.3 Offline Tolerance

The app works, in degraded form, without network. Every network
call has a failure path that does not crash the app.

### 2.4 Secure Storage

Tokens, credentials, and PII go in the platform's secure storage
(Keychain, Keystore). Never in plain preferences.

### 2.5 Store Compliance

The app follows Apple App Store Review Guidelines, Google Play
Policies, and the platform's requirements. Non-compliance means
removal.

### 2.6 Battery Discipline

The app does not poll in the background, does not hold wake locks
unnecessarily, and respects the OS's battery-saving modes.

### 2.7 Platform Convention

The app follows the platform's conventions (iOS HIG, Material
Design) unless the design genuinely requires deviation.

## 3. App Lifecycle

### 3.1 Save State on Background

When the app moves to the background, persist user-visible state
before the OS terminates the process.

BAD:
```swift
// Save only on user action.
func saveButtonTapped() {
    saveDocument()
}
```

If the user backgrounds the app without tapping, unsaved changes
are lost.

GOOD:
```swift
func scenePhaseDidChange(to phase: ScenePhase) {
    if phase == .background {
        saveDocument()
    }
}
```

### 3.2 Handle All Launch Types

Every launch is either cold (process created), warm (process
resumed), or hot (activity/view recreated). The app handles all
three.

BAD: Code that assumes the app boots into a known screen.

GOOD: Restore the navigation state and user-visible data on every
launch.

### 3.3 Handle Interruptions

Phone calls, incoming messages, and system dialogs interrupt the
app. Pause audio, stop animations, and pause timers. Resume on
return.

### 3.4 Do Not Fight the OS

- Do not prevent the user from backgrounding the app.
- Do not use hacks to extend background execution beyond the
  platform's allowance.
- Do not keep the screen awake without a user-visible reason.

### 3.5 Handle Deep Links and Universal Links

A deep link opens a specific screen, not the home screen. The link
carries a route and parameters that the app resolves.

BAD: A deep link that opens the home screen and ignores the payload.

GOOD: A deep link handler that validates the URL and navigates.

### 3.6 Android Back Button

The Android back button works on every screen. A screen without a
back path traps the user.

BAD: A modal with no close button and no back handling.

GOOD: Back closes the modal and returns to the previous screen.

## 4. Permissions

### 4.1 Request in Context

Request a permission when the user takes an action that requires
it. Never on first launch.

BAD: Requesting camera, location, and notification permissions at
startup.

GOOD: Requesting camera when the user taps "Take photo".

A permission prompt before any interaction is denied at a higher
rate, and on iOS a denial is one-shot.

### 4.2 Explain Before Prompting

Show a pre-permission screen explaining why the app needs the
permission. The OS prompt is one-shot on iOS. Once denied,
re-prompting requires a trip to Settings.

### 4.3 Handle Denial Gracefully

Every permission can be denied. Every feature behind a permission
has a fallback or a clear message with a path to Settings.

BAD: A blank screen when the camera permission is denied.

GOOD: A message explaining the feature requires camera access, with
a button to open Settings.

### 4.4 Minimum Permission Scope

- "When in use" location instead of "always" when possible.
- Limited photo access instead of full library access when
  possible.
- Specific contacts instead of full address book.

### 4.5 Request Only What You Use

Every permission in the manifest is a signal to the user and to
the store reviewers. Remove unused permissions.

### 4.6 Explain in `Info.plist` (iOS)

iOS requires a purpose string for each permission. Generic
descriptions ("This app needs camera access") are rejected.
Specific ones ("To scan QR codes") pass.

## 5. Offline and Network

### 5.1 Assume No Network

Mobile networks drop. Tunnels, elevators, planes, subways. Every
network call has a failure path.

### 5.2 Cache What Can Be Cached

- Static assets: bundled or downloaded once.
- API responses: cached with a clear expiry.
- User data: local persistence for offline reads.

### 5.3 Queue Writes When Offline

A user action that fails due to network is queued and retried when
the connection returns. Do not lose the user's input.

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

### 5.4 Distinguish Network Errors From Server Errors

"No connection" and "server returned 500" are different. The user
cannot fix the second by reconnecting.

### 5.5 Do Not Retry Aggressively

Mobile data is metered, and battery is limited. Exponential backoff
with a ceiling.

BAD: Retrying every 100 ms.

GOOD: Retrying at 1 s, 2 s, 4 s, 8 s, capped at 60 s, with jitter.

### 5.6 Show Connectivity State

A user who cannot tell whether the app is offline blames the app.
A visible offline indicator prevents confusion.

### 5.7 Cancel Requests on Screen Exit

A request started on screen A that completes after the user leaves
A is wasted. Cancel it via the framework's abort mechanism.

## 6. Storage and Secrets

### 6.1 Choose the Right Storage

- **User preferences**: `UserDefaults`, `SharedPreferences`.
- **Small structured data**: SQLite, Room, Core Data.
- **Large files**: file system, not database.
- **Secrets**: Keychain, Keystore.

### 6.2 Never Store Secrets in Plain Storage

Tokens, passwords, and keys go in Keychain (iOS) or Keystore
(Android). Never in `UserDefaults` or `SharedPreferences`.

BAD:
```typescript
await AsyncStorage.setItem("token", jwt); // plain text
```

GOOD: Use `react-native-keychain` or the platform's secure API.

### 6.3 Encrypt Sensitive Data at Rest

If the app stores PII or financial data, encrypt it before writing.
The device filesystem is not a safe place for plaintext.

### 6.4 Clean Up on Logout

On logout, clear:

- Session tokens.
- User-specific cached data.
- User-specific preferences.
- Downloaded content tied to the account.

Otherwise the next user sees the previous user's data.

### 6.5 Migration Path for Storage

When the persisted schema changes, provide a migration. Otherwise
the app crashes on launch for existing users after an update.

BAD: Reading the new field directly from old data.

GOOD:
```typescript
const raw = await storage.get("user");
const user = raw ? migrateUser(raw) : null;
```

### 6.6 Do Not Use `localStorage` in React Native

`localStorage` does not exist in React Native. Use
`AsyncStorage` (or the project's storage library).

## 7. Push Notifications

### 7.1 Request Permission in Context

Never on first launch. See 4.1.

### 7.2 Register the Token After Login

The push token is tied to the user session. Register after login,
unregister on logout.

### 7.3 Handle Token Refresh

Push tokens change. The platform provides a callback. Update the
server on change.

BAD: Register the token once and never update it.

GOOD:
```swift
func application(
    _ application: UIApplication,
    didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
) {
    let token = deviceToken.map { String(format: "%02x", $0) }.joined()
    Task { await api.registerDeviceToken(token) }
}
```

### 7.4 Do Not Use Notifications for Everything

A notification is an interruption. Use it for:

- Time-sensitive information.
- User-relevant updates.
- Actions the user explicitly opted into.

Do not use it for marketing without explicit consent.

### 7.5 Deep Link on Tap

Tapping a notification opens a specific screen, not the home
screen. The payload carries the navigation target.

### 7.6 Handle Foreground and Background

A notification received while the app is in the foreground is
handled differently from one received in the background. Both
paths are tested.

### 7.7 Request a Notification Channel (Android)

Android requires a channel for notifications. Without a channel,
notifications are silently dropped.

## 8. Performance on Real Devices

### 8.1 Test on Low-End Devices

The simulator runs on the development machine, which is faster than
any real phone. Test on the lowest-supported device.

### 8.2 Cold Start Time

A cold start over 2 seconds is slow. Profile startup. Lazy-load
non-essential modules.

### 8.3 Memory

Mobile memory is limited. A leak that takes days to surface on
desktop crashes the app in minutes on a low-end device.

### 8.4 Battery

- Do not poll in the background.
- Use the platform's push mechanisms.
- Batch network requests.
- Respect the OS's battery-saving modes.

### 8.5 App Size

- Remove unused assets.
- Use vector assets where possible.
- Split by device architecture (Android App Bundle, iOS App
  Thinning).
- Review every dependency's size before adding.

### 8.6 Do Not Block the UI Thread

A synchronous operation over 16 ms drops frames. Move I/O, database
access, and heavy computation off the main thread.

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

## 9. Platform Conventions

### 9.1 Follow the Platform's Design Language

iOS uses Human Interface Guidelines. Android uses Material Design.
Do not build an iOS-looking app on Android or vice versa.

A user on iOS expects swipe-back navigation. A user on Android
expects the back button. Both must work.

### 9.2 Respect Safe Areas

Notches, dynamic islands, and home indicators. Use the platform's
safe area APIs. Never draw under the status bar or the home
indicator.

BAD: A fixed header at `top: 0`.

GOOD: A header inside the safe area.

### 9.3 Touch Targets

Minimum 44x44 points on iOS, 48x48 dp on Android. Small targets
cause mis-taps.

### 9.4 System Gestures

Do not interfere with system gestures (swipe from edge, pull down
for control center). A custom gesture that conflicts with the
system is a bug.

### 9.5 System Font Size

A user who increased the system font size expects the app to
respect it. Layouts must not break when text is scaled to 200%.

### 9.6 System Dark Mode

If the OS is in dark mode, the app respects it (or explicitly opts
out with a user setting). Hardcoded light-only styling is a
convention violation.

## 10. App Store Compliance

### 10.1 In-App Purchases for Digital Goods

Apple and Google require their in-app purchase systems for digital
goods. Linking to an external payment page violates the guidelines.

### 10.2 No Placeholder Content

Reviewers reject apps with "Lorem ipsum" or obviously unfinished
content. Every screen in the build is production-ready.

### 10.3 Privacy Manifest and Data Disclosure

Both stores require a privacy disclosure listing the data collected
and its use. Match the manifest to the actual behavior.

### 10.4 Account Deletion (Apple)

Apple requires apps with account creation to offer account deletion
in-app. Google has similar requirements. The deletion path must be
discoverable.

### 10.5 Permission Usage Descriptions

Covered in 4.6.

### 10.6 No Private APIs

Using private iOS APIs or reflection into system frameworks causes
rejection and can cause crashes on OS updates.

### 10.7 Age Rating Accuracy

The age rating matches the content. A mislabeled app is removed.

## 11. Anti-Patterns

### 11.1 Permission Request at Startup

Covered in 4.1.

### 11.2 Assuming Network

Covered in 5.1.

### 11.3 Blocking the UI Thread

Covered in 8.6.

### 11.4 Storing Tokens in Plain Storage

Covered in 6.2.

### 11.5 No Offline State

Covered in 5.3.

### 11.6 Hard-Coded Layouts for One Screen Size

BAD: Fixed positions that assume a 390x844 viewport.

GOOD: Constraint-based or flex layouts that adapt.

### 11.7 Ignoring the Back Button (Android)

Covered in 3.6.

### 11.8 No Loading State on Slow Operations

A frozen screen with no feedback looks like a crash.

### 11.9 Push Notifications Without Opt-Out

Covered in 7.4.

### 11.10 Silent Failures

BAD: `try { ... } catch (e) {}` in a data sync path.

GOOD: Log the failure, queue the retry, inform the user if
user-visible.

### 11.11 No Update Path for Storage Schema

Covered in 6.5.

### 11.12 Untested on Real Devices

Covered in 8.1.

### 11.13 Synchronous Network Calls on the Main Thread

`URLSession` with `sendSynchronousRequest`, `HttpURLConnection`
without a thread. Both block the UI.

### 11.14 No Deep Link Handling

Covered in 3.5.

### 11.15 No Badge Clearing

A badge count that never decreases. Users see a permanent
notification indicator.

### 11.16 Storing Secrets in the Bundle

An API key in the app binary is extractable by anyone who downloads
the app.

BAD: `const API_KEY = "sk-..."` in the app source.

GOOD: A server-side proxy that holds the key.

### 11.17 Ignoring System Dark Mode

Covered in 9.6.

### 11.18 No App State Restoration

A user who backgrounds the app and returns to a reset screen. iOS
and Android both provide restoration APIs.

### 11.19 Requesting Background Location Without a Reason

Background location is heavily audited. Requesting it without a
documented user benefit causes rejection and distrust.

### 11.20 Using the Wrong Permission Type

BAD: Requesting `READ_CONTACTS` when only one contact is needed.

GOOD: The system contact picker, which requires no permission.

### 11.21 No Handling for Interrupted Downloads

A download that fails on a network switch is retried from scratch.
Use the platform's resumable download API.

### 11.22 Using `UIWebView` (iOS)

`UIWebView` is deprecated and removed. Use `WKWebView`.

### 11.23 No Android 13+ Notification Permission Handling

Android 13 introduced `POST_NOTIFICATIONS` as a runtime permission.
Not handling it means notifications are silently blocked.

### 11.24 Ignoring `onTrimMemory` (Android)

Android signals memory pressure. Not responding means the OS kills
the app harder.

### 11.25 No Crash Reporting

A crash without a report is a bug the developer never sees. Use
the platform's or a third-party crash reporter.

### 11.26 Using `SharedPreferences` for Complex Data

`SharedPreferences` is for small key-value pairs. Complex data
belongs in a database.

### 11.27 No Certificate Pinning for Sensitive Apps

An app handling financial or health data without certificate
pinning is vulnerable to MITM on untrusted networks. See the
security concern file for details.

### 11.28 Ignoring Accessibility Services

TalkBack and VoiceOver must be tested. A custom widget without
accessibility labels is invisible to screen readers.

### 11.29 No Rating Prompt Strategy

Asking for a review at the wrong moment (during onboarding, after
a crash) is ineffective and annoying. Use `SKStoreReviewController`
or the Play In-App Review API at a positive moment.

### 11.30 Assuming a Specific Screen Density

Assets that only ship in one density appear blurry or oversized on
other devices.

### 11.31 Ignoring `applicationDidEnterBackground` Timing

iOS gives the app a few seconds to save state before termination.
Long work there is killed. Use `beginBackgroundTask` for extended
work.

### 11.32 No Handling for Time Zone Changes

A user who travels across time zones sees wrong times unless the
app uses the system time zone or an explicit one.

### 11.33 Trusting Device Time

A user can change the device clock. Never use device time for
security decisions (token expiry, session duration). Use server
time.

### 11.34 No Localization

Strings hardcoded in code. Localization added at the end costs ten
times more.

### 11.35 No Screenshot Protection for Sensitive Screens

Financial apps should blur or block screenshots on sensitive
screens. The platform provides APIs for this.

## 12. Response to Violation

If a previous response violated a rule here:

```
In the previous response, [specific rule] was violated. Correction:
[corrected code]
```

No justification. No apology paragraph. Fix and move on.
