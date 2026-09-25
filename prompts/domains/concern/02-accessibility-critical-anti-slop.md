---
id: 02-accessibility-critical-anti-slop
title: "Accessibility-Critical Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md"]
category: domain
domain_type: concern
version: 2
---

# Accessibility-Critical Anti-Slop Layer

This file defines behavioral contracts specific to accessibility-critical projects. It sits in the concern layer, below the universal anti-slop rules and alongside other cross-cutting concerns. It covers WCAG 2.2 compliance, semantic HTML, keyboard accessibility, visual accessibility, screen reader support, forms, interactive components, content accessibility, and testing methodology. It does not cover the baseline accessibility rules already defined in `00-master-anti-slop.md` (MAS-039), delivery-specific UI patterns (see delivery files), framework-specific component libraries (see framework files), or visual design tokens (see `04-ui-design-system.md`).

For most projects, the baseline accessibility rules in the frontend delivery layer are sufficient. This file is for the subset of projects where keyboard-only users, screen-reader users, or users with low vision are a first-class audience.

## When This File Applies

This file MUST be sent when at least one of the following objective criteria is met:

- The project is a public-facing service with a legal accessibility obligation (government, public sector).
- The project's audience includes assistive-technology users by design (education, healthcare, government).
- The project is a component library that other teams will build accessible products on.
- The project has committed to WCAG 2.2 AA or higher compliance.
- The project has received accessibility complaints or is under an accessibility audit.
- The project is subject to Section 508, the European Accessibility Act, ADA, or equivalent regulations.

This file does NOT apply to: internal tools with no public audience, prototype projects with no compliance requirement, marketing sites with no interactive content, or projects where the baseline delivery-layer rules suffice. Sending this file for every project dilutes its signal.

## Scope

This file applies to web applications, single-page applications, component libraries, and web-based products built with HTML, CSS, and JavaScript (or TypeScript). The examples use HTML, CSS, and JSX where illustrative. Framework-specific accessibility APIs (React Aria, Vue A11y, Angular CDK) live in framework files. Native mobile accessibility (VoiceOver, TalkBack, Accessibility Services) lives in `02-mobile-anti-slop.md`.

The concern is cross-cutting: rules in this file apply to frontend applications, component libraries, web-based desktop apps, and browser extensions equally, wherever the applicability criteria above are met.

## Concern Budgets

Accessibility-critical projects MUST operate within these measurable thresholds:

| Concern | Threshold | Verification Method | Rule |
|---|---|---|---|
| Body Text Contrast | >= 4.5:1 against background | axe-core, WebAIM Contrast Checker | A11Y-022 |
| Large Text Contrast (18pt+ or 14pt bold+) | >= 3:1 | axe-core | A11Y-022 |
| UI Component Contrast (borders, icons) | >= 3:1 | axe-core | A11Y-022 |
| Focus Indicator Contrast | >= 3:1 against adjacent colors | axe-core, Figma inspector | A11Y-025 |
| Text Resize | Functional at 200% zoom | Browser zoom test (WCAG 1.4.4) | A11Y-026 |
| Reflow Width | No horizontal scroll at 320 CSS px | Browser resize (WCAG 1.4.10) | A11Y-027 |
| Flash Rate | < 3 flashes per second | PEAT tool (WCAG 2.3.1) | A11Y-029 |
| Time Limit Warning | >= 20 seconds before timeout | Code review (WCAG 2.2.1) | A11Y-045 |
| Auto-Play Media Duration | <= 3s or has pause control | Manual test (WCAG 1.4.2) | A11Y-075 |
| Automated Test Coverage | Run on every PR, block on critical issues | axe-core in CI | A11Y-063 |

## Rule Severity

Severity follows `_universal/00-style-guide.md`. Violations in this file range from critical (focus traps, missing form labels) to significant (contrast, landmark structure).

## Contracts

An accessibility-critical project commits to seven contracts aligned with the WCAG 2.2 principles. The table below maps each contract to the rules that enforce it.

