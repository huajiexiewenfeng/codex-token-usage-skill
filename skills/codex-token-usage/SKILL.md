---
name: codex-token-usage
description: Summarize Codex token usage from local Codex Desktop or CLI session JSONL logs. Use when the user asks to count, audit, total, compare, or report Codex/OpenAI token usage for a period such as today, this week, last month, a calendar month, a rolling 30-day window, peak week, peak day, input/output/cached/reasoning breakdown, or net token usage.
---

# Codex Token Usage

## Overview

Use the bundled script to read local Codex session logs and produce a consistent token usage report. Prefer deterministic script output over ad hoc `rg` summaries.

## Workflow

1. Identify the reporting window from the user request.
   - If the user asks for "one month" or "last month" without naming a calendar month, use the last 30 local calendar days ending today.
   - If the user asks for "this month" or names a specific month, use that calendar month, clipped to today if it is the current month.
   - Use the user's timezone from context when available; default to the local machine timezone only if no timezone is provided.
2. Run `scripts/codex_token_usage.py`.
3. Report results in a table with these rows: total, input, cached input, output, reasoning output, non-cached input, net usage, cache hit rate, and daily average total.
4. Include the peak day and busiest week with exact dates.
5. State the net usage formula.

## Script

Run from the skill directory or pass an absolute script path:

```bash
python scripts/codex_token_usage.py --days 30 --timezone Asia/Shanghai
```

Useful options:

```bash
python scripts/codex_token_usage.py --start 2026-03-30 --end 2026-04-28 --timezone Asia/Shanghai
python scripts/codex_token_usage.py --month 2026-04 --timezone Asia/Shanghai
python scripts/codex_token_usage.py --codex-home C:\Users\admin\.codex --days 30
python scripts/codex_token_usage.py --days 30 --format json
python scripts/codex_token_usage.py --days 30 --format markdown --language en
```

If `python` is not on PATH, use the bundled Codex runtime if available:

```bash
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\codex_token_usage.py --days 30 --timezone Asia/Shanghai
```

## Definitions

- `total`: sum of `last_token_usage.total_tokens` across `token_count` events.
- `input`: sum of `last_token_usage.input_tokens`.
- `cached input`: sum of `last_token_usage.cached_input_tokens`.
- `output`: sum of `last_token_usage.output_tokens`.
- `reasoning output`: sum of `last_token_usage.reasoning_output_tokens`.
- `non-cached input`: `input - cached input`.
- `net usage`: `non-cached input + output`.
- `cache hit rate`: `cached input / input`.
- `daily average total`: `total / number of local calendar days in the reporting range`.

Avoid summing `total_token_usage` for each event because it is cumulative within a session and will overcount. Sum `last_token_usage` instead.

## Response Format

Use a concise Markdown table. Localize row labels to the user's language. For Chinese responses, use labels like total, Input, Cached input, Output, Reasoning output, non-cached Input, and net usage in Chinese where appropriate.

```markdown
| Metric | Tokens | Notes |
|---|---:|---|
| Total | 730,366,547 | Sum of `total_tokens` |
| Input | 724,204,405 | Input tokens, including cached input |
| Cached input | 640,615,168 | Cached input tokens |
| Output | 3,239,893 | Output tokens |
| Reasoning output | 456,198 | Reasoning output tokens |
| Non-cached input | 83,589,237 | `Input - Cached input` |
| Net usage | 86,829,130 | `Non-cached input + Output` |
| Cache hit rate | 88.44% | `Cached input / Input` |
| Daily average total | 24,345,552 | `Total / days in range` |
```

Then add one sentence for the peak day and busiest week:

```markdown
The peak day was 2026-04-01: 72,000,000 tokens.
The busiest week was 2026-03-30 to 2026-04-05: 244,371,620 tokens.
```

Use `--format json` when the result will feed another script, dashboard, automation, or report generator. Use Markdown for direct user answers.
