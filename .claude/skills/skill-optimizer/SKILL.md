---
name: skill-optimizer
description: Optimize and restructure Claude Code skills in this project. Use when a new skill is added, or when asked to review/optimize skills. Identifies redundancy, extracts shared logic, and ensures token efficiency.
allowed-tools: Read, Glob, Grep, Write, Edit
---

# Skill Optimizer

Review all skills in the project and optimize for token efficiency and maintainability. Run this after adding or modifying skills.

---

## Step 1: Inventory

Scan all skill files:
```
Glob: .claude/skills/**/SKILL.md
Glob: .claude/skills/shared/*.md
```

For each skill, extract:
- name, description, allowed-tools
- Approximate line count (proxy for token cost)
- References to shared files

---

## Step 2: Analyze

Check for:

### Redundancy
- Duplicated instructions across skills (candidates for shared extraction)
- Overlapping trigger descriptions that could confuse skill selection
- Repeated tool usage patterns

### Token Efficiency
- Verbose instructions that could be compressed
- Examples that could be shortened or removed
- Shared references that are loaded but not used

### Consistency
- Naming conventions across skills
- Output format consistency
- Shared reference usage

---

## Step 3: Propose Changes

Present findings as a checklist:

```
## Optimization Report

### Redundancy
- [ ] Description of redundancy → proposed fix

### Token Savings
- [ ] Description of saving → estimated line reduction

### Consistency
- [ ] Description of inconsistency → proposed fix
```

---

## Step 4: Apply (with confirmation)

Ask the user before applying changes. Then:
1. Extract shared logic to `shared/` reference files
2. Update skill files to reference shared logic
3. Remove redundant content
4. Verify no skill references are broken (Grep for all `../shared/` paths)

Report the before/after line counts as a summary.
