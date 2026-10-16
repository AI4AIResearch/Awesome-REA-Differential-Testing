# Investigation template

Copy this template into a new lab or case study. Replace every placeholder with an observed value; omit measurements you did not take.

## Question and target

- Question: one behavior or function to explain.
- Target: name, origin, version, redistribution license, and SHA-256.
- Scope: exact files, functions, or capture entries under analysis.

## Environment and commands

- OS and architecture:
- REA version and provider version, if used:
- Other tools and versions:
- Exact commands and required inputs:
- Expected elapsed time or cost only if actually measured:

## Findings

| Claim | Evidence location | How observed | Confidence and limits |
| --- | --- | --- | --- |
| A concrete behavior | File and line, address, offset, method, or capture entry | Static instruction, decompiler, runtime trace, or test | State the unresolved alternative |

## Reproduction and checks

Record the minimal steps, input cases, expected outputs, actual outputs, and failures. Keep a reference implementation or independent check where possible. A successful tool invocation alone does not establish the semantic correctness of its conclusions.

## Coverage

State what was not executed, what required a separate tool, and what evidence would change the conclusion. Link the original sources and keep publishable evidence separate from private target material.
