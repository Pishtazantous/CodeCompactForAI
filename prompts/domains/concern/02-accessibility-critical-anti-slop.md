--
id: 02-accessibility-critical-anti-slop
title: "Accessibility-Critical Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: concern
version: 1
---

# Accessibility-Critical Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file is sent for projects where accessibility is a first-class
requirement, not a checkbox: public-sector services, healthcare,
financial products with regulatory requirements, education, and any
product that must comply with WCAG 2.2 AA or higher, or with
regulations such as Section 508, the European Accessibility Act, or
the ADA.

For most projects, the baseline accessibility rules in
`domains/delivery/02-frontend-anti-slop.md` section 10 are sufficient.
This file is for the subset of projects where keyboard-only users,
screen-reader users, or users with low vision are a first-class
audience.

## 1. When This File Applies

Send this file when the project is:

- A public-facing service with a legal accessibility obligation.
- A product whose audience includes assistive-technology users by
  design (education, healthcare, government).
- A component library that other teams will build on.
- A project that has committed to WCAG 2.2 AA or higher.
- A project that has received accessibility complaints or is under
  audit.

If none of these apply, the baseline in the frontend delivery layer
is enough. Sending this file for every project dilutes its signal.

## 2. WCAG 2.2 Framework

### 2.1 The Four Principles

WCAG organizes criteria under four principles. Every rule in this
file traces back to one of them:

- **Perceivable** -- users can perceive the content.
- **Operable** -- users can operate the interface.
- **Understandable** -- users can understand the content and the
  interface behavior.
- **Robust** -- the content works with current and future
  assistive technologies.

### 2.2 The Three Levels

- **A** -- minimum. Removing these makes the content inaccessible.
- **AA** -- the standard target for most regulations. Default for
  this file.
- **AAA** -- enhanced. Required only when the project has committed
  to it or when the domain demands it.

Do not claim a level without verifying it. If unsure, say which
criteria are satisfied and which are not.

### 2.3 Success Criteria Are Testable

Every criterion has a testing procedure. "Accessible" is not a
feeling; it is a set of pass/fail checks. Report which criteria a
change affects.

## 3. Semantic HTML First

### 3.1 Use the Native Element

Before reaching for ARIA, use the HTML element that already has the
behavior:

| Need | Native element |
|---|---|
| Button | `<button>` |
| Link | `<a href="...">` |
| Text input | `<input type="text">` |
| Checkbox | `<input type="checkbox">` |
| Radio group | `<fieldset>` + `<input type="radio">` |
| Dropdown | `<select>` |
| Modal dialog | `<dialog>` (when supported) or a `role="dialog"` pattern |
| Disclosure | `<details>` / `<summary>` |
| Progress | `<progress>` |
| Tabs | WAI-ARIA tabs pattern (no native equivalent) |
| Tooltip | `title` for simple, WAI-ARIA for rich |

Native elements come with keyboard behavior, focus management, and
screen-reader support for free. ARIA re-implements them at a cost.

### 3.2 First Rule of ARIA

From the WAI-ARIA specification:

> If you can use a native HTML element or attribute with the
> semantics and behavior you require already built in, instead of
> re-purposing an element and adding an ARIA role, state or
> property to make it accessible, then do so.

ARIA is a fallback, not a default.

### 3.3 No `role="button"` on a `<div>`

BAD:
html
<div role="button" tabindex="0" onclick="save()">Save</div>
This requires manually implementing keyboard activation (Enter and
Space), focus styles, and disabled state. Every one of these is a
common bug.

GOOD:

html
<button onclick="save()">Save</button>
3.4 No Click Handlers on Non-Interactive Elements
BAD: <div onclick="..."> or <span onclick="...">.
GOOD: <button>, <a>, or an element with role="button" and full
keyboard support (which is more work than using <button>).

If a click handler is on a <div>, linters should flag it. Do not
disable that rule.

