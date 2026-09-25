---
id: 06-make-ui-file
title: "How to Generate the UI File"
lang: en
category: helper
version: 2
---

# How to Generate the UI File

The UI file (`ui/04-ui-design-system.md`) defines visual and
interaction rules: design tokens, component primitives, variants,
composition, visual anti-slop, animation, and RTL/LTR. It applies
only to projects that have a user interface.

## The Single File Rule

There is ONE UI file per system. Not one per framework. Not one per
project. The file lives at `prompts/ui/04-ui-design-system.md` and
is shared by every project that has a UI.

If a project has a different design system (for example, an internal
admin tool with a distinct visual language), that design system
belongs in the project file, not in a new UI file. The UI file
describes universal visual rules; project-specific branding belongs
in `projects/<name>/00-anti-slop-core.md`.

If a system is truly multilingual and multi-brand with distinct
visual systems, the UI file describes the shared baseline and each
project's file describes its brand layer.

Do NOT create multiple UI files. If the single file grows too large,
split by topic within the same file, not across files.

## When to Use This Guide

Use this guide when:

- Generating the UI file for the first time.
- Regenerating the UI file when the design system changes.
- Adding a new section to the UI file.

Do NOT use it when:

- Generating a language file (see `02-make-language-file.md`).
- Generating a delivery file (see `01-make-delivery-file.md`).
- Generating a framework file (see `03-make-framework-file.md`).
- Generating a concern file (see `04-make-concern-file.md`).
- Filling in a project file (see `05-make-project-file.md`).

## Files to Attach

### Required

- `_universal/00-master-anti-slop.md`

This file is mandatory. Without it, the AI cannot avoid duplicating
universal rules.

### Required (1-2 framework references)

Attach at least one existing framework file that matches the UI's
primary framework:

- `domains/framework/02-react-anti-slop.md` for React-based UIs.
- `domains/framework/02-vue-anti-slop.md` for Vue-based UIs.
- `domains/framework/02-svelte-anti-slop.md` for Svelte-based UIs.
- `domains/framework/02-angular-anti-slop.md` for Angular-based UIs.

The framework file prevents the UI file from repeating component
discipline and lifecycle rules that belong there.

### Required (frontend delivery)

Attach:

- `domains/delivery/02-frontend-anti-slop.md`

This file contains component, state, data fetching, and forms rules
that the UI file must not duplicate.

### Optional (accessibility concern)

If the project has accessibility as a first-class concern, attach:

- `domains/concern/02-accessibility-critical-anti-slop.md`

Without it, the UI file may duplicate accessibility rules that
belong in the concern file.

### Optional (design system source)

If the project has a design system already, attach:

- The design token file (`tailwind.config.ts`, `theme.ts`,
  `tokens.css`, or equivalent).
- 2-3 existing primitive components (`Button.tsx`, `Input.tsx`,
  `Card.tsx`).

These anchor the rules to the actual design system.

## Reference Attachments by UI Context

The following table tells you which attachments to choose for each
UI context.

| UI context | Framework reference | Extra |
|---|---|---|
| React SPA | 02-react-anti-slop.md | tailwind.config or theme.ts |
| Next.js app | 02-nextjs-anti-slop.md + 02-react-anti-slop.md | design tokens |
| Vue SPA | 02-vue-anti-slop.md | design tokens |
| Nuxt app | 02-nuxt-anti-slop.md + 02-vue-anti-slop.md | design tokens |
| Svelte app | 02-svelte-anti-slop.md | design tokens |
| SvelteKit app | 02-sveltekit-anti-slop.md + 02-svelte-anti-slop.md | design tokens |
| Angular app | 02-angular-anti-slop.md | design tokens |
| React Native | 02-react-native-anti-slop.md | mobile design tokens |
| Flutter | 02-flutter-anti-slop.md | mobile design tokens |
| Electron | 02-electron-anti-slop.md + 02-react-anti-slop.md | design tokens |
| Tauri | 02-tauri-anti-slop.md | design tokens |

Choose the closest context. If the UI is React-based, always attach
`02-react-anti-slop.md` regardless of the meta-framework.

## Additional Prompt Requirements

When filling in the master prompt for the UI file, insert the
following block under the `Mandatory Rules` section. This block
overrides the defaults for the UI category.

