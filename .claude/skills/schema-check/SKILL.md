---
name: schema-check
description: Validate that database models and Pydantic schemas align with the phase plan data model. Use after modifying models or migrations.
argument-hint: [phase-number]
user-invocable: true
allowed-tools: Read, Glob, Grep
---

# Schema Consistency Checker

Check schema alignment for: $ARGUMENTS

## Instructions

1. Read the relevant phase plan from `.claude/phase{1,2,3}_plan.md` — specifically the "Data Model" section
2. Find all SQLAlchemy/Alembic models in `libs/storage/` and `migrations/`
3. Find all Pydantic schemas in `libs/schemas/`
4. Compare and report:
   - Tables/columns defined in plan but missing from code
   - Tables/columns in code but not in plan (intentional additions?)
   - Type mismatches (e.g., plan says vector(384) but code uses different dimension)
   - Missing indexes noted in the plan
   - Missing constraints (unique, FK, etc.)
5. Output a clear checklist of discrepancies