4. Keyboard Accessibility
4.1 Everything Reachable by Keyboard
Every interactive element is reachable and usable with keyboard only:
Tab to move, Shift+Tab to go back, Enter or Space to activate, arrow
keys within composite widgets.

4.2 No Positive tabindex
BAD: tabindex="1", tabindex="2".

Positive values override the natural document order and are
unmaintainable. Use tabindex="0" to make a custom element
focusable, and tabindex="-1" to make it programmatically focusable
but not tab-reachable.

4.3 Never Remove Focus Outlines Without a Replacement
BAD:

css
*:focus { outline: none; }
GOOD:

css
:focus-visible { outline: 2px solid var(--focus-color); outline-offset: 2px; }
The :focus-visible pseudo-class shows the outline for keyboard
users, not mouse users. It is the correct default.

If a design demands a custom indicator, provide one that meets the
contrast and visibility requirements (see 5.4).

4.4 Focus Order Matches Reading Order
Tab order should follow the visual and logical order of the page. If
Tab jumps around, the DOM order does not match the design. Fix the
DOM, not the tabindex.

4.5 Composite Widgets Have a Single Tab Stop
A menu, a listbox, a grid, a tab strip: one Tab stop for the whole
widget, arrow keys within. Do not put every item in the Tab order.

4.6 Focus Management on Navigation
When a single-page application navigates, focus should move to a
sensible place (the new page's heading, the main landmark). Otherwise
the user is left with focus on the old link and must Tab through
everything again.

4.7 Focus Trap in Modals
A modal dialog traps focus until it closes. Focus returns to the
element that opened it. Escape closes (unless the dialog is
destructive and requires an explicit choice).

4.8 Skip Links
Every page with repeated navigation has a "Skip to content" link as
the first focusable element. The link is hidden visually but
focusable:

BAD:

html
<a href="#main" class="sr-only">Skip</a>
If sr-only never becomes visible on focus, the link is invisible
to sighted keyboard users too.

GOOD:

html
<a href="#main" class="skip-link">Skip to content</a>
css
.skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  left: 1rem;
  top: 1rem;
  z-index: 100;
}
4.9 No Keyboard Traps
Outside of intentional modals, focus must never be trapped. A user
must always be able to Tab out of any element.

4.10 Global Keyboard Shortcuts
Single-character shortcuts (letters, digits) without modifiers must
be disableable, remappable, or active only when the relevant element
has focus (WCAG 2.1 SC 2.1.4).

5. Visual Accessibility
5.1 Contrast Requirements
Body text: 4.5:1 against background.

Large text (18 pt or 14 pt bold): 3:1.

UI components (borders, icons that convey meaning): 3:1.

Focus indicators: 3:1 against adjacent colors.

Verify with a tool, not by eye. Designers and developers routinely
misjudge contrast.

5.2 Never Use Color Alone
Color must not be the only way to convey information:

Error: red plus icon plus text.

Success: green plus icon plus text.

Required fields: asterisk plus legend, or explicit "required" text.

Chart lines: distinct patterns, not just distinct colors.

Link in body text: underline plus color.

5.3 Text Over Images
Text over a background image must maintain contrast regardless of the
image. Use a solid overlay, a gradient with sufficient opacity, or
place the text in a solid panel.

5.4 Focus Indicator Visibility
The focus indicator must:

Be visible on every background.

Not rely on the browser's default alone if it is too subtle.

Meet 3:1 contrast against adjacent colors.

WCAG 2.2 SC 2.4.11 (Focus Not Obscured, Minimum) requires that the
focused element is not entirely hidden by sticky headers, footers,
or floating toolbars.

5.5 Text Resize
Text must remain readable and functional at 200% zoom without loss
of content or functionality (WCAG 1.4.4). Test with browser zoom,
not just a larger font size.

5.6 No Horizontal Scroll at 320px Width
Content reflows without a horizontal scrollbar at a viewport width
of 320 CSS pixels (WCAG 1.4.10). This is the equivalent of a 400%
zoom on a 1280px screen.

5.7 Reduced Motion
Respect the user's preference:

css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
Do not disable animations unconditionally in the base stylesheet.
Use the media query.

5.8 No Flashing Content
Nothing flashes more than three times per second (WCAG 2.3.1). This
applies to animated GIFs, videos, and CSS animations.

6. Screen Reader Support
6.1 Meaningful alt Text
Informative image: describes the information it conveys.

Decorative image: alt="" (empty, not missing).

Functional image (inside a button): describes the action, not the
image.

Complex image (chart, diagram): short alt plus a longer
description nearby or in aria-describedby.

BAD: alt="image", alt="icon", alt="logo.png".
GOOD: alt="Sales grew 20% in Q3".

6.2 Labels for Every Input
Every input has a <label> associated with for/id. Placeholder
text is not a label; it disappears on typing and is not reliably
announced.

BAD:

html
<input placeholder="Email">
GOOD:

html
<label for="email">Email</label>
<input id="email" type="email" placeholder="you@example.com">
If a visible label is not possible, use aria-label or
aria-labelledby.

6.3 Error Association
Form errors are associated with the input via aria-describedby and
aria-invalid:

html
<label for="email">Email</label>
<input id="email" type="email" aria-invalid="true"
       aria-describedby="email-error">
<p id="email-error" role="alert">Enter a valid email address.</p>
6.4 Dynamic Content Announced
When content changes asynchronously (a new message, a status update,
a validation result), the change is announced via a live region:

aria-live="polite" for non-urgent updates.

aria-live="assertive" for errors and time-sensitive alerts.

role="status" and role="alert" as shorthand.

Do not overuse live regions. Every announcement interrupts whatever
the user was reading.

6.5 No Redundant Announcements
BAD: <button aria-label="Click Save">Save</button>.
Screen readers read both the aria-label and the visible text.

GOOD: <button>Save</button>.

The label is needed only when the visible text is not descriptive
(icon-only buttons).

6.6 Icon-Only Buttons
Every icon-only button has an accessible name:

html
<button aria-label="Close dialog">
  <svg aria-hidden="true">...</svg>
</button>
The SVG is aria-hidden so the screen reader does not announce it.

6.7 Decorative Icons Are aria-hidden
BAD:

html
<button>
  <svg>...</svg> Save
</button>
The screen reader may announce the SVG's <title> or the file name.

GOOD:

html
<button>
  <svg aria-hidden="true">...</svg> Save
</button>
6.8 Heading Hierarchy
One <h1> per page.

No skipped levels (<h2> then <h4> is wrong).

Headings describe the content, not the styling.

Do not use headings for font size.

6.9 Landmarks
Use semantic landmarks:

<header>, <nav>, <main>, <aside>, <footer>.

role="search" for the search region.

role="form" for a form that is not already inside a <form>
landmark.

Landmarks help screen-reader users jump to sections.

6.10 Tables
Use <table> for tabular data, not for layout.

<th> for headers with scope="col" or scope="row".

<caption> for a table title.

Avoid role="presentation" on a data table.

7. Forms
7.1 Every Input Has a Label
Covered in 6.2.

7.2 Group Related Inputs
Radio buttons and checkboxes in a group are wrapped in
<fieldset> with a <legend>.

7.3 Required Fields Are Announced
Required is communicated in the label, not only via the asterisk:

html
<label for="email">Email <span aria-hidden="true">*</span>
  <span class="sr-only">(required)</span></label>
Or use aria-required="true" on the input.

7.4 Errors Are Specific and Actionable
BAD: "Invalid input."
GOOD: "Email must contain an @ sign."

The error tells the user what to do.

7.5 Error Summary at the Top of Long Forms
For forms with more than five fields, an error summary at the top
links to each invalid field. This is standard for government and
financial services.

7.6 No Time Limits Without Warning
If a form times out, warn the user at least 20 seconds before, and
offer a way to extend (WCAG 2.2.1).

7.7 Autocomplete Attributes
Use the standard autocomplete values (email, name, tel,
current-password, new-password, one-time-code) so password
managers and assistive technologies can fill forms correctly.

