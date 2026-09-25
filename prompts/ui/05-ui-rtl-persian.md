---
id: 05-ui-rtl-persian
title: "RTL & Persian UI Anti-Slop Layer"
lang: en
depends_on: ["_universal/00-style-guide.md", "_universal/00-master-anti-slop.md", "ui/04-ui-design-system.md"]
category: ui
version: 3
---

# RTL & Persian UI Anti-Slop Layer

This file defines rules specific to right-to-left (RTL) layouts and Persian-language interfaces. It sits in the UI layer, alongside `ui/04-ui-design-system.md`, and is sent together with it for RTL projects. It covers typography, directionality, logical properties, numerals, Jalali calendar presentation, bidirectional text, forms, layout behavior, and cultural conventions relevant to Persian UI. It does not replace the general UI design system, framework-specific patterns, or detailed accessibility rules. It applies to projects whose primary language is Persian, Arabic, Hebrew, or Urdu.

RTL is not simply LTR mirrored. Direction, semantic icon behavior, typography, bidi handling, data presentation, and component conventions must be designed intentionally.

## Scope

This file applies to:

- Persian-language web applications.
- Persian-language mobile applications.
- Bilingual Persian/English applications.
- RTL interfaces where the same directional principles apply.

This file does not replace `04-ui-design-system.md`. Both are sent together. The general file defines tokens, primitives, components, variants, spacing, color, and general interaction rules. This file adds RTL and Persian-specific constraints.

If the project is English-only LTR, this file is not required.

## Rule Severity

Severity follows `_universal/00-style-guide.md`.

When this file conflicts with an explicit product or design-system decision, the higher-level design system controls unless the rule is a technical RTL/bidi correctness requirement.

## RTL Contracts

An RTL interface follows six contracts.

### RTL-001 — Root Direction

**MUST**

The document root declares the actual language and direction.

For a Persian-first document:

``` html
<html dir="rtl" lang="fa">
```

Do not rely only on CSS `direction: rtl` for document semantics.

### RTL-002 — Language Accuracy

**MUST**

The `lang` attribute must match the primary document language.

For Persian:

``` html
<html dir="rtl" lang="fa">
```

The language metadata affects assistive technology, language-specific processing, pronunciation, and font behavior.

### RTL-003 — User-Generated Direction

**SHOULD**

For content whose direction is unknown, use automatic direction detection:

``` html
<textarea dir="auto"></textarea>
```

Use explicit direction when the field has a known semantic type.

### RTL-004 — Component-Level Direction

**MUST**

Do not add `dir="rtl"` to arbitrary child components merely to force the visual layout. The root direction should establish the page flow.

Use local `dir` only when the content itself has a different direction, for example:

- English code
- URL
- email
- isolated English name
- quoted content with a different direction

## Logical Properties

### RTL-005 — Logical CSS

**MUST**

Directional CSS should use logical properties instead of physical `left` and `right` properties whenever the value represents layout flow.

| Physical | Logical |
|---|---|
| `margin-left` | `margin-inline-start` |
| `margin-right` | `margin-inline-end` |
| `padding-left` | `padding-inline-start` |
| `padding-right` | `padding-inline-end` |
| `border-left` | `border-inline-start` |
| `border-right` | `border-inline-end` |
| `left` | `inset-inline-start` |
| `right` | `inset-inline-end` |
| `text-align: left` | `text-align: start` |
| `text-align: right` | `text-align: end` |

Example:

``` css
.card {
  margin-inline-start: 1rem;
  padding-inline-end: 0.5rem;
  border-inline-start: 2px solid;
  text-align: start;
}
```

### RTL-006 — Tailwind Logical Utilities

**SHOULD**

When using a Tailwind version that supports logical utilities, prefer:

``` tsx
<div className="ms-4 me-2 ps-3 pe-6 text-start" />
```

over hardcoded directional utilities when the intent is logical flow.

### RTL-007 — Physical Positioning

**MUST**

Do not hardcode physical `left`/`right` for elements whose position is supposed to follow writing direction.

