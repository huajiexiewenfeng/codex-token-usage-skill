# Codex Token Usage Skill

**English** | [中文](README.zh-CN.md)

**See your Codex token usage, from the total down to every day.**

Analyze local Codex Desktop / CLI session logs, generate an offline HTML dashboard, and open it in your system's default external browser. After installation, just ask Codex: “Summarize this week's usage.”

## Dashboard preview

Track total and net tokens, cache hit rate, sessions and daily averages. Switch the daily chart between total and net usage, and explore mutually exclusive token categories.

![Codex usage dashboard with summary cards, daily trends and token breakdown](docs/images/usage-dashboard.png)

Sort daily details by date or total usage, hover for exact counts, and export a CSV for further analysis.

![Daily details with peak day, cache reuse, busiest week and daily token counts](docs/images/daily-details.png)

*Screenshots show a local report snapshot with the Chinese interface. Your results depend on your logs, date range and timezone; English labels are available with `--language en`.*

## Install and use

Install into your Codex environment with Skills CLI:

```bash
npx skills add https://github.com/huajiexiewenfeng/codex-token-usage-skill --skill codex-token-usage
```

Then ask Codex in plain language:

```text
Summarize my Codex token usage for this week.
```

```text
Show my last 30 days of usage, including daily counts and cache hit rate.
```

```text
Generate an HTML dashboard of my usage for August 2026.
```

The skill resolves the dates, runs the report script, generates the fixed HTML template and requests an external browser to open it.

| Section | Contents |
| --- | --- |
| Overview | Total tokens, net tokens, cache hit rate, active sessions and daily average |
| Daily trend | Stacked bars, reported-total line, total/net switch and keyboard-accessible day selection |
| Token breakdown | Uncached input, cached input, output and any difference from the reported total |
| Highlights | Peak day, cache reuse and busiest week |
| Daily details | All dates including inactive days, sorting, exact-value tooltips and CSV export |

Compact token values use **亿 (100 million), 千万 (10 million) and 百万 (1 million)** in both interface languages. Values below one million are shown in full. Daily tables use the same units; tooltips and CSV retain exact counts.

## Run the script directly

Requires Python 3.9+. IANA timezones require a system timezone database or the `tzdata` package. Run these examples from the repository root.

Generate and open a dashboard for the last 30 calendar days:

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --timezone Asia/Shanghai --language en
```

The default output is `output/token-usage-<start>-<end>.html` under the working directory.

| Option | Purpose | Example |
| --- | --- | --- |
| `--days` | Last N calendar days ending today or on `--end` | `--days 7` |
| `--month` | Calendar month, clipped to today for the current month | `--month 2026-08` |
| `--start` / `--end` | Inclusive date range | `--start 2026-09-01 --end 2026-09-08` |
| `--timezone` | Reporting timezone | `--timezone Asia/Shanghai` |
| `--codex-home` | Log directory; defaults to `CODEX_HOME`, then `~/.codex` | `--codex-home ~/.codex` |
| `--output` | Output file, supported by all formats | `--output output/usage.html` |
| `--no-open` | Generate HTML without launching a browser | `--no-open` |
| `--format` | HTML (default), Markdown or JSON | `--format json` |
| `--language` | Chinese (default) or English labels | `--language en` |

“This week” means Monday through today. When using the script directly, pass those dates with `--start` and `--end`; `--days 7` is a rolling seven-day window.

Generate a file for automation:

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --no-open --output output/usage.html
```

Use text or machine-readable output:

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --format markdown
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --format json
```

Markdown and JSON print to stdout by default and do not open a browser. **Scripts that relied on the old default Markdown output must add `--format markdown` when upgrading.** If an existing Codex task retains old instructions, ask it to reread the installed codex-token-usage skill.

## How usage is counted

The script reads JSONL files in `sessions/` and `archived_sessions/`, deduplicates events by session, timestamp and selected usage fields, and sums `last_token_usage` from `token_count` events. It does not sum the cumulative `total_token_usage` on every event.

| Metric | Calculation |
| --- | --- |
| Total | Sum of `last_token_usage.total_tokens` |
| Input / cached input | Sum of `input_tokens` / `cached_input_tokens` |
| Output / reasoning output | Sum of `output_tokens` / `reasoning_output_tokens` |
| Uncached input | `Input − cached input` |
| Net usage | `Uncached input + output` |
| Cache hit rate | `Cached input ÷ input` |
| Daily average | `Total ÷ selected calendar days`, including inactive dates |

Cache is part of input, and reasoning is part of output; neither is stacked twice. Reported totals may differ from input plus output, and the dashboard states the difference. Weeks start on Monday and count only events in the selected range. Token event counts are not tool call counts.

These are statistics from locally readable logs, not account billing or live quota data. The report does not infer success rates, active duration or model/project rankings. JSON includes summary, daily and weekly rows, peaks, timezone and generation time.

## Local and offline

The report process does not upload logs, credentials or usage reports. HTML embeds aggregate data only, without prompts, session IDs or source log paths.

Every report uses the same template with embedded CSS, JavaScript and data. No server, build step or CDN is required; JavaScript must be enabled in the browser. Reports are snapshots and update when regenerated. If browser launch fails, the saved file can still be opened manually.

## Development checks

```bash
python -B skills/codex-token-usage/scripts/test_codex_token_usage.py
npx skills add . --list
```

Tests cover daily/summary consistency, inactive dates, timezones, archive deduplication, HTML export, default browser dispatch and `--no-open`. Browser launches are mocked in tests.

## License

[MIT](LICENSE)
