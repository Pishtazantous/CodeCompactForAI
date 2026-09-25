---
id: 04-ui-design-system
title: "UI & Design System Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md", "ui/05-ui-rtl-persian.md"]
category: ui
version: 4
---

# UI & Design System Anti-Slop Layer

This file defines universal visual and interaction contracts for projects with a user interface. It sits in the UI layer, below the universal anti-slop rules and above framework-specific patterns. It covers design tokens, component primitives, variants, composition, visual anti-slop, and animation. It does not cover component logic (see framework files), data fetching and state (see `domains/delivery/02-frontend-anti-slop.md`), detailed accessibility (see `domains/concern/02-accessibility-critical-anti-slop.md`), project-specific branding (see project files), or detailed RTL/Persian typography (see `ui/05-ui-rtl-persian.md`).

Visual consistency is a contract with the user, not an aesthetic preference.

## Scope

This file applies to SaaS, consumer, marketing, admin, mobile, and desktop applications with a UI, as well as shared component libraries. The principles are framework-agnostic. This file is the single source of visual truth.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

## Contracts

A design system commits to seven contracts. The table below maps each contract to the rules that enforce it.

| Contract | Description | Enforced By |
|---|---|---|
| Token Coverage | Every visual property resolves to a token. | UI-004, UI-005, UI-008 |
| Primitive Availability | Every generic UI element has a single primitive. Duplicate implementations are not permitted. | UI-002, UI-011 |
| Variant Consistency | Variants are enumerated and applied consistently. | UI-015, UI-016 |
| Composition Over Configuration | Components compose via slots or children, not configuration flags. | UI-018 |
| Accessibility Baseline | Every primitive meets keyboard, focus, label, and contrast baseline. | UI-021 to UI-025 |
| Visual Restraint | Limited palette, effects with reason, no clichés. | UI-026 to UI-048 |
| Direction Awareness | UI supports LTR and RTL with logical properties. | UI-056 |

## Design Tokens

### UI-001 — Token Discovery

**MUST**

Before writing a color, spacing value, font size, or border radius, the assistant MUST fetch the project's token source (e.g., `tailwind.config.ts`, `theme.ts`, CSS custom properties) and use the semantic token name.

Inventing raw values produces visual drift and breaks theming.

### UI-002 — Primitive Discovery

**MUST**

Before writing a new generic UI element (Button, Input, Card, Dialog), the assistant MUST search the component library. If a primitive exists, it MUST be used. If it is close but missing a variant, the gap MUST be reported before extending it. New primitives are only created when nothing close exists.

Duplicate primitives fragment the design system.

### UI-003 — Pattern Consistency

**MUST**

The assistant MUST follow the project's existing styling and composition patterns. Introducing a new styling paradigm without explicit permission is prohibited.

Consistency beats individual preference.

### UI-004 — Semantic Token Usage

**MUST**

Every visual property in the codebase MUST resolve to a semantic token. Raw values are not allowed in component code.

Example (illustrative, JSX-style):

BAD:
```tsx
<div className="bg-red-500 text-white p-4 rounded-lg" />
```

GOOD:
```tsx
<div className="bg-danger text-on-danger p-md rounded-md" />
```

### UI-005 — Raw Value Prohibition

**MUST NOT**

Raw hex, RGB, HSL, or arbitrary pixel values MUST NOT be used in component code. Raw color values appear only in the token definition file.

### UI-006 — Framework Palette Prohibition

**MUST NOT**

Using framework palette names directly (e.g., `red-500`, `blue-600`, `gray-300`) couples the component to the framework's default theme. Semantic tokens MUST be used instead.

### UI-007 — Documented Color Roles

**MUST**

Every color in the system MUST have a documented role. Inventing new color roles (e.g., "accent-2", "brand-purple") without review is prohibited.

### UI-008 — Arbitrary Value Prohibition

**MUST NOT**

Arbitrary values (e.g., `p-[13px]`, `mt-[7px]`, `w-[347px]`) MUST NOT be used. They break the design scale and produce visual drift. The nearest token MUST be used, or a missing token MUST be reported.

### UI-009 — Token Addition Review

**MUST**

If a value is missing from the token set, the assistant MUST report it. Adding a new token without review is prohibited. The design system is a shared resource.

### UI-010 — Semantic Token Naming

**MUST**

Token names MUST be semantic (e.g., `--color-primary`, `--space-md`), not visual (e.g., `--color-blue-500`, `--space-13px`). Semantic names survive re-theming.

## Component Primitives

### UI-011 — Primitive Uniqueness

**MUST**

There MUST be exactly one primitive per concept. Duplicate implementations (e.g., two `Button` components in different directories) MUST be deleted.

### UI-012 — Minimal Component Props

**MUST**

Component props MUST describe visual variation (e.g., `variant`, `size`), not the caller's intent or boolean explosions.

Example (illustrative, JSX-style):

BAD:
```tsx
<Button isPrimary isLarge hasIcon iconPosition="left" />
```

GOOD:
```tsx
<Button variant="primary" size="lg" leadingIcon={<SaveIcon />} />
```

### UI-013 — Primitive Logic Separation

**MUST NOT**