Prefer:

``` css
.tooltip {
  inset-inline-start: 100%;
}
```

A physical side is acceptable only when the product intentionally defines a physical, direction-independent position.

### RTL-008 — Flex and Grid

**MUST**

Do not double-reverse layouts.

In an RTL context, a normal row already follows the document's writing direction. Do not add `row-reverse` merely because the page is RTL.

Use explicit reversal only when it represents an intentional component behavior.

## Typography for Persian

### RTL-009 — Persian Font Support

**MUST**

The selected font stack must support:

- Persian-specific letters: `پ`, `چ`, `ژ`, `گ`
- Arabic shaping required by Persian
- ZWNJ
- Required numerals
- The project's supported punctuation

Example:

``` css
font-family: "Vazirmatn", "IRANSans", Tahoma, sans-serif;
```

This is an implementation example, not a mandatory font choice.

### RTL-010 — Font Size

**SHOULD**

Persian text may require slightly larger sizing than an equivalent Latin interface. Tune typography using actual Persian content rather than a fixed universal offset.

Do not enforce a blanket `+1px` or `+2px` rule across every component.

### RTL-011 — Line Height

**SHOULD**

Persian body text generally benefits from comfortable line height, often around `1.6–1.8`.

Component-specific typography may use tighter values when readability and glyph clipping have been tested.

Do not enforce one line-height value across all components.

### RTL-012 — Persian Italic

**SHOULD NOT**

Do not use `font-style: italic` as the default Persian emphasis mechanism. Prefer weight, color, emphasis, or a design-system emphasis variant.

If a specific Persian font provides a deliberate italic treatment, the component may use it when visually validated.

### RTL-013 — Letter Spacing

**MUST NOT**

Do not apply decorative positive letter-spacing to normal Persian text. It can interfere with the visual integrity of connected script.

Component-specific typography may define carefully tested tracking values when technically and visually appropriate.

### RTL-014 — Persian Case Transform

**MUST NOT**

Do not use uppercase/lowercase transformations as Persian typography rules. Persian has no case distinction.

### RTL-015 — ZWNJ

**MUST**

Use the Persian zero-width non-joiner (`\u200C`) where Persian orthography requires it.

Example:

``` text
کتاب‌ها
```

rather than:

``` text
کتابها
```

Persian strings defined by the application should be reviewed for appropriate ZWNJ usage.

### RTL-016 — Persian Punctuation

**SHOULD**

Use Persian-appropriate punctuation in Persian copy where the product's content convention requires it:

``` text
،  ؛  ؟  « »
```

Do not blindly replace punctuation inside technical data, code, URLs, identifiers, or other machine-readable values.

## Text Alignment

### RTL-017 — Default Text Alignment

**MUST**

Text alignment should follow semantic writing direction.

Prefer:

``` css
text-align: start;
```

for normal text blocks rather than hardcoding `right`.

### RTL-018 — Intentional Alignment

**SHOULD**

Use `center` for content that is intentionally centered.

Use `end`, `start`, or a documented physical alignment when a component has a clear semantic requirement.

Do not treat "RTL means everything must be right-aligned" as a universal rule.

### RTL-019 — Numeric Alignment

**SHOULD**

Numeric columns should use a consistent alignment strategy appropriate to the data type and table design. Financial and quantitative tables often benefit from end alignment or decimal-aware alignment.

## Direction Matrix

Use semantic direction rather than applying one direction to every value.

| Content type | Default direction |
|---|---|
| Persian prose | RTL |
| Arabic prose | RTL |
| English prose | LTR |
| User-generated unknown text | AUTO |
| Email address | LTR |
| URL | LTR |
| Code | LTR |
| UUID / technical ID | LTR |
| API key / token | LTR |
| Phone number | LTR or domain-specific |
| IBAN | LTR |
| Card number | LTR |
| Version string | LTR |
| Date display | Locale-aware |
| Amount display | Locale-aware |
| Mixed Persian/English sentence | RTL with bidi isolation as needed |

