---
name: codex-token-usage
description: Use when the user asks to count, audit, compare, or report local Codex Desktop or CLI token usage, including daily token counts, total or net usage, cache hit rate, peak periods, or an offline HTML usage dashboard.
---

# Codex Token Usage

## Overview

Use the bundled script to read local Codex session logs and produce a consistent token usage report. Prefer deterministic script output over ad hoc `rg` summaries.

**Default: generate the fixed HTML dashboard and open it in the system's default external browser.** This also applies to plain requests such as “统计本周用量” or “统计下 token”. Do not answer with only a Markdown table unless the user explicitly requests text, Markdown, JSON, or no browser. Re-read this installed file when reusing an old task; earlier task instructions may describe the old Markdown default.

## Workflow

1. Identify the reporting window from the user request.
   - If the user asks for "one month" or "last month" without naming a calendar month, use the last 30 local calendar days ending today.
   - If the user asks for "this month" or names a specific month, use that calendar month, clipped to today if it is the current month.
   - Use the user's timezone from context when available; default to the local machine timezone only if no timezone is provided.
   - “This week” means Monday through today in that timezone; pass explicit `--start` and `--end` dates.
2. Run the installed `scripts/codex_token_usage.py` from the user's workspace with the reporting dates and timezone. Resolve the script from the skill directory containing this file. Use the active `CODEX_HOME` for logs when present; do not infer log location from a legacy skill installation path.
3. Unless explicitly overridden, use HTML (the CLI default). The script writes `output/token-usage-<start>-<end>.html` under the working directory and requests the system's default external browser to open it. `--output` overrides the file path. Keep reports outside the skill source directory.
4. Do not substitute an in-app browser preview. If opening fails or is blocked, provide the saved file link and accurately state that it was not opened; do not bypass host restrictions. A successful OS launch request alone is not evidence that the page rendered.
5. Return a clickable absolute HTML file link, exact date range and a short summary. The dashboard contains daily counts, peak periods and metric definitions; do not replace it with a long Markdown table.
6. For explicit text/Markdown requests, pass `--format markdown`; for machine-readable requests, pass `--format json`. These formats print to stdout unless `--output` is provided and do not open a browser. For automation or a user request not to open a browser, use `--no-open` with HTML.

## Script

Run from the user's workspace, passing the installed script's absolute path (relative examples below are shorthand):

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
python scripts/codex_token_usage.py --days 30 --timezone Asia/Shanghai --format html --output /path/to/output/token-usage.html
python scripts/codex_token_usage.py --days 30 --timezone Asia/Shanghai --no-open
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

By default, provide the HTML file link and a short summary after requesting the external browser. Only for an explicit text/Markdown request, use the concise table below. Localize row labels to the user's language.

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

Use `--format json` when the result will feed another script, automation, or report generator. Use Markdown for text answers. All formats support `--output` for UTF-8 file output.

## HTML Dashboard

The single HTML file embeds its CSS, JavaScript and aggregate report data; it opens offline without a build step, server or CDN. JavaScript must be enabled. Use `--language zh` (default) or `--language en`.

Always generate HTML through the bundled script and `assets/dashboard.html`. Reuse this fixed template for every report; replace aggregate data and language only. Do not redesign the page, generate ad hoc HTML, or change layout, colors or interactions unless the user requests a design change. Responsive layout still adapts to viewport size.

Compact token values, including the 每日明细 (Daily details) table, use 亿 at 100,000,000, 千万 at 10,000,000, and 百万 at 1,000,000, with up to two decimal places. Below one million, show the full number with grouping separators; do not use B, M or K. Table tooltips and CSV keep exact token counts. Event and session counts remain full numbers.

It includes total/net usage, cache hit rate, session count, daily average, daily stacked bars with total/net modes and keyboard-accessible day selection, token composition, peak day/week, a sortable daily table, and CSV export. Dates use the selected reporting timezone. Zero-usage days count toward the average and remain in every output. JSON retains its existing fields and adds `timezone` and `generated_at`; `daily` now contains every date in the range.

Chart components are **non-cached input + cached input + output**. Cached input is part of input, and reasoning is part of output; never stack either subset on top of its parent. If source totals differ from the component sum, the dashboard states the difference. Do not call token events tool calls, or invent model/project rankings, active time or success rates from the existing parser. This is a generated snapshot, not a live monitor.

Generated reports contain usage aggregates only, without prompts, session IDs or source paths. They remain local unless the user asks to share them. Preserve `assets/dashboard.html` alongside `scripts/` when installing the skill.