| Contract | WCAG Principle | Description | Enforced By |
|---|---|---|---|
| Semantic Foundation | Robust | Native HTML elements are preferred over ARIA re-implementations. | A11Y-006 to A11Y-010 |
| Keyboard Operability | Operable | Every interaction is reachable and usable with keyboard only. | A11Y-011 to A11Y-020 |
| Visual Perception | Perceivable | Contrast, resize, reflow, motion, and focus are accessible. | A11Y-021 to A11Y-029 |
| Screen Reader Compatibility | Perceivable + Robust | Content is announced correctly, landmarks and labels are meaningful. | A11Y-030 to A11Y-040 |
| Form Accessibility | Understandable | Inputs are labeled, errors are associated, required fields are announced. | A11Y-041 to A11Y-047 |
| Interactive Component Patterns | Operable + Robust | Modals, menus, tabs, and comboboxes follow WAI-ARIA patterns. | A11Y-048 to A11Y-055 |
| Content Integrity | Understandable | Language, titles, links, and media are accessible. | A11Y-056 to A11Y-062 |

## WCAG 2.2 Framework

### A11Y-001 — Four Principles Alignment

**MUST**

Every accessibility rule in this file MUST trace back to one of the four WCAG principles:

- **Perceivable**: users can perceive the content.
- **Operable**: users can operate the interface.
- **Understandable**: users can understand the content and interface behavior.
- **Robust**: content works with current and future assistive technologies.

### A11Y-002 — Conformance Level Declaration

**MUST**

The target conformance level MUST be declared: A (minimum), AA (default for this file and most regulations), or AAA (only when the project has committed to it). The project MUST NOT claim a level without verifying it. If unsure, the project MUST state which criteria are satisfied and which are not.

### A11Y-003 — Success Criteria Testability

**MUST**

Every WCAG success criterion is testable with a pass/fail procedure. Accessibility claims MUST be backed by specific success criteria, not by a feeling. Changes MUST report which criteria they affect.

### A11Y-004 — Baseline vs Enhanced

**MUST**

The baseline accessibility rules in `00-master-anti-slop.md` (MAS-039) and the frontend delivery layer MUST be followed regardless of whether this file applies. This file specializes and extends those rules for accessibility-critical contexts; it does not replace them.

## Semantic HTML First

### A11Y-005 — Native Element Preference

**MUST**

Before reaching for ARIA, the native HTML element that already has the required behavior MUST be used:

| Need | Native Element |
|---|---|
| Button | `<button>` |
| Link | `<a href="...">` |
| Text input | `<input type="text">` |
| Checkbox | `<input type="checkbox">` |
| Radio group | `<fieldset>` + `<input type="radio">` |
| Dropdown | `<select>` |
| Modal dialog | `<dialog>` (where supported) |
| Disclosure | `<details>` / `<summary>` |
| Progress | `<progress>` |

Native elements come with keyboard behavior, focus management, and screen-reader support for free.

### A11Y-006 — First Rule of ARIA

**MUST NOT**

ARIA MUST NOT be used when a native HTML element or attribute with the required semantics and behavior already exists. ARIA is a fallback, not a default. Adding ARIA to elements that already have correct semantics creates maintenance burden and potential bugs.

### A11Y-007 — No Fake Buttons

**MUST NOT**

`<div role="button">` with manual `tabindex` and `onclick` MUST NOT be used. It requires manually implementing keyboard activation (Enter and Space), focus styles, and disabled state, each of which is a common bug. `<button>` MUST be used.

Example (illustrative, HTML):

BAD:
```html
<div role="button" tabindex="0" onclick="save()">Save</div>
```

GOOD:
```html
<button onclick="save()">Save</button>
```

### A11Y-008 — No Click Handlers on Non-Interactive Elements

**MUST NOT**

Click handlers on `<div>` or `<span>` elements MUST NOT be used. A `<button>`, `<a>`, or element with `role="button"` and full keyboard support MUST be used. Linters that flag this MUST NOT be disabled.

### A11Y-009 — Semantic Landmarks

**MUST**

Semantic landmarks (`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`) MUST be used. `role="search"` MUST be used for the search region. `role="form"` MUST be used for forms not inside a `<form>` landmark. Landmarks help screen-reader users jump to sections.