This table defines defaults, not an excuse to override semantic requirements of a specific domain.

## Numerals

### RTL-020 — Numeral Convention

**MUST**

The project must define a consistent numeral policy, but the policy may vary by data type.

Do NOT require one numeral system for every value in the interface.

Typical Persian-first presentation:

``` text
۱۲۳۴۵۶۷۸۹۰
```

Typical technical representation:

``` text
1234567890
```

### RTL-021 — Technical Values

**SHOULD**

Technical values normally remain Western/Latin-oriented when required for copying, interoperability, or machine processing:

- URLs
- IDs
- UUIDs
- API keys
- codes
- version numbers
- email addresses

### RTL-022 — Financial Values

**SHOULD**

Financial display must follow the project's established locale and financial formatting rules.

Example:

``` text
۱۲۵٬۰۰۰ تومان
```

Do not mix formatting conventions arbitrarily within the same product.

### RTL-023 — Number Formatting

**SHOULD**

Use locale-aware formatting APIs rather than manually replacing digits or separators.

Example:

``` ts
new Intl.NumberFormat("fa-IR").format(value);
```

The exact locale and numbering system should follow the product requirement.

### RTL-024 — Decimal and Thousands Separators

**SHOULD**

Use the locale-aware formatter for decimal and grouping separators.

Do not assume that a Persian UI means every numeric field must use the same separator or digit set.

## Dates, Time, and Calendar

### RTL-025 — Persian-Facing Date Presentation

**SHOULD**

For Persian-facing user interfaces, present dates in the Jalali/Persian calendar when that matches the product's domain and user expectations.

Examples:

``` text
۱۴۰۳/۱۰/۲۶
۲۶ دی ۱۴۰۳
```

### RTL-026 — Presentation vs Storage

**MUST**

Do not confuse user-facing date presentation with machine-readable storage or API formats.

Presentation may be Jalali/Persian while storage and integration remain canonical formats such as ISO 8601.

Example API value:

``` text
2026-09-25T10:30:00Z
```

The UI may render the same instant as a Persian calendar date.

### RTL-027 — Date Formatting

**SHOULD**

Use a Jalali-aware implementation.

For browser-native formatting:

``` ts
new Intl.DateTimeFormat("fa-IR-u-ca-persian", {
  year: "numeric",
  month: "long",
  day: "numeric",
}).format(date);
```

Validate required browser/runtime support.

### RTL-028 — Time Format

**SHOULD**

Persian-facing interfaces generally prefer 24-hour time:

``` text
۱۴:۳۰
```

Use 12-hour notation only when it is an intentional product convention.

### RTL-029 — Week Start

**SHOULD**

For Persian calendar components, Saturday should normally be treated as the first day of the week.

If the product serves multiple locales, derive the week start from the active locale rather than hardcoding it globally.

### RTL-030 — Month Names

**MUST**

When displaying Persian calendar month names, use the Persian month names appropriate to the selected calendar.

Do not substitute Gregorian month names into a Persian-calendar display.

## Icons and Directionality

### RTL-031 — Directional Icons

**MUST**

Icons whose meaning depends on direction must follow semantic direction.

Examples:

- Back
- Forward
- Next
- Previous
- Breadcrumb chevrons
- Directional progress
- Undo/redo when the visual direction carries meaning

For RTL:

- Back generally points right.
- Next generally points left.
- Breadcrumb progression runs right to left.

### RTL-032 — Object Icons

**MUST**

Do not mirror object/concept icons merely because the page is RTL.

Examples:

- User avatar
- Document
- Heart
- Star
- Search
- Settings
- Brand marks

### RTL-033 — Semantic Action, Not Icon Name

**MUST**

Determine mirroring from the semantic action, not from the icon's file name.

An icon called `ArrowLeft` is not automatically a "back" icon.

### RTL-034 — Logos

**MUST NOT**

Do not mirror a brand logo unless the brand explicitly provides an RTL variant.

### RTL-035 — Charts

**SHOULD**

Choose chart direction based on the meaning of the data.