```
### UI-Specific Requirements

UI files must satisfy the following in addition to the general
rules:

1. Design System Contracts.

   The file MUST include a section titled "Design System Contracts"
   that states what the design system promises:

   - What token categories exist (color, spacing, typography,
     radius, shadow, motion).
   - What primitives exist (Button, Input, Card, Dialog, and so on).
   - What variant system is used (CVA, tailwind-variants, custom).
   - What composition pattern is used (compound components,
     slots, children).
   - What accessibility baseline is enforced (labels, focus,
     keyboard, contrast).

   The contracts section is the reference. Other sections enforce
   the contracts.

2. UI Boundaries.

   The opening paragraph MUST state clearly what this file does
   NOT cover, with references to sibling files. For example:

       This file does NOT cover:
       - Component logic and hooks (see the framework files).
       - Data fetching and state (see the frontend delivery file).
       - Detailed accessibility rules (see the accessibility
         concern file).
       - Project-specific branding (see the project file).

   Without boundaries, the UI file duplicates framework, delivery,
   and concern rules.

3. Token Discipline.

   The file MUST include a section titled "Token Discipline" that
   states:

   - Every visual property in the codebase resolves to a token.
   - The token categories and their naming convention.
   - The rule for adding a new token (ask first, do not invent).
   - The rule against raw values (hex, rgb, pixel sizes, custom
     easing curves).

   Example:

       Every color, spacing value, font size, border radius, and
       shadow resolves to a token. Raw values (hex codes, arbitrary
       pixel sizes) are not allowed in components. If a token is
       missing, report it; do not add one without review.

4. Visual Anti-Slop Catalog.

   The file MUST include a section titled "Visual Anti-Slop" with
   at least 25 specific visual patterns to avoid. Each item:

   - Names the pattern.
   - Explains why it is slop.
   - States what to do instead.

   Examples:
   - Purple-to-blue gradients (AI cliché).
   - Glass morphism (backdrop-blur) without a design reason.
   - `hover:scale-105` combined with `hover:shadow-2xl`.
   - `transition-all` instead of specific properties.
   - Global `animate-pulse` on non-loading elements.
   - Emoji as UI icons.
   - Icons on every label.
   - Dark mode without a strategy.

   The visual anti-slop catalog is where most of the file's value
   lives. Be specific. Vague rules ("no ugly design") are
   useless.

5. UI-Specific, Not General.

   Every rule MUST be specific to visual and interaction patterns.
   If a rule applies to any frontend, it belongs in
   `02-frontend-anti-slop.md`. If a rule applies to component
   logic, it belongs in the framework file.

   Test: does the rule describe a visual property, a design token
   decision, or an interaction pattern? If not, it is not a UI
   rule.

   BAD (belongs in frontend delivery):
       ### 3.1 Do Not Fetch Data in Components

       Components must not call fetch directly.

   GOOD (belongs in UI):
       ### 3.1 Spacing Uses Tokens, Not Arbitrary Values

       Use the spacing scale (`p-md`, `gap-sm`) instead of arbitrary
       values (`p-[13px]`). Arbitrary values break the visual rhythm
       and drift over time.

6. Rationale for Every Rule.

   Every rule MUST include a one-line rationale, even when the rule
   seems obvious.

   For visual rules, the rationale often references consistency,
   accessibility, or a stale trend.

7. At Least 25 Anti-Patterns.

   The `Visual Anti-Slop` section MUST have at least 25 items.

   Each item has:
   - A short title.
   - A one-line explanation.
   - A BAD/GOOD code pair, or a BAD/GOOD visual description.

   Visual anti-patterns are often purely visual (a gradient, a
   shadow, a font choice). For those, a textual BAD/GOOD is
   acceptable if the code would be trivial.

8. At Least 15 Rules with Code Examples.

   Not 50% of rules. At least 15 concrete code or class examples in
   the entire file. This number is a floor, not a target.

   UI rules are highly concrete: a specific class combination, a
   specific token name, a specific component pattern. Examples are
   the primary way to convey these rules.

9. RTL and Bidirectional.

   If the project supports right-to-left languages, the file MUST
   include a section titled "RTL and Bidirectional Layouts" that
   covers:

   - Logical properties (`ms-`, `me-`, `ps-`, `pe-` over `ml-`,
     `mr-`, `pl-`, `pr-`).
   - Directional icon mirroring.
   - The `dir` attribute strategy.
   - Numerals in RTL contexts.

   If the project does not support RTL, state this explicitly in
   the Scope section. Do not omit the section silently.
```

## Filling in the Master Prompt

Use this template for the metadata portion of the master prompt:

```
Path: prompts/ui/04-ui-design-system.md
id: 04-ui-design-system
title: UI & Design System Anti-Slop Layer
domain_type: ui
depends_on: [00-master-anti-slop]

Coverage:
Design tokens, component primitives, variants, composition,
visual anti-slop, animation, RTL/LTR.

NOT covered:
Component logic, state management, data fetching, framework-
specific component patterns, detailed accessibility rules.
```

Note: the `domain_type` for UI files is `ui`, not one of the four
domain types. This file lives in a separate layer.

Then insert the `Additional Prompt Requirements` block above under
the `Mandatory Rules` section of the master prompt.

## Standard Structure

The UI file has these sections, in this order:

1. Frontmatter
2. Title (H1)
3. Opening paragraph (boundaries)
4. Scope
5. Reference the Existing Design System First
6. Design Tokens
7. Design System Contracts
8. Token Discipline
9. Component Primitives
10. Variants
11. Composition
12. Accessibility Baseline
13. Visual Anti-Slop (25+ items)
14. Animation
15. RTL and Bidirectional Layouts
16. Working with codemerge
17. Response to Violation

Adjust the exact numbering based on what the design system contains.
Every section above must appear, even if short.

## Suggested Topics by UI Context

The following topics apply to specific UI contexts. Adjust the
general structure with these additions.

### Web UI (Desktop-first)

- Responsive breakpoints (define the scale, do not invent per
  component)
- Pointer and hover states
- Keyboard navigation
- Focus indicators
- Contrast requirements (WCAG AA baseline)

### Web UI (Mobile-first)

- Touch targets (minimum 44x44 px)
- Tap, long-press, swipe interactions
- Safe areas
- Sticky headers
- Scroll physics

### Data-heavy UI (Dashboards, Admin)

- Table styling and density
- Sorting and filtering affordances
- Empty states
- Loading states (skeleton vs spinner)
- Error states (inline vs toast)

### Marketing UI

- Hero section patterns (avoid the AI cliché gradient)
- Typography hierarchy
- Call-to-action placement
- Social proof patterns
- Above-the-fold discipline

### SaaS product UI

- Navigation patterns (sidebar, top bar, hybrid)
- Onboarding patterns
- Settings layouts
- Notification patterns
- Modal and drawer usage

### Mobile UI

- Platform conventions (iOS HIG vs Material)
- Safe area handling
- Native navigation patterns
- Bottom sheets
- Swipe gestures

### Embedded UI (Widgets, Inline)

- Minimal footprint
- Shadow DOM isolation
- Theming via CSS variables
- No global styles

## Common Visual Anti-Patterns to Include

The following list is a starting point. The generated file should
include all of these, plus any project-specific ones.

### Color

1. Purple-to-blue gradients (AI cliché).
2. Rainbow gradients on text.
3. Colors not from the design system.
4. Mixing color systems (slate + gray + zinc).
5. Using color as the only signal of state.
6. Insufficient contrast (below 4.5:1 for text).
7. Dark mode added without a strategy.
8. `bg-opacity-*` used to create hover states.

### Typography

9. More than three font sizes on one screen.
10. More than two font weights on one screen.
11. Line length over 80 characters.
12. Center-aligned body text.
13. All-caps body text.
14. `font-bold` on everything.

### Spacing

15. Arbitrary pixel values (`p-[13px]`).
16. Inconsistent vertical rhythm.
17. Padding larger than the content itself.

### Radius and Shadow

18. Mixed border radii (some `rounded-md`, some `rounded-lg`).
19. Heavy shadows (`shadow-2xl`) on small elements.
20. Multiple shadow layers.

### Motion

21. `transition-all` on everything.
22. Duration over 500 ms.
23. Animations on page load without reason.
24. Bouncing or pulsing on non-loading elements.
25. `hover:scale-105` combined with `hover:shadow-2xl`.
26. Ignoring `prefers-reduced-motion`.

### Components

27. New component when a primitive exists.
28. Reinventing `Button`, `Input`, or `Card`.
29. Emoji as UI icons.
30. Icons on every label.
31. `!important` in Tailwind.
32. Inline `style={{}}` for things Tailwind handles.
33. Long class strings repeated in 10 places.

### Accessibility (baseline)

34. Removed focus outlines.
35. Missing `alt` or empty `alt` on meaningful images.
36. `<div onClick>` instead of `<button>`.
37. Placeholder used as label.
38. Focus trap missing in modals.

### Layout

39. Absolute positioning for layout.
40. Fixed pixel heights on content.
41. Deeply nested flex/grid.
42. Z-index values outside a defined scale.

## Verification

After receiving the file from the AI, verify:

1. Every item in the master prompt's self-audit checklist.
2. Every item in the `UI-Specific Self-Audit` below.
3. The file is between 250 and 400 lines.
4. The file does not repeat rules from the framework, delivery, or
   accessibility files attached.

If any item fails, request a revision from the AI rather than
saving a weak file.

## UI-Specific Self-Audit

Before saving the file, verify every item:

Design System Contracts:
- [ ] A section titled "Design System Contracts" exists
- [ ] Token categories are listed
- [ ] Primitives are listed
- [ ] Variant system is described
- [ ] Composition pattern is described
- [ ] Accessibility baseline is described

Boundaries:
- [ ] The opening paragraph states what the file does NOT cover
- [ ] References to framework, delivery, and concern files exist
- [ ] No rule belongs to another layer