### A11Y-010 — Heading Hierarchy

**MUST**

One `<h1>` per page MUST exist. Heading levels MUST NOT be skipped (e.g., `<h2>` followed by `<h4>` is wrong). Headings MUST describe the content, not the styling. Headings MUST NOT be used for font size alone.

## Keyboard Accessibility

### A11Y-011 — Keyboard Reachability

**MUST**

Every interactive element MUST be reachable and usable with keyboard only: Tab to move, Shift+Tab to go back, Enter or Space to activate, arrow keys within composite widgets.

See MAS-039 in `_universal/00-master-anti-slop.md`.

### A11Y-012 — No Positive tabindex

**MUST NOT**

Positive `tabindex` values (`tabindex="1"`, `tabindex="2"`) MUST NOT be used. They override the natural document order and are unmaintainable. `tabindex="0"` MUST be used to make a custom element focusable; `tabindex="-1"` MUST be used to make it programmatically focusable but not tab-reachable.

### A11Y-013 — Focus Outline Preservation

**MUST NOT**

Focus outlines MUST NOT be removed without a replacement that meets contrast and visibility requirements. The `:focus-visible` pseudo-class is the correct default.

Example (illustrative, CSS):

BAD:
```css
*:focus { outline: none; }
```

GOOD:
```css
:focus-visible {
  outline: 2px solid var(--focus-color);
  outline-offset: 2px;
}
```

### A11Y-014 — Focus Order Alignment

**MUST**

Tab order MUST follow the visual and logical order of the page. If Tab jumps around, the DOM order does not match the design. The DOM MUST be fixed, not the tabindex.

### A11Y-015 — Single Tab Stop for Composite Widgets

**MUST**

Composite widgets (menus, listboxes, grids, tab strips) MUST have a single Tab stop for the whole widget. Arrow keys MUST be used to navigate within. Every item MUST NOT be placed in the Tab order.

### A11Y-016 — Focus Management on SPA Navigation

**MUST**

