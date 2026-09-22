---
name: plan
description: Discovers bounded target, dependency, consumer and test context and records an evidence-mapped implementation plan in the task PR.
---

# Plan

## Goal
Find the smallest safe change and persist enough references for another ChatGPT Web session to resume.

## New task discovery
1. Read project context and the user request.
2. Search for request keywords, identifiers, error messages and likely file names.
3. Fetch only promising files.
4. Identify exact target symbols/files.
5. Expand a bounded neighborhood:
   - imports/requires used by the target;
   - direct consumers/usages of target symbols/modules;
   - related tests;
   - config/schema/API/framework contracts.
6. Record each loaded source reference in `context.observed_files` with current GitHub blob SHA.

If retrieval misses a target, use another scoped search. Do not conclude "no impact" merely because one search returned no results.

## By mode

### bug_fix
- reproduce/locate the symptom when possible;
- trace to evidence-supported root cause;
- identify or plan a regression test;
- include nearby consumer/test impact.

### refactor
- target is usually explicit;
- discover all reasonably findable direct consumers;
- capture baseline behavior/checks before changing structure;
- list invariants that must remain unchanged.

### feature/change
- record desired behavior and compatibility constraints;
- identify affected public/config/data contracts.

## Acceptance criteria
Assign stable IDs such as AC1. Each criterion must state an observable expected result and feasible evidence. Use `unverified` rather than inventing evidence.

## PR manifest update
Set:
- mode/request/status;
- targets/symbols;
- dependencies;
- consumers;
- tests/config files;
- observed file SHAs;
- acceptance criteria;
- uncertainty.

The manifest is routing state, not a place to paste source code.

## Output
Summarize target files/symbols, dependency/consumer neighborhood, tests, ordered implementation steps, verification evidence and known uncertainty.
