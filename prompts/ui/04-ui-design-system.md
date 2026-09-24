--
id: 04-ui-design-system
title: "UI & Design System Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: ui
version: 1
---

# UI & Design System Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) are NOT repeated here.

This file is sent only for projects that have a user interface. It
covers design tokens, component primitives, variants, composition,
visual anti-slop, animation, and bidirectional layouts. It does NOT
cover state, data fetching, or architectural patterns; those live in
`domains/delivery/02-frontend-anti-slop.md` and
`domains/framework/`.

When the project has a design system, this file enforces it. When the
project does not have one, this file prevents inventing one
mid-task.

## 1. Scope

This layer applies to:

- SaaS and consumer web applications.
- Marketing sites with interactive elements.
- Admin dashboards and internal tools.
- Mobile and desktop application UIs.

The principles are framework-agnostic. Framework-specific UI rules
(React, Vue, Svelte component patterns) live in the respective
framework layer. Accessibility rules live in
`domains/concern/02-accessibility-critical-anti-slop.md` when that
file is sent; the baseline is repeated here.

## 2. Reference the Existing Design System First

### 2.1 Find the Tokens Before Writing Any Style

Before writing a color, a spacing value, a font size, or a border
radius:

1. Fetch the project's token source (`tailwind.config`, `theme.ts`,
   CSS custom properties, a design tokens package).
2. Identify the semantic name for what you need (`--color-danger`,
   `--space-4`, `text-lg`).
3. Use that name. Not a raw value.

If a token for the needed value does not exist, report it. Do not add
a new token without permission; the design system is a shared
contract.

### 2.2 Find the Primitive Before Writing Any Component

Before writing a new `Button`, `Input`, `Card`, `Dialog`, `Badge`,
`Tooltip`, or any generic primitive:

1. Search the component directory (`components/ui/`,
   `components/primitives/`, or the project's equivalent).
2. If a primitive exists, use it, even if it is imperfect.
3. If it is close but missing a variant, report the gap before
   extending it.
4. Only create a new primitive when nothing close exists.

### 2.3 Follow the Existing Pattern, Not a Better One You Know

If the project uses `class-variance-authority` for variants, do not
introduce a `styled-components` variant pattern. If the project uses
Tailwind utility classes, do not add a CSS module. Consistency beats
preference.

## 3. Design Tokens

### 3.1 Semantic Tokens Over Raw Values

BAD:
tsx
<div className="bg-red-500 text-white p-4 rounded-lg" />
GOOD:

tsx
<div className="bg-danger text-on-danger p-md rounded-md" />
The semantic name communicates intent and can be re-themed. The raw
value cannot.

3.2 Token Categories
A well-formed design system has tokens for:

Color: background, surface, border, text, primary, danger,
warning, success, info, and their "on-" counterparts for text on
those backgrounds.

Spacing: a scale, typically 4px-based (0, 1, 2, 3, 4, 6, 8, 12, 16, ...).

Typography: font family, size scale, weight scale, line height.

Radius: typically none, sm, md, lg, full.

Shadow: elevation levels, not arbitrary box-shadows.

Motion: duration scale, easing curves.

Every visual property in the project resolves to a token in one of
these categories.

3.3 No Raw Hex, RGB, or HSL in Components
BAD: <div style={{ color: "#3b82f6" }} />
GOOD: <div className="text-primary" />

The only place raw color values appear is in the token definition
file.

3.4 No Magic Spacing Values
BAD: <div className="p-[13px] mt-[7px]" />
GOOD: <div className="p-md mt-sm" />

Arbitrary values break the scale and produce visual drift.

3.5 No Named Colors From the Framework Default
Using red-500, blue-600, gray-300 directly couples the
component to a framework palette. Use the semantic token instead. If
the project has not defined semantic tokens, report the gap.

3.6 No Color Without a Semantic Role
Every color in the system has a role:

primary -- main action color.

danger -- destructive actions and errors.

warning -- caution.

success -- confirmation.

info -- neutral information.

background, surface, elevated -- containers.

border, divider -- separators.

text, text-muted, text-inverse -- typography.

Do not invent a new role ("accent-2", "brand-purple"). If the design
requires one, ask.

4. Component Primitives
4.1 The Primitive Set
A typical design system has:

Button

Input, Textarea, Select, Checkbox, Radio, Switch

Label, FieldError, FieldHint

Card, Panel, Surface

Dialog, Drawer, Sheet, Popover

Tooltip

Tabs, Accordion

Table, List

Badge, Tag, Chip

Avatar

Toast, Alert

Spinner, Skeleton

Progress

Not every project needs all of these. Every project needs whichever
ones it has to be used consistently.

4.2 One Primitive Per Concept
Two Button components (one in ui/, one in features/) is a sign
that the design system is not authoritative. Delete the duplicate and
fix the usage.

4.3 Props Are Minimal and Typed
A primitive exposes the smallest prop surface that covers its use
cases:

BAD:

tsx
<Button
  isPrimary
  isLarge
  hasIcon
  iconPosition="left"
  iconName="save"
  isFullWidth
/>
GOOD:

tsx
<Button variant="primary" size="lg" leadingIcon={<SaveIcon />} fullWidth />
Props describe the visual variation, not the caller's intent.

4.4 No Business Logic in Primitives
A Button does not fetch data. A Card does not navigate. A Dialog
does not know about the domain. Primitives are visual and
interactive; everything else lives above them.

4.5 Forward the Underlying Element's Attributes
Every primitive that wraps a native element forwards ref, onClick,
aria-*, data-*, className, and the element's remaining
attributes. This is what allows consumers to compose without
forking.

5. Variants
5.1 Enumerated Variants, Not Boolean Explosions
BAD:

tsx
<Button isPrimary isGhost isDanger />
GOOD:

tsx
<Button variant="primary" />
<Button variant="ghost" />
<Button variant="danger" />
The variant prop is a discriminated union. Boolean flags for each
variant are unmaintainable and allow impossible combinations.

5.2 The Standard Variant Set
Most projects converge on:

primary -- the main action.

secondary -- a supporting action.

ghost -- a low-emphasis action.

danger -- a destructive action.

link -- a text-only action.

Not all projects need all five. The set is smaller than developers
think.

5.3 Size Is Its Own Prop
size is orthogonal to variant. Do not create primaryLarge and
primarySmall.

5.4 State Is Not a Variant
disabled, loading, pressed, and focused are states, not
variants. A variant describes what the component is; a state
describes what it is doing now.

6. Composition
6.1 Composition Over Configuration
BAD:

tsx
<Card
  title="User"
  subtitle="Details"
  showDivider
  actions={[...]}
  footer={<Button>Save</Button>}
/>
GOOD:

tsx
<Card>
  <Card.Header>
    <Card.Title>User</Card.Title>
    <Card.Subtitle>Details</Card.Subtitle>
  </Card.Header>
  <Card.Body>...</Card.Body>
  <Card.Footer>
    <Button>Save</Button>
  </Card.Footer>
</Card>
Composition lets the caller arrange what they need. Configuration
makes the primitive predict every combination.

6.2 Slots Where Composition Is Awkward
When composition is genuinely awkward (dialogs with many regions,
tables with fixed structure), use named slots:

tsx
<Dialog
  trigger={<Button>Open</Button>}
  title="Confirm"
  body={<p>...</p>}
  footer={<Button>OK</Button>}
/>
Both patterns are valid. Pick the one that fits the component's real
usage.

6.3 asChild or render for Polymorphism
A primitive that must render as different elements uses a
asChild/render prop, not a tag string that changes the props
type:

BAD:

tsx
<Button tag="a" href="/x">Link</Button>  // href not typed, tag not typed
GOOD (Radix-style asChild):

tsx
<Button asChild>
  <a href="/x">Link</a>
</Button>
7. Accessibility Baseline
Detailed accessibility rules live in
domains/concern/02-accessibility-critical-anti-slop.md when that
file is sent. The baseline for every UI component:

7.1 Keyboard
Every interactive element is reachable by Tab.

Every interactive element is activatable by Enter or Space (or the
appropriate key for the element).

Focus order matches the reading order.

7.2 Focus
Focus is visible on every interactive element.

:focus-visible shows an indicator for keyboard users.

Modals trap focus and return it on close.

7.3 Labels
Every input has an associated <label>.

Icon-only buttons have an aria-label.

Errors are associated with the input via aria-describedby.

7.4 Color
Color is never the only signal of state.

Text on backgrounds meets 4.5:1 (or 3:1 for large text).

Focus indicators meet 3:1 against adjacent colors.

7.5 Motion
prefers-reduced-motion is respected.

No content flashes more than three times per second.

8. Visual Anti-Slop
8.1 No Purple-to-Blue Gradient
The default purple-to-blue gradient is the most recognizable visual
cliché of AI-generated interfaces. If the project does not use it,
do not introduce it.

8.2 No Glass Morphism Without Reason
backdrop-blur combined with translucent backgrounds is a stale
trend. Add it only when the project already uses it and the design
calls for it.

8.3 No hover:scale + hover:shadow-2xl Everywhere
A hover effect is a design decision, not a default. Pick one
interaction and use it consistently. Do not stack scale, shadow,
translate, and rotate on every card.

8.4 No transition-all
BAD: transition-all duration-300
GOOD: transition-colors duration-150

transition-all transitions layout, paint, and composite properties
that the user did not intend to animate. Transition specific
properties only.

8.5 No Global animate-pulse
Skeleton loaders are correct for loading content. A pulsing animation
on every element is visual noise.

8.6 No Gradient Text
bg-clip-text text-transparent on headings is a cliché. If the
project does not use it, do not add it.

8.7 No Emoji as UI
BAD: 🎉, ✅, ❌, ⚠️ as icons.
GOOD: SVG icons from the project's icon set (lucide-react,
heroicons, phosphor, or the project's own).

Emoji render differently across platforms, do not scale cleanly, and
are not announced by screen readers as intended.

8.8 No Icons on Every Label
An icon is for attention or disambiguation. When every menu item, every
button, and every card has an icon, none of them stands out.

8.9 No Conflicting Color Systems
If the project uses slate, do not introduce gray, zinc, or
neutral in the same view. Pick one and stay there.

8.10 No Dark Mode Unless the Project Has It
A hardcoded dark:bg-slate-900 on a component in a project without a
dark-mode strategy produces inconsistency. If the project has dark
mode, use its tokens. If it does not, do not add dark styles.

8.11 No !important in Tailwind
If a class needs !important, the specificity is wrong or the class
is being applied in the wrong place. Fix the cause.

8.12 No Inline style for Things the Styling Solution Handles
BAD: <div style={{ display: "flex", gap: 8 }} />
GOOD: <div className="flex gap-2" />

Inline styles bypass the design system and the responsive variants.

8.13 No Repeating Long Class Strings
If px-4 py-2 rounded-lg bg-primary text-on-primary appears in ten
places, it is a Button. Extract it.

8.14 No Arbitrary Values
BAD: w-[347px], text-[13.5px], p-[7px].
GOOD: The nearest token value, or a new token if the design demands
it.

Arbitrary values drift. Tokens align.

8.15 No Excessive Responsive Classes
Before writing sm: md: lg: xl: 2xl:, ask:

What devices does this page target?

Is there a real design difference at each breakpoint?

Mobile-first with two or three breakpoints covers most pages.

8.16 No Z-Index Arms Race
Z-index values should come from a defined scale (z-base, z-dropdown,
z-modal, z-tooltip). Arbitrary z-[9999] creates unwinnable
conflicts.

8.17 No Layout Built From Absolute Positioning
Absolute positioning for layout breaks flow, responsiveness, and
accessibility. Use it only for elements that genuinely overlay.

8.18 No Fixed Pixel Heights for Content
A fixed h-16 on a container with text overflows in another language
or at larger font sizes. Use min-h-* or padding.

8.19 No Images Without Dimensions
An <img> without width and height causes layout shift when it
loads. Specify dimensions or an aspect ratio.

8.20 No Text Over Images Without a Contrast Layer
White text over a light image is unreadable. Add a solid or gradient
overlay, or move the text into a solid container.

9. Animation
9.1 Animation Communicates, It Does Not Decorate
Every animation answers "what changed?" or "what is happening?".
Animations that answer neither are decoration and should be removed.

9.2 Duration Scale
100–150ms: micro-interactions (hover, focus, active).

200–300ms: transitions (modal open, drawer slide).

300–500ms: larger context changes (page transition, expand).

Anything longer than 500ms feels sluggish. Anything shorter than
100ms is invisible.

9.3 Easing
ease-out for entering elements.

ease-in for exiting elements.

ease-in-out for elements that move within the viewport.

Linear is for continuous motion (progress bars, spinners), not for
interface transitions.

9.4 Animate transform and opacity
These properties are GPU-accelerated. Animating width, height,
top, left, or margin triggers layout on every frame.

9.5 Respect prefers-reduced-motion
css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
9.6 No Animation on Page Load Without Reason
A page that fades in every section on load delays the user. Entrance
animations are for a specific storytelling moment, not a default.

9.7 No Parallax by Default
Parallax is a design choice. It causes motion sickness in some users
and is expensive on low-end devices. Add it only when the project
already uses it.

9.8 No Skeleton for Less Than 200ms
A skeleton that appears and disappears within 200ms is a flash. Show
the skeleton only after a threshold, or not at all.

10. RTL and Bidirectional Layouts
10.1 Logical Properties
Use logical properties that adapt to direction:

margin-inline-start instead of margin-left.

padding-inline-end instead of padding-right.

border-inline-start instead of border-left.

In Tailwind: ms-* / me-* / ps-* / pe-* instead of ml-* /
mr-* / pl-* / pr-*.

10.2 Directional Icons Mirror
Back arrows, chevrons, and progress indicators mirror in RTL.
Icons that represent an object (a user, a document) do not.

BAD: A back arrow that points right in an RTL layout.
GOOD: A back arrow that points in the reading-start direction.

Use rtl:rotate-180 or the project's utility for this.

10.3 dir Attribute on the Root
<html dir="rtl" lang="fa"> for Persian. <html dir="ltr" lang="en">
for English. Bilingual pages set dir per section where the
direction changes.

10.4 Do Not Mix Directions Inside a Component
An LTR input inside an RTL page is intentional only for specific
content (a phone number, a code, a URL). Otherwise, the whole
component follows the page direction.

10.5 Numerals
Persian and Arabic use Eastern Arabic numerals (۰۱۲۳) in some
contexts and Western numerals (0123) in others. Follow the project's
convention. Do not mix within a single view.

11. Working With codemerge
11.1 Discover the Design System
Before writing any UI code:

codemerge-fetch
tailwind.config.ts
src/styles/theme.css
src/components/ui/Button.tsx
src/components/ui/Input.tsx
Or, if the project uses a tokens package:

codemerge-search
color-primary
11.2 Fetch Two or Three Similar Components
To match the project's pattern, fetch:

One form component (to see input + label + error pattern).

One container component (to see card + spacing pattern).

One interactive component (to see hover + focus + disabled states).

11.3 Report Gaps, Do Not Fill Them Silently
If the design system lacks a token or a primitive, report it in the
response. Do not invent one inline. The design system is a shared
resource; changes to it need review.

12. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.

If the violation is a visual inconsistency in already-shipped code,
add a note: "This pattern is likely repeated in other components.
Consider a project-wide audit."

text

---