Token Discipline:
- [ ] A section titled "Token Discipline" exists
- [ ] The rule against raw values is stated
- [ ] The rule for adding a new token is stated
- [ ] Token naming convention is described

Visual Anti-Slop:
- [ ] A section titled "Visual Anti-Slop" exists
- [ ] At least 25 items are present
- [ ] Each item has a short title and one-line explanation
- [ ] At least 15 items have a BAD/GOOD example
- [ ] The catalog covers color, typography, spacing, motion,
      components, and layout

UI Specificity:
- [ ] Every rule is specific to visual or interaction patterns
- [ ] No rule would apply to a non-UI project
- [ ] Component logic rules are not present
- [ ] Data fetching rules are not present

Rationale Discipline:
- [ ] Every rule has a one-line rationale
- [ ] The rationale explains why, not just what

RTL:
- [ ] The file either covers RTL or states explicitly that RTL is
      not supported
- [ ] If covered, logical properties are mentioned
- [ ] If covered, icon mirroring is mentioned

Code Examples:
- [ ] At least 15 rules in the file have BAD/GOOD examples
- [ ] Examples use `tsx`, `jsx`, `vue`, `svelte`, `css`, or
      `tailwind` language tags
- [ ] Class names and tokens are realistic

Structural:
- [ ] Frontmatter is complete with `category: ui`
- [ ] Opening paragraph is 3-5 lines
- [ ] At least 12 sections total
- [ ] Response to Violation section matches the fixed template
- [ ] Entire file is in English
- [ ] No emoji

Non-Duplication:
- [ ] No rule from Universal is repeated
- [ ] No rule from the framework file is repeated
- [ ] No rule from the frontend delivery file is repeated
- [ ] No rule from the accessibility concern file is repeated
- [ ] References to other files have one-line summaries

If any item fails, ask the AI to revise the specific section. Do
not save a file that fails the self-audit.

## Common Failures

The following failures occur frequently when generating the UI
file. Use this table during review.

| Failure | How to spot it | Fix |
|---|---|---|
| Framework bleed | Mentions `useState`, `v-model`, hooks | Move to framework file |
| Delivery bleed | Mentions data fetching, forms, routing | Move to delivery file |
| Concern bleed | Detailed WCAG rules, a11y testing | Move to concern file |
| Universal bleed | Mentions "no TODO", "declare assumptions" | Delete; they are in Universal |
| Vague rules | "Use good design" or "be consistent" | Make specific |
| Emoji in text | `✅`, `❌`, `🚫` | Replace with `GOOD:`/`BAD:` |
| No visual anti-slop section | Missing the 25+ item catalog | Request it |
| Under 25 anti-patterns | Count them | Request more |
| No token discipline | Missing the section | Request it |
| Missing rationale | Rules say "do not" without "because" | Request rationale |
| No RTL section | Silent omission | Add section or state not supported |
| Over-length | Over 400 lines | Split by topic within the file |

## Verification Before Use

Before using the UI file in a real session:

1. Confirm `prompts/ui/04-ui-design-system.md` is the only UI file
   in the system.
2. Confirm no framework, delivery, or concern rule is duplicated.
3. Confirm the design tokens referenced in the file exist in the
   project's token source.
4. Confirm the primitives referenced in the file exist in the
   project's component library.
5. Confirm the visual anti-slop catalog has at least 25 items.

If any item fails, the file is not ready. A UI file that references
non-existent tokens or primitives confuses the AI more than it
helps.

## Updating the UI File

The UI file is updated when:

- The design system changes (new tokens, new primitives, new
  variants).
- A new visual anti-pattern is spotted in review.
- The accessibility baseline changes (for example, WCAG AA becomes
  AAA for a project).
- The framework or design system library changes (for example,
  moving from Tailwind v3 to v4).

Update the file on the same commit as the change that caused it.
This keeps the file in sync with the code.

## After the File Is Accepted

1. Save to `prompts/ui/04-ui-design-system.md`.
2. Update `prompts/README.md` to include the UI file in the file
   list.
3. Reference the UI file from every project file that has a UI:

   ```
   # In prompts/projects/<name>/00-anti-slop-core.md:
   depends_on: [..., 04-ui-design-system]
   ```

4. Do not create a second UI file. If a project needs a distinct
   visual language, add a "Brand" section to the project file, not
   a new UI file.

## Time Budget

Generating the UI file with a frontier model takes 5-8 minutes (the
file is longer than other domain files because of the anti-slop
catalog). Review takes 15-20 minutes with the self-audit checklist.

Because this file is generated once for the whole system, the time
investment is amortized across every project that uses it.

## Reference Example

The example in `prompts/_send-packages/example-svelte/` shows the
workflow for a framework file. The same workflow applies to the UI
file, with the additional `UI-Specific Requirements` block inserted
into the master prompt.
