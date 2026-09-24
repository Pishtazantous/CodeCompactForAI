---
id: 14-checklist
title: "Pre-Response Checklist"
lang: en
depends_on: []
category: task
version: 2
---

# Pre-Response Checklist

Before sending any response, verify every item:

- [ ] Have I seen the manifest for this session?
- [ ] Do I understand the codemerge.py rules (fetch, search, diff)?
- [ ] Did I use the `codemerge-fetch` format for every file request?
- [ ] Did I explain why I need each requested file?
- [ ] Did I stay within the file limit (10 to 15 per request)?
- [ ] Did I match the project's existing style in new code?
- [ ] Did I provide complete files, not fragments?
- [ ] Did I declare the rollback point at the top of editing responses?
- [ ] Did I state assumptions explicitly when anything was ambiguous?
- [ ] Did I declare the scope (what changed, what did not)?
- [ ] Did I avoid introducing new dependencies without permission?
- [ ] Did I avoid new patterns not present in the project?
- [ ] Did I avoid TODO / placeholder / "rest of file" markers?
- [ ] Did I avoid emoji in code, comments, and normative text?
- [ ] If I could not complete the task, did I say so clearly and
      explain why?
- [ ] Did I end the response with a "Next Step" section?

If any box is unchecked, fix it before sending.