Primitives MUST NOT contain business logic, data fetching, or navigation logic. A `Button` does not fetch data; a `Card` does not navigate. Primitives are visual and interactive only.

### UI-014 — Attribute Forwarding

**MUST**

Every primitive that wraps a native element MUST forward `ref`, `onClick`, `aria-*`, `data-*`, and `className` to allow consumers to compose without forking.

## Variants and Composition

### UI-015 — Enumerated Variants

**MUST**

Variants MUST be enumerated (e.g., `primary`, `secondary`, `ghost`, `danger`). Boolean flags for combinations (e.g., `isPrimary isGhost`) MUST NOT be used.

### UI-016 — Orthogonal Sizing

**MUST**

Size MUST be an orthogonal prop (e.g., `size="lg"`). Combined variant-size props (e.g., `primaryLarge`) MUST NOT be created.

### UI-017 — State and Variant Separation

**MUST**

`disabled`, `loading`, `pressed`, and `focused` are states, not variants. A variant describes what the component is; a state describes what it is doing now.

### UI-018 — Composition Over Configuration

**MUST**

Components MUST compose via slots or children rather than growing boolean flags or complex configuration objects for every layout combination.

Example (illustrative, JSX-style):

BAD:
```tsx
<Card
  title="User"
  subtitle="Details"
  showDivider
  actions={[...]}
  footer={<Button>Save</Button>}
/>
```

GOOD:
```tsx
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
```

### UI-019 — Polymorphic Rendering

**MUST**

A primitive that must render as different elements MUST use `asChild` or `render` props, not a `tag` string that changes the props type unsafely.

### UI-020 — Primitive Single Responsibility

**MUST**

A primitive MUST have one responsibility. A `Card` that also handles selection, expansion, and navigation is three components merged and MUST be split.

## Accessibility Baseline

Detailed accessibility rules live in `domains/concern/02-accessibility-critical-anti-slop.md`. The baseline for every UI component:

### UI-021 — Keyboard Accessibility

**MUST**

Every interactive element MUST be reachable by Tab and activatable by Enter or Space. Focus order MUST match reading order.

### UI-022 — Focus Visibility

**MUST**

Focus MUST be visible on every interactive element. `:focus-visible` MUST show the indicator for keyboard users. Modals MUST trap focus and return it on close.

### UI-023 — Semantic Labeling

**MUST**

Every input MUST have an associated `<label>`. Icon-only buttons MUST have an `aria-label`. Errors MUST be associated with the input via `aria-describedby`.

### UI-024 — Contrast Ratios

**MUST**

Text on backgrounds MUST meet 4.5:1 (or 3:1 for large text). UI components MUST meet 3:1 against adjacent colors. Focus indicators MUST meet 3:1.

### UI-025 — Multi-Signal States

**MUST NOT**

Color MUST NOT be the only signal for state. Every state communicated by color MUST also be communicated by an icon, label, or shape.

## Anti-Patterns

The patterns below are forbidden unless the project already uses them and the design explicitly calls for them.

### UI-026 — Visual Cliché Prohibition

**MUST NOT**