Time-series and financial charts may intentionally remain LTR even in an RTL application. Other sequential visualizations may follow RTL.

Document the decision in the component or design system.

## Forms and Inputs

### RTL-036 — Persian Text Input

**MUST**

Inputs intended primarily for Persian text should render in RTL.

### RTL-037 — Technical Input

**MUST**

Technical values such as email, URL, code, and identifiers should use LTR direction.

Example:

``` html
<input type="email" dir="ltr" />
```

### RTL-038 — Unknown-Direction Input

**SHOULD**

For free-form user content whose direction is unknown:

``` html
<textarea dir="auto"></textarea>
```

### RTL-039 — Placeholder

**SHOULD**

Placeholder content should match the semantic direction and language of the field.

Do not place an English placeholder in a Persian-only field unless the English text is itself the intended example value.

### RTL-040 — Labels

**SHOULD**

Place labels above fields when this improves readability and supports long Persian labels. Side-by-side labels remain valid when the design system explicitly supports them.

### RTL-041 — Validation Messages

**MUST**

Validation messages must be readable, localized appropriately, and aligned with the field's text direction.

Do not rely on an English browser-native message when the application requires a Persian validation experience.

### RTL-042 — Autofill and Paste

**MUST**

Test autofill and paste behavior for RTL and LTR fields. Do not assume that browser autofill will preserve the intended direction in every browser.

## Bidirectional Text

### RTL-043 — Isolate Embedded LTR Content

**MUST**

Isolate embedded LTR content inside RTL prose when the boundary can affect visual ordering or punctuation.

Example:

``` html
<p>نام کاربر <span dir="ltr">admin</span> است</p>
```

### RTL-044 — URLs

**MUST**

URLs embedded in RTL prose must be isolated.

Example:

``` html
<p>سایت <bdi>https://example.com</bdi> را ببینید</p>
```

or:

``` html
<span dir="ltr">https://example.com</span>
```

### RTL-045 — Unknown Direction Names

**SHOULD**

Use `<bdi>` for user-generated names or values whose direction is unknown.

Example:

``` html
<p>کاربر <bdi>John</bdi> پیام داد</p>
```

### RTL-046 — Unicode Bidi Isolation

**MAY**

For server-rendered or stored text where HTML isolation is unavailable, Unicode isolation characters may be used:

- `\u2066` LRI
- `\u2067` RLI
- `\u2068` FSI
- `\u2069` PDI

Do not introduce invisible characters into stored data without a clear serialization and debugging strategy.

### RTL-047 — Mixed Content Testing

**MUST**

Test real mixed-direction strings rather than relying on symmetric test text.

Examples:

``` text
کاربر admin است
شماره پیگیری: ABC-12345
سایت https://example.com را ببینید
شناسه تراکنش TXN-2026-000123
```

## Layouts

### RTL-048 — Logical Navigation Start

**SHOULD**

Primary navigation normally begins on the logical start side of an RTL layout.

A product may intentionally keep a navigation rail on a fixed physical side. Such behavior must be an explicit design-system decision, not an accidental result of hardcoded `left`/`right`.

### RTL-049 — Sidebar Positioning

**MUST**

When sidebar position is intended to follow writing direction, use logical positioning:

``` css
.sidebar {
  inset-inline-start: 0;
}
```

### RTL-050 — Breadcrumbs

**SHOULD**

Breadcrumb progression follows RTL reading order:

``` text
خانه ← محصولات ← جزئیات
```

The exact separator icon must also respect directional semantics.

### RTL-051 — Progress

**SHOULD**

Sequential progress indicators normally start from the logical start side. For RTL this commonly means the first step is on the right and progress fills toward the left.

### RTL-052 — Pagination

**SHOULD**

Pagination follows RTL reading order. "Next" is normally on the logical end side and "Previous" on the logical start side, with directional icons matching their semantic meaning.

### RTL-053 — Tabs

**SHOULD**

Tabs normally begin from the logical start side.

### RTL-054 — Modal Close Button

**SHOULD**

