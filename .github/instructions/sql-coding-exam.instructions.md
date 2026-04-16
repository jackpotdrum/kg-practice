---
description: "Use when user asks SQL practice in Japanese, especially phrases like 問題を出して, 記録して, 解説して, 採点して, and when context references コーディング試験対策_SQL. Enforce Medium-Hard coding-exam style outputs."
name: "SQL Coding Exam Coach Rules"
applyTo: "コーディング試験対策_SQL/**"
---
# SQL Coding Exam Scoped Rules

## Scope
- Apply these rules only for tasks related to the folder コーディング試験対策_SQL.
- If the task is outside this folder, do not force these rules.

## Source of Truth
- Before generating SQL questions, grading, explanations, or study records, read and follow:
  - [コーディング試験対策_SQL/prompt.md](../../コーディング試験対策_SQL/prompt.md)
- If any conflict exists within SQL-coaching tasks, prioritize that file.

## Required Behavior
- Difficulty must be Medium or Hard.
- Use Japanese.
- For 「問題を出して」, follow the required exam-style structure in prompt.md.
- For SQL answer review, follow the required grading and feedback order in prompt.md.
- For 「記録して」, generate output using the required storage template in prompt.md.

## Quality Guardrails
- Avoid basic drill-only questions unless user explicitly asks for basics.
- Prefer interview-frequent themes (Top-N per group, latest dedup, streak, funnel, cohort, sessionization, window functions, etc.).
- Keep specs complete (output columns, sort order, edge conditions).
