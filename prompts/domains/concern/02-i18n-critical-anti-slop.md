---
id: 02-i18n-critical-anti-slop
title: "i18n-Critical Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop]
category: domain
domain_type: concern
version: 1
---
# i18n-Critical Anti-Slop Layer
Layered under `_universal/00-master-anti-slop.md`. Universal rules and
the general requirement to use the project's language conventions are
not repeated here. This layer governs behavior that changes across
supported languages, locales, scripts, calendars, and reading directions.
## 1. Applicability
Send this layer when a change affects any of these surfaces:
- user-visible text or formatting;
- locale selection and fallback;
- translated content supplied by users or administrators;
- dates, times, numbers, currencies, addresses, or units;
- bidirectional layout or right-to-left behavior;
- plural-sensitive notifications, commerce, messaging, or accessibility
  announcements;
- persistence, search, sorting, routing, or analytics of localized data.
A single-language internal tool does not need this layer unless it will
import localized data, serve several regions, or change locale-aware
storage.
## 2. Supported Locales
### 2.1 Declare the Contract
1. Enumerate supported application locales, not browser guesses alone.
2. Map each locale to a language and, when needed, a regional variant.
3. Distinguish translated languages from formatting-only variants.
4. Define the default locale and the fallback order explicitly.
5. Use canonical identifiers throughout configuration, APIs, and storage.
6. Normalize external locale input at the boundary.
Do not infer user preference solely from `Accept-Language`; combine it
with product policy, availability, and a user override.
### 2.2 Missing Translations
1. Fail validation when a required message key is absent from a target
   locale rather than silently rendering empty content.
2. Use the documented fallback only during controlled development or
   migration.
3. Report the key and locale without exposing user content.
4. Keep fallback messages understandable to maintainers.
5. Block release for missing critical flow keys when translation
   completeness is part of the release contract.
## 3. Message Key Discipline
### 3.1 Stable Semantic Keys
1. Name keys by meaning, not by English source text.
2. Keep one key when every locale uses the same message structure.
3. Add variants only when grammatical or semantic differences require
   them.
4. Never concatenate sentence fragments from separate keys.
5. Keep interpolation fields named by role: `userName`, `count`, `dueDate`.
6. Remove obsolete keys through the repository's catalog workflow.
### 3.2 Parameter Safety
1. Define accepted interpolation fields and their types in the message contract.
2. Validate or type-check interpolation arguments at build time.
3. Use locale-aware plural APIs for counts, not string replacement.
4. Keep user data separate from translator-controlled format text.
5. Escape interpolation for the output context defined by the framework.
A key rename is a contract change. Update every locale in the same
change and search dynamic key construction before renaming.
### 3.3 Context and Gender
1. Use explicit context keys when words differ by grammatical role.
2. Do not encode gender assumptions unless the product and target locales
   require them.
3. Provide forms approved by translators for formal and informal address.
4. Keep variants narrow and documented so translators can select them.
5. Do not infer language nuance from the English source alone.
## 4. Pluralization and Messages
### 4.1 Use the Runtime's Plural Rules
1. Select plural categories with the runtime's message-format library.
2. Supply the exact numeric value required by that runtime.
3. Test one value from every plural category required by the locale.
4. Cover decimal and compact formatting when the message exposes them.
5. Do not reproduce English `one` and `other` assumptions in application
   code.
### 4.2 Interpolation in Every Required Form
1. Give every selected plural form the same interpolation fields.
2. Validate parameter sets across all forms.
3. Keep translated examples free from accidental markup.
4. Test messages with empty, long, and script-mixed values.
5. Verify that accessibility announcements expose the final localized
   message, not a raw numeric template.
