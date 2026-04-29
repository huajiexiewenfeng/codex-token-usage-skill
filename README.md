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