Close-button placement must follow the established component convention in the design system. Do not assume that every RTL modal must use the physical top-left or every LTR modal the physical top-right.

If the component mirrors its placement with direction, use logical positioning.

### RTL-055 — Tooltips and Popovers

**MUST**

Tooltip/popover positioning logic must not assume a physical side when the intended behavior is directional.

Use logical placement where the positioning library supports it, and test collision/fallback behavior in both directions.

### RTL-056 — Tables

**SHOULD**

Table column order may follow RTL reading order, but technical and financial tables may intentionally preserve a fixed column order.

The decision must be based on the table's semantics and the product's domain.

## Buttons and Component Composition

### RTL-057 — Icon/Text Ordering

**MUST**

Icon placement must follow semantic intent, not accidental DOM order.

For a normal RTL flex row, the first child appears on the logical start side. Use explicit reversal only when the component intentionally requires the icon on the opposite side.

### RTL-058 — Primary and Secondary Actions

**SHOULD**

Action ordering should follow the general design-system convention for the product. Do not infer button priority solely from RTL direction.

For example, a product may define:

``` text
[عمل اصلی] [لغو]
```

or the reverse for a specific interaction pattern. Consistency within the design system is more important than an assumed universal RTL order.

## Anti-Patterns

### RTL-059 — Missing Root Direction

**MUST NOT**

A Persian page without correct root direction is invalid.

### RTL-060 — Hardcoded Directional CSS

**MUST NOT**

Avoid `left`/`right` when the intent is logical flow.

### RTL-061 — Double Reversal

**MUST NOT**

Do not combine RTL with unnecessary `row-reverse`, mirrored DOM order, and mirrored icons.

### RTL-062 — Mirrored Object Icons

**MUST NOT**

Do not apply `scaleX(-1)` to user, document, heart, star, search, or other non-directional object icons.

### RTL-063 — Decorative Letter Spacing

**MUST NOT**

Do not apply Latin-style tracking to normal Persian text.

### RTL-064 — Broken Persian Font Fallback

**MUST NOT**

Do not allow Persian content to silently fall back to an unsuitable Latin-only font.

### RTL-065 — Gregorian-Only User Presentation

**MUST NOT**

Do not expose Gregorian-only dates in a Persian-first interface when the product requires Persian calendar presentation.

### RTL-066 — Incorrect Numeral Mixing

**MUST NOT**

Do not mix Persian and Western digits arbitrarily inside the same semantic data field.

### RTL-067 — RTL Technical Fields

**MUST NOT**

Do not use RTL direction for emails, URLs, code, IDs, or other technical values whose correct visual order is LTR.

### RTL-068 — Unisolated URLs and IDs

**MUST NOT**

Do not place URLs, identifiers, or English names into RTL prose without testing or isolation where bidi ambiguity exists.

### RTL-069 — Physical Layout Assumptions

**MUST NOT**

Do not assume that every sidebar, modal, table, or chart must physically mirror. Determine whether the behavior is semantic, logical, or intentionally physical.

### RTL-070 — Latin Placeholder in Persian Context

**MUST NOT**

Do not use an unexplained English placeholder in a Persian field.

### RTL-071 — Missing ZWNJ

**MUST NOT**

Review Persian copy for words that require ZWNJ.

### RTL-072 — Code Blocks

**MUST**

Code blocks must use LTR direction:

``` html
<pre dir="ltr"><code>const value = 123;</code></pre>
```

### RTL-073 — Mixed Persian/English Without Testing

**MUST NOT**

Do not approve a Persian UI using only artificial strings such as `متن تست`. Use realistic mixed content.

## Testing Matrix

### RTL-074 — Real Persian Content

**MUST**

Test with realistic Persian sentences containing:

- Short text
- Long text
- ZWNJ
- Persian punctuation
- Numbers
- English terms
- URLs
- IDs
- Dates
- Currency values

### RTL-075 — Mixed Direction

**MUST**

Test at minimum:

``` text
Persian + English
English + Persian
Persian + URL
Persian + code
Persian + ID
Persian + number
Persian + date
Persian + currency
```