## 5. Dates, Times, Numbers, and Currencies
### 5.1 Use the Intl Equivalent of the Platform
1. Format dates and times with the project's locale-aware API.
2. Specify a time zone for values representing an instant.
3. Store instants in the repository's canonical storage form.
4. Distinguish calendar date, local time, and time-zone-specific time.
5. Use the locale's calendar and numbering system only when required.
### 5.2 Number Semantics
1. Use locale-aware grouping and decimal separators.
2. Pass numeric values as numbers, not preformatted strings.
3. Preserve precision rules for currencies, units, and measurements.
4. Sort by numeric value, not localized display text.
5. Use locale-aware comparison for user-facing alphabetical collation.
### 5.3 Currency and Units
1. Format currency with its ISO code or the product's explicit policy.
2. Keep amount and currency as separate data until presentation.
3. Do not parse localized display text with fixed punctuation.
4. Use locale-aware measurement formatting for units.
5. Test negative values, grouping, and compact display where supported.
## 6. Bidirectional Layout
### 6.1 Direction Is a Runtime Concern
1. Set document or component direction from the active locale.
2. Use logical CSS properties for margins, padding, borders, and insets.
3. Use bidirectional isolation for user-controlled mixed-direction text.
4. Keep icons that indicate direction aware of locale direction.
5. Test embedded numbers, punctuation, phone numbers, and code fragments.
### 6.2 Layout Testing Matrix
1. Test at least one left-to-right locale and one right-to-left locale.
2. Test mixed-direction content, not only fully translated pages.
3. Verify focus order, truncation, overlays, charts, and tabular data.
4. Use explicit physical overrides only for visual decorations that must
   mirror regardless of meaning.
5. Inspect with real translated content; Latin sample copy cannot expose layout
   expansion or direction defects.
## 7. Locale-Aware Persistence and Transport
### 7.1 Store Stable Identity
1. Store localized text separately from stable domain identifiers.
2. Store locale with a localized value when its meaning depends on locale.
3. Normalize locale identifiers when matching records or routes.
4. Do not use translated text as a database key, enum, or permission.
5. Define migration behavior for records that contain embedded locale
   assumptions.
### 7.2 Transport Stable Contracts
1. Send machine values as typed fields with explicit units or codes.
2. Let the presentation layer format them for the active locale.
3. Parse incoming numeric and date fields with known formats or typed
   transport primitives.
4. Reject ambiguous user input with a localized, actionable message.
5. Keep time zones explicit at process and inter-service boundaries.
## 8. Domain-Specific Rules
### 8.1 i18n Rules
1. Declare supported locales and fallback policy.
2. Keep stable semantic keys and validated interpolation.
3. Use runtime plural categories for every supported language.
4. Format dates, times, numbers, currencies, and units with locale-aware
   APIs.
5. Use logical layout properties and test right-to-left locales.
6. Keep locale-dependent storage and transport data explicit.
## Domain-Specific Anti-Patterns
### 9.1 English Plural Logic
BAD:
```javascript
const message = `${count} ${count === 1 ? "item" : "items"}`;
return t(message);
```
Application code assumes English plural rules for every locale.
GOOD:
```javascript
return t("cart.itemCount", { count });
```
The catalog owns locale-specific plural categories.
### 9.2 Translated Display Values as Data
BAD:
```javascript
const amount = new Intl.NumberFormat(locale, {
  style: "currency",
  currency: "EUR",
}).format(1200);
await saveOrder({ amount });
```
Formatted display text loses the amount and currency contract.
GOOD:
```javascript
await saveOrder({ amountMinor: 1200, currency: "EUR" });
```
Typed data survives the locale boundary until presentation.
### 9.3 Physical CSS in Right-to-Left Layout
BAD:
```css
.drawer {
  left: 16px;
  margin-right: 24px;
  border-left: 1px solid;
}
```
Physical properties freeze the layout on one reading direction.
GOOD:
```css
.drawer {
  inset-inline-start: 16px;
  margin-inline-end: 24px;
  border-inline-start: 1px solid;
}
```
Logical properties follow the active reading direction.
### 9.4 Fragmented Sentences
BAD:
```javascript
return t("cart.total") + ": " + formatMoney(total);
```
Concatenation prevents translators from controlling word order.
GOOD:
```javascript
return t("cart.totalWithAmount", { total: formatMoney(total) });
```
The translator controls the complete sentence and its word order.
### 9.5 English-Only Right-to-Left Validation
BAD:
```html
<section dir="rtl">
  <p>Example item</p>
  <span>Invoice 42</span>
</section>
```
Latin-only content cannot prove bidirectional layout behavior.
GOOD:
```html
<section dir="rtl">
  <p lang="he">חשבונית 42</p>
  <bdi>ABC-42</bdi>
</section>
```
The test includes translated and mixed-direction data.
## 10. Response to Violation
If a previous response violated this layer:
```text
In the previous response, [specific i18n rule] was violated. Correction:
[locale-corrected implementation]
```
State the affected locale, form, or direction when known. Do not
localize unrelated code while applying the correction.
