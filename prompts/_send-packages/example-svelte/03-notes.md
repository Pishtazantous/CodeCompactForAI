---
id: example-svelte-notes
title: "Example: Notes on the Svelte Generation"
lang: en
category: helper
version: 1
---

# Example: Notes on the Svelte Generation

## What to Look For in the Output

When the AI returns the Svelte file, check these specific things:

1. **Runes, not stores.** Svelte 5 uses `$state`, `$derived`, `$effect`,
   and `$props` as the primary reactivity model. `writable` and `readable`
   stores still exist but are not the default. If the file focuses on
   stores, it was written for Svelte 4. Ask for a revision.

2. **`$effect` discipline.** The `$effect` rune is analogous to
   `useEffect` in React and has similar anti-patterns (using it for
   derived state, infinite loops, side effects during render).

3. **Component props with `$props`.** Svelte 5 uses `let { name } =
   $props()` instead of `export let name`. The file should reflect this.

4. **`<script>` not `<script context="module">`.** The `context` attribute
   was renamed to `<script module>` in Svelte 5.

5. **No `on:click`.** Svelte 5 prefers `onclick` (lowercase, no colon).
   Both work; the new syntax is the default.

6. **Snippets over slots.** Svelte 5 introduces `{#snippet}` and
   `{@render}` alongside the existing `<slot>`. The file should
   acknowledge both.

7. **No reference to SvelteKit routing.** `+page.svelte`,
   `+layout.svelte`, and `+server.ts` belong to the SvelteKit layer,
   not the Svelte layer.

## Common Failures

When generating this file, the following failures are common:

| Failure | How to spot it | Fix |
|---|---|---|
| Svelte 4 style | Uses `export let` for props | Ask for `$props()` |
| Store focus | `writable` used as default state | Ask for `$state` |
| Vue-like | Refers to "reactivity" in Vue terms | Ask for Svelte runes |
| Too general | Rules apply to any framework | Point to Universal or frontend delivery |
| Too long | Over 400 lines | Ask to split into Svelte and SvelteKit |

## What the File Should NOT Include

- Rules from React (hooks, `useMemo`, `useEffect` dependency arrays).
- Rules from Vue (composition API, `reactive`, `ref`).
- Rules from the frontend delivery file (component discipline, data
  fetching patterns).
- Rules from the architecture file (layering, folder structure).
- Rules from Universal (fabrication, over-engineering).

## Expected Length

280-320 lines. If it is under 250, the file is likely too shallow. If
over 350, it is probably covering SvelteKit or restating other layers.

## After the File Is Accepted

1. Save to `prompts/domains/framework/02-svelte-anti-slop.md`.
2. Update `prompts/README.md` to include the new file in the framework
   list.
3. Optionally, generate `02-sveltekit-anti-slop.md` next, using the
   Svelte file as a reference.

## Time Budget

Generating this file with a frontier model takes 2-4 minutes. Review
takes 5-10 minutes. If review takes longer, the prompt likely needs
refinement for future files.
