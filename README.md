# Codex Token Usage Skill

[English](README.md) | [中文](README.zh-CN.md)

Codex Token Usage Skill summarizes local Codex Desktop and Codex CLI token usage from session JSONL logs. It reports total usage, net usage, cache hit rate, daily averages, peak day, and busiest week so you can understand recent Codex usage across local sessions.

## Privacy

This skill reads local files only. It does not upload logs, auth data, SQLite databases, or usage reports.

## Install

Install the skill with Skills CLI:

```bash
npx skills add https://github.com/huajiexiewenfeng/codex-token-usage-skill --skill codex-token-usage
```

List available skills from the repository:

```bash
npx skills add https://github.com/huajiexiewenfeng/codex-token-usage-skill --list
```

## Codex Usage Examples

After installation, ask Codex for usage summaries in plain language:

```text
Summarize my Codex token usage for the last 30 days, including net usage and peak day.
```

```text
Show my Codex token usage for April 2026 with cache hit rate and busiest week.
```

```text
Compare my daily average Codex token usage this month.
```

## Direct Script Examples

Run the bundled report script directly from the repository root:

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30
```

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --month 2026-04
```

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --start 2026-04-01 --end 2026-04-29
```

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --format json
```

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --codex-home ~/.codex
```

## Daily Usage and HTML Dashboard

The default now generates the fixed HTML dashboard and asks the system's default external browser to open it, including for plain requests such as “summarize this week's usage.” The default file is `output/token-usage-<start>-<end>.html` under the working directory. Daily rows include zero-usage dates. Token displays use 亿, 千万 and 百万, with full numbers below one million.

Generate a self-contained dark analytics dashboard:

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --timezone Asia/Shanghai --format html --language en --output output/token-usage.html
```

Open the file in a browser with JavaScript enabled. No build, server, CDN or network connection is required. The dashboard includes total/net usage, daily stacked bars with keyboard-accessible day selection, token composition, peak day/week, a sortable daily table and CSV export. All formats support `--output` for UTF-8 files; use `--language zh` for Chinese.

Use `--no-open` for automation or file-only generation. For text output, explicitly pass `--format markdown`; for JSON, pass `--format json`. Neither opens a browser. A failed browser launch preserves the report and prints its path. Existing scripts that depended on default Markdown stdout must add `--format markdown` when upgrading.

You can also ask Codex: “Generate an HTML dashboard of my last 30 days of token usage, including totals and daily details.”

Charts stack uncached input, cached input and output without double-counting. The current parser does not supply success rates, tool calls or active duration, so these are not inferred. Reports are snapshots with timezone and generation time. Only aggregate data is embedded, without prompts, session IDs or source paths.

JSON retains existing fields and adds `timezone` and `generated_at`. Its `daily` array now includes all calendar dates in the range, with zeros for inactive dates. Weeks start on Monday and count only events inside the requested range.

## Metric Definitions

| Metric | Formula |
| --- | --- |
| Total | Sum of `last_token_usage.total_tokens` |
| Input | Sum of `last_token_usage.input_tokens` |
| Cached input | Sum of `last_token_usage.cached_input_tokens` |
| Output | Sum of `last_token_usage.output_tokens` |
| Reasoning output | Sum of `last_token_usage.reasoning_output_tokens` |
| Non-cached input | `Input - Cached input` |
| Net usage | `Non-cached input + Output` |
| Cache hit rate | `Cached input / Input` |
| Daily average total | `Total / days in range` |

## Verify

Run the test script:

```bash
python -B skills/codex-token-usage/scripts/test_codex_token_usage.py
```

Run quick validation:

```bash
python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/codex-token-usage
```

Verify local Skills CLI metadata:

```bash
npx skills add . --list
```

## License

MIT
