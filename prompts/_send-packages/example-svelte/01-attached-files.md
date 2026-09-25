---
id: example-svelte-attached
title: "Example: Files Attached for Svelte Generation"
lang: en
category: helper
version: 1
---

# Example: Files Attached for Svelte Generation

For the worked example, the following files were attached to the AI
conversation. Each is a link to its actual file in the repository.

## Attached Files

1. `_universal/00-master-anti-slop.md`
2. `domains/framework/02-architecture-anti-slop.md`
3. `domains/framework/02-vue-anti-slop.md`
4. `domains/framework/02-react-anti-slop.md`
5. `domains/delivery/02-frontend-anti-slop.md`

## Why These Files

- `00-master-anti-slop.md`: to prevent repeating universal rules.
- `02-architecture-anti-slop.md`: Svelte is a framework; architecture
  rules apply.
- `02-vue-anti-slop.md`: closest paradigm to Svelte (reactivity,
  component model).
- `02-react-anti-slop.md`: second closest, for style comparison.
- `02-frontend-anti-slop.md`: Svelte is a frontend framework; the
  frontend delivery rules are a required dependency.

## Total Attachment Size

Approximately 90 KB, or about 22,000 tokens. Well within the context
window of frontier models.

## Order of Sending

1. First message: "Read the attached files. Confirm you have read
   them and are ready."
2. Wait for confirmation.
3. Second message: the filled master prompt (see the next file).