### RTL-076 — Responsive Testing

**MUST**

Validate RTL behavior at representative widths, for example:

``` text
320px
375px
768px
1024px
1440px
```

Include overflow and wrapping behavior.

### RTL-077 — Long Content

**MUST**

Test:

- Long Persian labels
- Long English labels
- Long URLs
- Long IDs
- Long usernames
- Long validation messages
- Multi-line table cells

### RTL-078 — Truncation

**SHOULD**

Test ellipsis, line clamp, tooltips, and accessible full-value exposure for both Persian and LTR content.

### RTL-079 — Browser Testing

**SHOULD**

Test the target browsers, including:

- Chrome
- Firefox
- Safari
- Target mobile browsers

Focus especially on bidi, font rendering, form controls, autofill, and calendar formatting.

### RTL-080 — Paste and Autofill

**MUST**

Test:

- Persian paste into Persian fields
- English paste into Persian fields
- Persian paste into LTR technical fields
- Browser autofill
- Copy/paste of numbers
- Copy/paste of URLs and IDs

### RTL-081 — Calendar Testing

**MUST**

Verify Jalali rendering, month names, week start, date boundaries, and timezone-sensitive values in supported browsers and runtimes.

### RTL-082 — Dark Mode

**SHOULD**

Test Persian typography in both light and dark modes, especially thin glyphs, contrast, and font rendering.

### RTL-083 — Native Persian Review

**SHOULD**

Have a fluent Persian reader review production-facing Persian copy and rendering. Technical correctness alone does not guarantee natural Persian copy.

## Accessibility Cross-Reference

Accessibility requirements are defined by:

``` text
domains/concern/02-accessibility-critical-anti-slop.md
```

This file does not duplicate the full accessibility specification.

RTL/Persian implementation must still be validated for:

- Screen-reader language
- Focus order
- Keyboard navigation
- Form labeling
- Error announcement
- Accessible names
- Direction-aware content

Visual RTL correctness must never be used as a substitute for semantic accessibility.

## Verification Methods

Before approving a Persian/RTL UI, verify:

- [ ] Root `dir` and `lang` are correct.
- [ ] Logical CSS is used for directional layout.
- [ ] No accidental `left`/`right` hardcoding exists.
- [ ] No unnecessary `row-reverse` is used.
- [ ] Persian font support is confirmed.
- [ ] Persian line-height is readable.
- [ ] ZWNJ is correct where required.
- [ ] Persian punctuation is correct.
- [ ] Numeral conventions are defined by data type.
- [ ] Technical values use an appropriate LTR representation.
- [ ] User-facing Persian dates use the intended calendar.
- [ ] Storage/API date formats remain machine-readable.
- [ ] Directional icons follow semantic meaning.
- [ ] Object icons and logos are not mirrored.
- [ ] URLs and IDs are isolated where needed.
- [ ] Email/URL/code fields are LTR.
- [ ] Unknown-direction text uses `dir="auto"` where appropriate.
- [ ] Tables have intentional column order and numeric alignment.
- [ ] Sidebar/modal/popover behavior follows the design-system decision.
- [ ] Responsive RTL behavior is tested.
- [ ] Long and mixed-direction content is tested.
- [ ] Browser autofill and paste are tested.
- [ ] Persian content has been reviewed by a fluent reader.

## Response to Violation

When a rule in this file is violated, report:

Violation: RTL-{NNN}
Reason: {one-line reason}
Correction: {smallest fix}

For multiple violations, report each rule ID separately.

Do not replace a technical correction with a generic explanation.

## Design Principle

The goal of this layer is not to mirror every visual element.

The goal is to produce an interface that is:

- semantically RTL,
- typographically natural for Persian,
- correct for mixed-direction content,
- consistent with the project's design system,
- safe for technical and financial data,
- accessible,
- testable,
- and maintainable across LTR/RTL variants.

RTL should be treated as a first-class layout and content mode, not as a final visual transformation applied to an LTR interface.