The following generated or low-quality UI signals MUST NOT be introduced:
- Purple-to-blue gradients (the default AI gradient).
- Rainbow gradient text on headings.
- Glass morphism (`backdrop-blur-lg` with translucent backgrounds) without explicit design reason.
- The "AI card" hover (`hover:scale-105` with `hover:shadow-2xl`).
- Global `animate-pulse` on non-loading elements.
- Emoji as UI icons (use SVG icons from the project's set).

### UI-027 — Transition Discipline

**MUST NOT**

`transition-all` MUST NOT be used. It transitions layout and paint properties the user did not intend to animate. Specific properties (e.g., `transition-colors`) MUST be used.

### UI-028 — Icon Discipline

**SHOULD NOT**

Icons SHOULD NOT be added to every label, menu item, or card. Icons are for attention or disambiguation.

### UI-029 — Color System Consistency

**MUST NOT**

Conflicting color systems MUST NOT be mixed in the same view (e.g., `slate` and `gray` and `zinc`).

### UI-030 — Dark Mode Strategy

**MUST NOT**

Hardcoded `dark:` classes MUST NOT be added to components in projects without a deliberate dark mode strategy.

### UI-031 — Specificity Discipline

**MUST NOT**

`!important` in Tailwind and inline `style` for properties the styling solution handles MUST NOT be used. They indicate wrong specificity or wrong application context.

### UI-032 — Component Extraction

**MUST**

Repeated long class strings (e.g., `px-4 py-2 rounded-lg bg-primary text-on-primary` in ten places) MUST be extracted into a component.

### UI-033 — Responsive Restraint

**SHOULD**

Excessive responsive classes (`sm: md: lg: xl: 2xl:`) SHOULD be avoided. Mobile-first with two or three breakpoints covers most pages.

### UI-034 — Z-Index Scale

**MUST**

Z-index values MUST come from a defined scale (`z-base`, `z-dropdown`, `z-modal`). Arbitrary `z-[9999]` creates unwinnable conflicts.

### UI-035 — Layout Flow

**MUST NOT**

Absolute positioning MUST NOT be used for layout. Deeply nested flex/grid containers SHOULD be flattened into a single grid with proper areas.

### UI-036 — Content Sizing

**MUST NOT**

Fixed pixel heights on content containers MUST NOT be used. Images MUST have dimensions or an aspect ratio to prevent layout shift.

### UI-037 — Image Contrast

**MUST**

Text over images MUST have a solid or gradient overlay, or be moved into a solid container. White text over light images is unreadable.

### UI-038 — Border Radius Scale

**MUST**

Border radii MUST follow a defined scale. Mixed radii (`rounded-md`, `rounded-lg`, `rounded-full`) in the same view are prohibited.

### UI-039 — Shadow Elevation

**MUST**

Shadows MUST correspond to elevation, not size. Heavy shadows on small elements and multiple shadow layers without reason are prohibited.

### UI-040 — Typography Hierarchy

**MUST NOT**

All-caps body text, center-aligned body text over three lines, more than three font sizes on one screen, and more than two font weights on one screen MUST NOT be used.

### UI-041 — Contrast Verification

**MUST**

Insufficient contrast (gray-on-light-gray, white-on-pastel) MUST be verified with a tool, not by eye.

### UI-042 — Form Labels

**MUST NOT**

Placeholders MUST NOT be used as labels. Forms lose context when the user types.

### UI-043 — Focus Outlines

**MUST NOT**

Removing focus outlines (`*:focus { outline: none; }`) is prohibited. `:focus-visible` with a visible indicator MUST be used.

### UI-044 — Semantic Elements

**MUST NOT**

Clickable `<div>` elements MUST NOT be used instead of `<button>` or `<a>`. They lack keyboard activation and screen reader semantics.

Example (illustrative, JSX-style):

BAD:
```tsx
<div onClick={handleClick}>Save</div>
```

GOOD:
```tsx
<button onClick={handleClick}>Save</button>
```

### UI-045 — Loading States

**MUST**

Skeleton loaders MUST be used for content instead of spinners to maintain layout. Layout shift on load MUST be prevented by reserving space.

### UI-046 — Modal Discipline

**SHOULD NOT**

Modals SHOULD NOT be used for navigation or content that could be inline. Toasts SHOULD NOT be used for every save or info message.

### UI-047 — Touch Interactions

**MUST NOT**

Hover-only interactions and hover tooltips on mobile MUST NOT be used. Tap and focus alternatives MUST be provided.

### UI-048 — Disabled State Clarity

**MUST**

Disabled buttons MUST show why they are disabled, or be hidden. Unexplained disabled states leave the user stuck.

## Animation

### UI-049 — Animation Purpose

**MUST**

Every animation MUST answer "what changed?" or "what is happening?". Decoration-only animation MUST be removed.

### UI-050 — Animation Duration

**MUST**

Durations MUST follow a scale: 100-150ms for micro-interactions, 200-300ms for transitions, 300-500ms for context changes. Over 500ms feels sluggish; under 100ms is invisible.

### UI-051 — Animation Easing

**MUST**

Easing MUST match intent: `ease-out` for entering, `ease-in` for exiting, `ease-in-out` for viewport movement, `linear` for continuous motion.

### UI-052 — GPU Acceleration

**MUST**

Only `transform` and `opacity` SHOULD be animated. Animating `width`, `height`, `top`, `left`, or `margin` triggers layout on every frame.

### UI-053 — Reduced Motion

**MUST**

`prefers-reduced-motion` MUST be respected. Animations and transitions MUST be reduced to 0.01ms for users who request it.

### UI-054 — Entrance Restraint

**SHOULD NOT**

Entrance animations on page load and parallax effects SHOULD NOT be used by default. They delay the user and cause motion sickness.

### UI-055 — Skeleton Threshold

**MUST**

Skeletons MUST only appear after a threshold (e.g., 200ms). A skeleton that flashes and disappears is visual noise.

## RTL and Bidirectional Layouts

This file requires direction awareness. When the project targets an RTL language:

- Use logical properties (`ms-*`, `me-*`, `ps-*`, `pe-*`) instead of physical (`ml-*`, `mr-*`).
- Use `text-start` / `text-end` instead of `text-left` / `text-right`.
- Mirror directional icons (back, forward, next), not object icons.

### UI-056 — RTL Reference

**MUST**

Detailed RTL, logical properties, bidirectional text, and Persian typography rules are defined in `ui/05-ui-rtl-persian.md`. This file MUST NOT duplicate those rules. General direction awareness and logical properties MUST follow the RTL file when the project targets an RTL language.

## AI-Specific UI Discipline

### UI-057 — Tailwind Class Verification

**MUST**

Before using a Tailwind utility class or arbitrary value (e.g., `p-[13px]`), the assistant MUST verify that the class exists in the project's Tailwind configuration. Invented classes produce no visual effect and are invisible at compile time.

Example (illustrative):

BAD: Using `p-[13px]` when the project uses a token-based spacing scale defined in `tailwind.config.ts`.

GOOD: Using `p-md` after verifying the token exists in the project's configuration.

## Response to Violation

When a rule in this file is violated, report:

Violation: UI-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.