8. Interactive Components
8.1 Modals
A modal dialog:

Has role="dialog" (or <dialog>).

Has aria-modal="true".

Has an accessible name via aria-labelledby.

Traps focus while open.

Closes on Escape (unless destructive; then confirm first).

Returns focus to the trigger on close.

Blocks interaction with the rest of the page (visually and for
assistive technology).

inert on the background is the modern approach. aria-hidden on
background siblings is the fallback for older browsers.

8.2 Menus and Dropdowns
A menu is a composite widget. It has:

One Tab stop (the trigger).

Arrow keys to move between items.

Enter or Space to activate.

Escape to close and return focus to the trigger.

Home and End to jump to first and last.

Do not implement a menu as a <div> with onclick handlers on
each item.

8.3 Tabs
The WAI-ARIA tabs pattern:

role="tablist" on the container.

role="tab" on each tab, with aria-selected and
aria-controls.

role="tabpanel" on each panel, with aria-labelledby.

Arrow keys navigate tabs; Tab moves to the panel.

Only the active tab is tabindex="0"; others are tabindex="-1".

8.4 Tooltips
A tooltip is triggered by hover or focus, not by click alone. It is
dismissable with Escape. It does not contain interactive content
(use a popover for that).

8.5 Accordions
Each header is a <button> with aria-expanded. The content panel
is associated via aria-controls. The panel is hidden from
assistive technology when collapsed (via hidden or display: none).

8.6 Comboboxes
Follow the WAI-ARIA combobox pattern. This is a complex widget; use
the project's component library or a well-tested library. Do not
build one from scratch without a strong reason.

8.7 Drag and Drop
Every drag-and-drop interaction has a keyboard equivalent. Dragging
with a mouse is not accessible. Provide buttons, a menu, or keyboard
shortcuts to achieve the same result.

9. Content
9.1 Language Declared
<html lang="en"> (or the correct language). If a passage is in a
different language, wrap it with lang="...".

9.2 Page Titles
Every page has a unique, descriptive <title>. This is the first
thing a screen reader announces.

BAD: <title>App</title>
GOOD: <title>Order #1234 -- Acme Store</title>

9.3 Link Text Describes the Destination
BAD: "Click here", "Read more", "Learn more".
GOOD: "Read the installation guide", "View order #1234".

Screen readers can list all links on a page. "Click here" repeated
12 times is useless in that list.

9.4 No Images of Text
Text as an image does not resize, does not reflow, and is not
readable by screen readers. Use real text with real fonts.

Exception: logos and brand marks, where the text is the design.

9.5 Captions and Transcripts
Video: captions (WCAG 1.2.2 for pre-recorded, 1.2.4 for live).

Audio-only: transcript (WCAG 1.2.1).

Video with audio: audio description for visual content (WCAG
1.2.5 at AA for pre-recorded).

9.6 No Content on Hover Only
Information revealed only on hover is not available to keyboard and
touch users. Provide a focus-triggered equivalent or a
click-triggered one.

10. Testing
10.1 Automated Testing Catches About 30%
Tools like axe-core, Lighthouse, and pa11y catch roughly 30% of
issues. They catch missing labels, contrast, and structural problems.
They do not catch:

Focus order.

Screen-reader experience.

Keyboard interaction in custom widgets.

Cognitive load and clarity.

Never claim a page is accessible because the automated tool passed.

10.2 Keyboard-Only Walkthrough
Unplug the mouse. Navigate the entire flow with Tab, Shift+Tab,
Enter, Space, arrow keys, and Escape. Every step must work.

10.3 Screen-Reader Testing
Test with at least one screen reader:

NVDA (Windows, free)

JAWS (Windows, commercial)

VoiceOver (macOS, iOS, built-in)

TalkBack (Android, built-in)

Orca (Linux)

The experience varies. What works in VoiceOver may fail in NVDA.

10.4 Zoom Testing
200% browser zoom: no loss of function.

