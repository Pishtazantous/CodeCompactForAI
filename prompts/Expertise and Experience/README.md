# Expertise and Experience with Anti-Slop

Each prompt in this folder has two layers:

1. **Expertise layer** — principles, tools, patterns to follow.
2. **Anti-Slop layer** — traps specific to that expertise to avoid.

## Governing Principle

Expertise tells the AI **what to do**.
Anti-Slop tells the AI **what not to do**.
Together, they remove low-quality output from the response.

## How to Use

```
1. prompts/01-system.md                                     (base)
2. prompts/02-manifest.md + manifest                        (kickoff)
3. prompts/Anti-AI-Slop/00-master-anti-slop.md              (generic anti-slop)
4. prompts/Expertise and Experience/00-anti-slop-core.md    (project anti-slop)
5. prompts/Expertise and Experience/XX-*.md                 (domain expertise)
6. prompts/03-bug-fix.md                                    (task)
```

## Steel Rule

**Never combine two expertise prompts in one session.** If a task needs both TypeScript
and Security, first send the TypeScript prompt, finish the task, then start a new
session with the Security prompt.

## Maintenance

Every time you spot a new slop pattern in code review, add it to the
"Domain-Specific Anti-Slop Rules" section of the relevant file.