When a single-page application navigates, focus MUST move to a sensible place (the new page's heading, the main landmark). Focus MUST NOT stay on the old link, forcing the user to Tab through everything again.

### A11Y-017 — Modal Focus Trap

**MUST**

A modal dialog MUST trap focus until it closes. Focus MUST return to the element that opened it. Escape MUST close it (unless the dialog is destructive and requires an explicit choice).

### A11Y-018 — Skip Links

**MUST**

Every page with repeated navigation MUST have a "Skip to content" link as the first focusable element. The link MUST be hidden visually but become visible on focus.

Example (illustrative, HTML + CSS):

BAD:
```html
<a href="#main" class="sr-only">Skip</a>
```

GOOD:
```html
<a href="#main" class="skip-link">Skip to content</a>
```
```css
.skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  left: 1rem;
  top: 1rem;
  z-index: 100;
}
```

### A11Y-019 — No Keyboard Traps

**MUST NOT**

Outside of intentional modals, focus MUST NEVER be trapped. A user MUST always be able to Tab out of any element.

### A11Y-020 — Global Keyboard Shortcut Discipline

**MUST**

Single-character shortcuts (letters, digits) without modifiers MUST be disableable, remappable, or active only when the relevant element has focus (WCAG 2.1 SC 2.1.4).

## Visual Accessibility

### A11Y-021 — Contrast Requirements

**MUST**

Contrast ratios MUST meet WCAG 2.2 AA thresholds:

- Body text: >= 4.5:1 against background.
- Large text (18 pt or 14 pt bold): >= 3:1.
- UI components (borders, icons conveying meaning): >= 3:1.
- Focus indicators: >= 3:1 against adjacent colors.

Contrast MUST be verified with a tool, not by eye. Designers and developers routinely misjudge contrast.

### A11Y-022 — No Color Alone

**MUST NOT**

Color MUST NOT be the only way to convey information. Errors MUST combine color with an icon and text. Success states MUST do the same. Required fields MUST use an asterisk plus a legend or explicit text. Chart lines MUST use distinct patterns, not just distinct colors. Links in body text MUST be underlined in addition to colored.

### A11Y-023 — Text Over Images

**MUST**

Text over a background image MUST maintain contrast regardless of the image. A solid overlay, a gradient with sufficient opacity, or a solid panel MUST be used.

### A11Y-024 — Focus Indicator Visibility

**MUST**

The focus indicator MUST be visible on every background, MUST NOT rely on the browser's default alone if it is too subtle, and MUST meet 3:1 contrast against adjacent colors. WCAG 2.2 SC 2.4.11 (Focus Not Obscured, Minimum) requires that the focused element is not entirely hidden by sticky headers, footers, or floating toolbars.

### A11Y-025 — Text Resize

**MUST**

Text MUST remain readable and functional at 200% zoom without loss of content or functionality (WCAG 1.4.4). Testing MUST use browser zoom, not just a larger font size.

### A11Y-026 — Reflow at 320px Width

**MUST**

Content MUST reflow without a horizontal scrollbar at a viewport width of 320 CSS pixels (WCAG 1.4.10). This is equivalent to 400% zoom on a 1280px screen.

### A11Y-027 — Reduced Motion Respect

**MUST**

The user's `prefers-reduced-motion` preference MUST be respected. Animations MUST NOT be disabled unconditionally in the base stylesheet; the media query MUST be used.

Example (illustrative, CSS):
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### A11Y-028 — No Flashing Content

**MUST NOT**

Nothing MUST flash more than three times per second (WCAG 2.3.1). This applies to animated GIFs, videos, and CSS animations.

## Screen Reader Support

### A11Y-029 — Meaningful Alt Text

**MUST**

Alt text MUST match the image's role:

- **Informative**: describes the information it conveys.
- **Decorative**: `alt=""` (empty, not missing).
- **Functional** (inside a button): describes the action, not the image.
- **Complex** (chart, diagram): short alt plus a longer description nearby or in `aria-describedby`.

Alt text like `alt="image"`, `alt="icon"`, `alt="logo.png"` is prohibited.

### A11Y-030 — Input Labels

**MUST**

Every input MUST have a `<label>` associated via `for`/`id`. Placeholder text is not a label; it disappears on typing and is not reliably announced. If a visible label is not possible, `aria-label` or `aria-labelledby` MUST be used.

Example (illustrative, HTML):

BAD:
```html
<input placeholder="Email">
```

GOOD:
```html
<label for="email">Email</label>
<input id="email" type="email" placeholder="you@example.com">
```

### A11Y-031 — Error Association

**MUST**

Form errors MUST be associated with the input via `aria-describedby` and `aria-invalid`.

Example (illustrative, HTML):
```html
<label for="email">Email</label>
<input id="email" type="email" aria-invalid="true" aria-describedby="email-error">
<p id="email-error" role="alert">Enter a valid email address.</p>
```

### A11Y-032 — Live Region Discipline

**MUST**

Dynamic content changes (messages, status updates, validation results) MUST be announced via live regions:

- `aria-live="polite"` for non-urgent updates.
- `aria-live="assertive"` for errors and time-sensitive alerts.
- `role="status"` and `role="alert"` as shorthand.

Live regions MUST NOT be overused; every announcement interrupts the user's current reading.

### A11Y-033 — No Redundant Announcements

**MUST NOT**

`aria-label` MUST NOT duplicate the visible text of an element. Screen readers announce both; the duplication is noise.

Example (illustrative, HTML):

BAD:
```html
<button aria-label="Click Save">Save</button>
```

GOOD:
```html
<button>Save</button>
```

Labels are needed only when the visible text is not descriptive (e.g., icon-only buttons).

### A11Y-034 — Icon-Only Button Naming

**MUST**

Every icon-only button MUST have an accessible name via `aria-label`. The SVG inside MUST have `aria-hidden="true"` so the screen reader does not announce the file name or `<title>`.

Example (illustrative, HTML):
```html
<button aria-label="Close dialog">
  <svg aria-hidden="true">...</svg>
</button>
```

### A11Y-035 — Decorative Icon Hiding

**MUST**

Decorative icons next to text MUST have `aria-hidden="true"`. Otherwise the screen reader may announce the SVG's `<title>` or the file name.

### A11Y-036 — Table Semantics

**MUST**

`<table>` MUST be used for tabular data, not for layout. `<th>` MUST have `scope="col"` or `scope="row"`. `<caption>` MUST be used for a table title. `role="presentation"` MUST NOT be used on a data table.

## Forms

### A11Y-037 — Grouped Inputs

**MUST**

Radio buttons and checkboxes in a group MUST be wrapped in `<fieldset>` with a `<legend>`.

### A11Y-038 — Required Field Announcement

**MUST**

"Required" MUST be communicated in the label, not only via an asterisk. Either `aria-required="true"` MUST be set on the input, or the label MUST include a screen-reader-only "(required)" text.

Example (illustrative, HTML):
```html
<label for="email">Email <span aria-hidden="true">*</span>
  <span class="sr-only">(required)</span></label>
```

### A11Y-039 — Specific Actionable Errors

**MUST**

Error messages MUST tell the user what to do. Vague messages like "Invalid input" are prohibited; specific messages like "Email must contain an @ sign" MUST be used.

### A11Y-040 — Error Summary for Long Forms

**SHOULD**

For forms with more than five fields, an error summary at the top linking to each invalid field SHOULD be provided. This is standard for government and financial services.

### A11Y-041 — Time Limit Warnings

**MUST**

If a form times out, the user MUST be warned at least 20 seconds before and MUST be offered a way to extend (WCAG 2.2.1).

### A11Y-042 — Autocomplete Attributes

**MUST**

Standard `autocomplete` values (`email`, `name`, `tel`, `current-password`, `new-password`, `one-time-code`) MUST be used so password managers and assistive technologies can fill forms correctly.

### A11Y-043 — Placeholder as Label Prohibition

**MUST NOT**

Placeholders MUST NOT be used as labels. They disappear on typing and are not reliably announced by screen readers. See A11Y-030.

## Interactive Components

### A11Y-044 — Modal Pattern

**MUST**

A modal dialog MUST:

- Have `role="dialog"` (or use `<dialog>`).
- Have `aria-modal="true"`.
- Have an accessible name via `aria-labelledby`.
- Trap focus while open.
- Close on Escape (unless destructive).
- Return focus to the trigger on close.
- Block interaction with the rest of the page (via `inert` on the background or `aria-hidden` on siblings as fallback).

### A11Y-045 — Menu Pattern

**MUST**

A menu is a composite widget and MUST have:

- One Tab stop (the trigger).
- Arrow keys to move between items.
- Enter or Space to activate.
- Escape to close and return focus to the trigger.
- Home and End to jump to first and last items.

A menu MUST NOT be implemented as a `<div>` with `onclick` handlers on each item.

### A11Y-046 — Tabs Pattern

**MUST**

The WAI-ARIA tabs pattern MUST be followed:

- `role="tablist"` on the container.
- `role="tab"` on each tab, with `aria-selected` and `aria-controls`.
- `role="tabpanel"` on each panel, with `aria-labelledby`.
- Arrow keys navigate tabs; Tab moves to the panel.
- Only the active tab is `tabindex="0"`; others are `tabindex="-1"`.

### A11Y-047 — Tooltip Discipline

**MUST**

A tooltip MUST be triggered by hover or focus, not by click alone. It MUST be dismissable with Escape. It MUST NOT contain interactive content (use a popover for that).

### A11Y-048 — Accordion Pattern

**MUST**

Each accordion header MUST be a `<button>` with `aria-expanded`. The content panel MUST be associated via `aria-controls`. The panel MUST be hidden from assistive technology when collapsed (via `hidden` or `display: none`).

### A11Y-049 — Combobox Pattern

**MUST**

Comboboxes MUST follow the WAI-ARIA combobox pattern. This is a complex widget; the project's component library or a well-tested library MUST be used. Building one from scratch without a strong reason is prohibited.

### A11Y-050 — Drag and Drop Keyboard Equivalent

**MUST**

Every drag-and-drop interaction MUST have a keyboard equivalent (buttons, menu, keyboard shortcuts). Dragging with a mouse alone is not accessible.

## Content

### A11Y-051 — Language Declaration

**MUST**

The `<html>` element MUST have a `lang` attribute set to the correct language. Passages in a different language MUST be wrapped with `lang="..."`.

### A11Y-052 — Page Titles

**MUST**

Every page MUST have a unique, descriptive `<title>`. This is the first thing a screen reader announces. Generic titles like `<title>App</title>` are prohibited.

Example (illustrative, HTML):

BAD: `<title>App</title>`

GOOD: `<title>Order #1234 — Acme Store</title>`

### A11Y-053 — Link Text Describes Destination

**MUST NOT**

Generic link text like "Click here", "Read more", "Learn more" MUST NOT be used. Descriptive text like "Read the installation guide", "View order #1234" MUST be used. Screen readers can list all links on a page; "Click here" repeated many times is useless in that list.

### A11Y-054 — No Images of Text

**MUST NOT**

Text MUST NOT be rendered as an image. Text as an image does not resize, does not reflow, and is not readable by screen readers. Real text with real fonts MUST be used. Logos and brand marks are the only exception.

### A11Y-055 — Media Alternatives

**MUST**

Media MUST have alternatives per WCAG:

- **Video (pre-recorded)**: captions (1.2.2).
- **Video (live)**: captions (1.2.4).
- **Audio-only**: transcript (1.2.1).
- **Video with audio (pre-recorded, AA)**: audio description for visual content (1.2.5).

### A11Y-056 — No Hover-Only Content

**MUST NOT**

Information revealed only on hover MUST NOT be used. A focus-triggered or click-triggered equivalent MUST be provided for keyboard and touch users.

## Testing

### A11Y-057 — Automated Testing as Baseline

**MUST**

Automated tools (axe-core, Lighthouse, pa11y) MUST be run in CI. They catch approximately 30% of issues (missing labels, contrast, structural problems). They do NOT catch focus order, screen-reader experience, keyboard interaction in custom widgets, or cognitive clarity. A passing automated test MUST NOT be claimed as proof of full accessibility.

### A11Y-058 — Keyboard-Only Walkthrough

**MUST**

Every user flow MUST be tested with the mouse unplugged: Tab, Shift+Tab, Enter, Space, arrow keys, and Escape. Every step MUST work.

### A11Y-059 — Screen Reader Testing

**MUST**

The project MUST be tested with at least one screen reader: NVDA (Windows, free), JAWS (Windows, commercial), VoiceOver (macOS/iOS, built-in), TalkBack (Android, built-in), or Orca (Linux). Behavior varies across screen readers.

### A11Y-060 — Zoom Testing

**MUST**

The project MUST be tested at 200% browser zoom (no loss of function) and at 400% zoom on a 1280px viewport (equivalent to 320px width; no horizontal scroll, content reflows).

### A11Y-061 — Color Blindness Simulation

**MUST**

Protanopia, deuteranopia, and tritanopia MUST be simulated. No information MUST be lost. Red/green distinctions alone are prohibited.

### A11Y-062 — User Testing

**SHOULD**

Testing with actual assistive-technology users SHOULD be performed when possible. Automated testing and developer walkthroughs miss the friction that real users experience. If user testing is not possible, the limitation MUST be documented.

## AI-Specific Accessibility Discipline

### A11Y-080 — ARIA Attribute Verification

**MUST**

Before using an ARIA role, state, or property, the assistant MUST verify it is valid for the target element and is used correctly per the WAI-ARIA specification. Invented or misused ARIA attributes produce silent regressions that automated tools may not catch.

See MAS-036 in `_universal/00-master-anti-slop.md`.

### A11Y-081 — Existing Accessible Component Discovery

**MUST**

Before building a new accessible interactive component (modal, combobox, tabs), the assistant MUST search the project for an existing accessible implementation. Inventing parallel components creates inconsistent accessibility behavior across the product.

See MAS-035 in `_universal/00-master-anti-slop.md`.

### A11Y-082 — Native Element Preference Enforcement

**MUST**

Before suggesting a custom interactive element with ARIA roles, the assistant MUST verify that no native HTML element already provides the required semantics and behavior. This specializes A11Y-006 for the AI code generation context, where AI frequently generates `div role="button"` patterns.

## Anti-Patterns

### A11Y-063 — ARIA Everywhere

**MUST NOT**

Adding `role`, `aria-label`, or `aria-describedby` to elements that already have correct semantics is prohibited. Every ARIA attribute is a maintenance burden and a potential bug. The native element MUST be used first; ARIA only when native is impossible.

### A11Y-064 — aria-label Contradicting Visible Text

**MUST NOT**

`aria-label` MUST NOT contradict the visible text of an element. The `aria-label` MUST either match or be a superset of the visible text (WCAG 2.5.3 Label in Name). Voice control users cannot activate elements reliably when the announced name differs from the visible label.

Example (illustrative, HTML):

BAD:
```html
<button aria-label="Delete">Save</button>
```

### A11Y-065 — aria-hidden on Focusable Elements

**MUST NOT**

A focusable element MUST NOT have `aria-hidden="true"`. When focused, screen-reader users get silence, which is a severe bug.

Example (illustrative, HTML):

BAD:
```html
<button aria-hidden="true">Close</button>
```

### A11Y-066 — Global outline: none Reset

**MUST NOT**

A global `* { outline: none; }` reset is the single most common accessibility regression in modern frontends. It disables the only visual indicator keyboard users have and MUST NOT be used.

### A11Y-067 — Custom Widgets Without Keyboard Support

**MUST NOT**

A `<div>` that behaves like a dropdown but only responds to click, or a custom date picker that requires a mouse, is prohibited. Every custom widget MUST implement the full keyboard interaction pattern.

### A11Y-068 — Poor Disabled Element Contrast

**MUST NOT**

Disabled elements are still content. Users with low vision MUST be able to read them, and users MUST be able to tell what is disabled. A disabled state with less than 3:1 contrast fails.

### A11Y-069 — Placeholder Color as Only Cue

**MUST NOT**

Placeholder text is not a substitute for a label and is often too low contrast to read. It MUST NOT be used as the only visual cue for a required or invalid field.

### A11Y-070 — Toast-Only Errors

**MUST NOT**

A toast that disappears after a few seconds is a problem for users who read slowly, use screen readers, or have cognitive disabilities. Errors MUST persist until dismissed or until the input is corrected.

### A11Y-071 — No Focus Management in SPAs

**MUST NOT**

After a route change, focus MUST NOT stay on the old page's element. Screen readers MUST announce the new content; the user MUST NOT have to Tab from the top of the page again.

### A11Y-072 — Missing Language Declaration

**MUST NOT**

A page without `<html lang>` may be read with the wrong pronunciation rules. For non-English content, this is unusable. The `lang` attribute MUST always be set.

### A11Y-073 — Heading Order Reversed for Styling

**MUST NOT**

Using `<h3>` because it looks the right size, not because the content is at that level, breaks the document outline and MUST NOT be done.

### A11Y-074 — Empty Alt on Functional Images

**MUST NOT**

An image inside a button MUST NOT have an empty `alt` attribute. The screen reader will announce "button" with no name.

Example (illustrative, HTML):

BAD:
```html
<button>
  <img src="trash.svg" alt="">
</button>
```

GOOD:
```html
<button>
  <img src="trash.svg" alt="Delete">
</button>
```

### A11Y-075 — Auto-Playing Media

**MUST NOT**

Auto-playing audio or video interferes with screen readers. If the media plays for more than three seconds, it MUST have a pause control (WCAG 1.4.2).

### A11Y-076 — Moving Content Without Pause

**MUST**

Carousels, tickers, and auto-advancing content MUST be pausable (WCAG 2.2.2).

## Response to Violation

When a rule in this file is violated, report:

Violation: A11Y-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

If the violation is in already-shipped code, the correction MUST be accompanied by:

> "This may require an accessibility audit of related components. The same pattern is likely repeated elsewhere."

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.