400% zoom on a 1280px viewport (equivalent to 320px width): no
horizontal scroll, content reflows.

10.5 Color Blindness Simulation
Simulate protanopia, deuteranopia, tritanopia. Ensure no information
is lost. Do not rely on red/green distinctions.

10.6 Testing With Users
The most reliable test is with actual assistive-technology users.
Automated testing and developer walkthroughs miss the friction that
real users experience.

If the project has access to user testing with disabled users, use
it. If not, at least document the limitation.

11. Accessibility Anti-Patterns
11.1 ARIA Everywhere
Adding role, aria-label, and aria-describedby to elements that
already have correct semantics. Every ARIA attribute is a
maintenance burden and a potential bug.

Use the native element first. ARIA only when native is impossible.

11.2 aria-label That Contradicts Visible Text
BAD:

html
<button aria-label="Delete">Save</button>
Screen readers announce "Delete". Sighted users see "Save". Voice
control users cannot activate it by saying either word reliably.

The aria-label must either match or be a superset of the visible
text (WCAG 2.5.3 Label in Name).

11.3 aria-hidden="true" on Focusable Elements
BAD:

html
<button aria-hidden="true">Close</button>
A focusable element that is aria-hidden is announced as nothing
when focused. Screen-reader users get silence.

11.4 Placeholder as Label
Covered in 6.2. Repeating: placeholders disappear and are not
reliably announced.

11.5 tabindex="0" on a <div> With onclick
Covered in 3.3. This creates a fake button that fails on every
keyboard interaction except maybe Enter.

11.6 Focus Outline Removed
Covered in 4.3. One of the most common accessibility regressions.

11.7 Icon-Only Button Without aria-label
Covered in 6.6.

11.8 Empty Alt on a Functional Image
BAD:

html
<button>
  <img src="trash.svg" alt="">
</button>
The screen reader announces "button" with no name.

GOOD:

html
<button>
  <img src="trash.svg" alt="Delete">
</button>
11.9 role="presentation" on a Data Table
Removing the table semantics from a table that conveys data is a
regression. Use role="presentation" only for tables used for
layout.

11.10 Auto-Playing Media
Auto-playing audio or video interferes with screen readers. If the
media plays for more than three seconds, it must have a pause
control (WCAG 1.4.2).

11.11 Moving Content Without a Pause
Carousels, tickers, and auto-advancing content must be pausable
(WCAG 2.2.2).

11.12 Time-Limited Sessions Without Warning
Covered in 7.6.

11.13 outline: none in a Global Reset
BAD:

css
* { outline: none; }
This is the single most common accessibility regression in modern
frontends. It disables the only visual indicator keyboard users
have.

11.14 Custom Widgets Without Keyboard Support
A <div> that behaves like a dropdown but only responds to click.
A custom date picker that requires a mouse. Every custom widget needs
the full keyboard interaction pattern.

11.15 Poor Contrast on Disabled Elements
Disabled elements are still content. Users with low vision must be
able to read them, and users must be able to tell what is disabled.
A disabled state at 1.5:1 contrast fails.

11.16 Placeholder Color as the Only Cue
The placeholder text is not a substitute for a label, and it is often
too low contrast to read.

11.17 Toast-Only Errors
A toast that disappears after 5 seconds is a problem for users who
read slowly, use screen readers, or have cognitive disabilities. The
error must persist until dismissed or until the input is corrected.

11.18 No Focus Management in Single-Page Apps
After a route change, focus stays on the old page's element. Screen
readers announce nothing new. The user must Tab from the top of the
page again.

11.19 Language Not Declared
A page without <html lang> may be read with the wrong
pronunciation rules. For non-English content, this is unusable.

11.20 Reversed Heading Order for Styling
Using <h3> because it looks the right size, not because the
content is at that level. Breaks the document outline.

12. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

If the violation is in already-shipped code, add a note: "This may
require an accessibility audit of related components. The same
pattern is likely repeated elsewhere."

text

---