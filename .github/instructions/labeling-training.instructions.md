---
description: "Use when user asks labeling training in Japanese, especially phrases like 問題を出して, 記録して, 模範解答, 差分コメント, and when context references 1日3分ラベリング."
name: "Labeling Training Coach Rules"
applyTo: "1日3分ラベリング/**"
---
# Labeling Training Scoped Rules

## Scope
- Apply these rules only for tasks related to the folder 1日3分ラベリング.
- If the task is outside this folder, do not force these rules.

## Source of Truth
- Before generating labeling questions, model answers, feedback, or study records, read and follow:
  - [1日3分ラベリング/prompt.md](../../1日3分ラベリング/prompt.md)
- If any conflict exists within labeling-coaching tasks, prioritize that file.

## Required Behavior
- Use Japanese.
- For 「問題を出して」, follow the required structure in prompt.md.
- Alternate question styles over time so that one format is not overused (bullet-style and paragraph-style).
- For answer review, provide model answer + concise gap feedback + rationale for category labels.
- For 「記録して」, generate output using the required storage template in prompt.md.

## Quality Guardrails
- Keep category labels within 4 and simple labels within 10.
- Keep problem statements IT-engineer relevant.
- Vary audience persona among: 顧客エンジニア / 経営者 / 運用担当者.
- Treat model answers as one good example, not the only correct answer.
