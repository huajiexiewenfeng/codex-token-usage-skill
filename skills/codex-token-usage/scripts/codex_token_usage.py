#!/usr/bin/env python3
import argparse
import calendar
import json
import os
import pathlib
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


LABELS = {
    "en": {
        "range": "Range",
        "calls": "Calls",
        "sessions": "Sessions",
        "metric": "Metric",
        "tokens": "Tokens",
        "notes": "Notes",
        "total": "Total",
        "total_note": "Sum of `total_tokens`",
        "input_note": "Input tokens, including cached input",
        "cached_note": "Cached input tokens",
        "output_note": "Output tokens",
        "reasoning_note": "Reasoning output tokens",
        "non_cached": "Non-cached input",
        "non_cached_note": "`Input - Cached input`",
        "net": "Net usage",
        "net_note": "`Non-cached input + Output`",
        "cache_rate": "Cache hit rate",
        "cache_rate_note": "`Cached input / Input`",
        "daily_average": "Daily average total",
        "daily_average_note": "`Total / days in range`",
        "peak_day": "Peak day",
        "peak_week": "Busiest week",
        "period": "Period",
    },
    "zh": {
        "range": "\u8303\u56f4",
        "calls": "\u8c03\u7528\u6b21\u6570",
        "sessions": "\u4f1a\u8bdd\u6570",
        "metric": "\u6307\u6807",
        "tokens": "Token \u6570",
        "notes": "\u8bf4\u660e",
        "total": "\u603b\u91cf",
        "total_note": "`total_tokens` \u6c47\u603b",
        "input_note": "\u8f93\u5165 token\uff0c\u5305\u542b cached input",
        "cached_note": "\u547d\u4e2d\u7f13\u5b58\u7684\u8f93\u5165 token",
        "output_note": "\u8f93\u51fa token",
        "reasoning_note": "\u63a8\u7406\u8f93\u51fa token",
        "non_cached": "\u975e\u7f13\u5b58 Input",
        "non_cached_note": "`Input - Cached input`",
        "net": "\u51c0\u7528\u91cf",
        "net_note": "`\u975e\u7f13\u5b58 Input + Output`",
        "cache_rate": "\u7f13\u5b58\u547d\u4e2d\u7387",
        "cache_rate_note": "`Cached input / Input`",
        "daily_average": "\u65e5\u5747\u603b\u91cf",
        "daily_average_note": "`\u603b\u91cf / \u7edf\u8ba1\u5929\u6570`",
        "peak_day": "\u6700\u591a\u7684\u4e00\u5929",
        "peak_week": "\u6700\u591a\u7684\u4e00\u5468",
        "period": "\u5468\u671f",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize Codex token usage from local session JSONL logs.")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME") or str(pathlib.Path.home() / ".codex"))
    parser.add_argument("--timezone", default=None, help="IANA timezone, for example Asia/Shanghai.")
    parser.add_argument("--days", type=int, default=None, help="Rolling local calendar days ending on --end or today.")
    parser.add_argument("--start", default=None, help="Inclusive start date, YYYY-MM-DD.")
    parser.add_argument("--end", default=None, help="Inclusive end date, YYYY-MM-DD.")
    parser.add_argument("--month", default=None, help="Calendar month, YYYY-MM.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--language", choices=["zh", "en"], default="zh")
    return parser.parse_args()


def local_today(tz):
    return datetime.now(tz).date()


def resolve_range(args, tz):
    if args.month:
        year, month = [int(part) for part in args.month.split("-", 1)]
        start = date(year, month, 1)
        end = date(year, month, calendar.monthrange(year, month)[1])
        today = local_today(tz)
        if start <= today <= end:
            end = today
        return start, end

    end = date.fromisoformat(args.end) if args.end else local_today(tz)
    if args.start:
        start = date.fromisoformat(args.start)
    else:
        days = args.days or 30
        start = end - timedelta(days=days - 1)
    return start, end


def session_id(path):
    match = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", path.name)
    return match.group(1) if match else path.stem


def iter_token_events(codex_home, tz):
    roots = [codex_home / "sessions", codex_home / "archived_sessions"]
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.jsonl"):
            sid = session_id(path)
            try:
                handle = path.open("r", encoding="utf-8", errors="replace")
            except OSError:
                continue
            with handle:
                for line in handle:
                    if '"token_count"' not in line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    payload = obj.get("payload") or {}
                    if payload.get("type") != "token_count":
                        continue
                    usage = ((payload.get("info") or {}).get("last_token_usage") or {})
                    timestamp = obj.get("timestamp")
                    if not timestamp or not usage:
                        continue
                    key = (
                        sid,
                        timestamp,
                        usage.get("total_tokens"),
                        usage.get("input_tokens"),
                        usage.get("output_tokens"),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(tz)
                    yield {
                        "session": sid,
                        "date": dt.date(),
                        "input": usage.get("input_tokens") or 0,
                        "cached_input": usage.get("cached_input_tokens") or 0,
                        "output": usage.get("output_tokens") or 0,
                        "reasoning": usage.get("reasoning_output_tokens") or 0,
                        "total": usage.get("total_tokens") or 0,
                    }


def day_count(start, end):
    return max((end - start).days + 1, 1)


def summarize(events, days=None):
    input_tokens = sum(event["input"] for event in events)
    cached_input = sum(event["cached_input"] for event in events)
    output = sum(event["output"] for event in events)
    reasoning = sum(event["reasoning"] for event in events)
    total = sum(event["total"] for event in events)
    non_cached_input = input_tokens - cached_input
    net_usage = non_cached_input + output
    return {
        "calls": len(events),
        "sessions": len({event["session"] for event in events}),
        "total": total,
        "input": input_tokens,
        "cached_input": cached_input,
        "output": output,
        "reasoning": reasoning,
        "non_cached_input": non_cached_input,
        "net_usage": net_usage,
        "cache_hit_rate": (cached_input / input_tokens) if input_tokens else 0,
        "daily_average_total": (total / days) if days else None,
    }


def week_start(day):
    return day - timedelta(days=day.weekday())


def grouped(events, key_func):
    buckets = {}
    for event in events:
        key = key_func(event)
        buckets.setdefault(key, []).append(event)
    return buckets


def weekly(events):
    rows = []
    for start, bucket in sorted(grouped(events, lambda event: week_start(event["date"])).items()):
        rows.append({"start": start, "end": start + timedelta(days=6), "summary": summarize(bucket)})
    return rows


def daily(events):
    rows = []
    for day, bucket in sorted(grouped(events, lambda event: event["date"]).items()):
        rows.append({"date": day, "summary": summarize(bucket)})
    return rows


def fmt(value):
    if isinstance(value, float):
        if value.is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}"
    return f"{value:,}"


def fmt_percent(value):
    return f"{value * 100:.2f}%"


def json_ready(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    return value


def build_report(start, end, events):
    days = day_count(start, end)
    summary = summarize(events, days=days)
    weeks = weekly(events)
    days_rows = daily(events)
    peak_week = max(weeks, key=lambda row: row["summary"]["total"], default=None)
    peak_day = max(days_rows, key=lambda row: row["summary"]["total"], default=None)
    return {
        "start": start,
        "end": end,
        "days": days,
        "summary": summary,
        "peak_week": peak_week,
        "peak_day": peak_day,
        "weeks": weeks,
        "daily": days_rows,
    }


def print_json(report):
    print(json.dumps(json_ready(report), ensure_ascii=False, indent=2))


def print_markdown(report, language):
    labels = LABELS[language]
    summary = report["summary"]
    print(f"{labels['range']}: {report['start']} to {report['end']}")
    print(f"{labels['calls']}: {summary['calls']:,}")
    print(f"{labels['sessions']}: {summary['sessions']:,}")
    print()
    print(f"| {labels['metric']} | {labels['tokens']} | {labels['notes']} |")
    print("|---|---:|---|")
    print(f"| {labels['total']} | {fmt(summary['total'])} | {labels['total_note']} |")
    print(f"| Input | {fmt(summary['input'])} | {labels['input_note']} |")
    print(f"| Cached input | {fmt(summary['cached_input'])} | {labels['cached_note']} |")
    print(f"| Output | {fmt(summary['output'])} | {labels['output_note']} |")
    print(f"| Reasoning output | {fmt(summary['reasoning'])} | {labels['reasoning_note']} |")
    print(f"| {labels['non_cached']} | {fmt(summary['non_cached_input'])} | {labels['non_cached_note']} |")
    print(f"| {labels['net']} | {fmt(summary['net_usage'])} | {labels['net_note']} |")
    print(f"| {labels['cache_rate']} | {fmt_percent(summary['cache_hit_rate'])} | {labels['cache_rate_note']} |")
    print(f"| {labels['daily_average']} | {fmt(summary['daily_average_total'])} | {labels['daily_average_note']} |")
    print()
    if report["peak_day"]:
        peak = report["peak_day"]
        print(f"{labels['peak_day']}: {peak['date']}, {fmt(peak['summary']['total'])} tokens.")
    if report["peak_week"]:
        peak = report["peak_week"]
        print(f"{labels['peak_week']}: {peak['start']} to {peak['end']}, {fmt(peak['summary']['total'])} tokens.")
        print()
        print(f"| {labels['period']} | {labels['total']} | {labels['calls']} | {labels['sessions']} |")
        print("|---|---:|---:|---:|")
        for row in report["weeks"]:
            row_summary = row["summary"]
            print(
                f"| {row['start']} to {row['end']} | {fmt(row_summary['total'])} | "
                f"{row_summary['calls']:,} | {row_summary['sessions']:,} |"
            )


def main():
    args = parse_args()
    tz = ZoneInfo(args.timezone) if args.timezone else datetime.now().astimezone().tzinfo
    codex_home = pathlib.Path(args.codex_home).expanduser()
    start, end = resolve_range(args, tz)
    events = [event for event in iter_token_events(codex_home, tz) if start <= event["date"] <= end]
    report = build_report(start, end, events)
    if args.format == "json":
        print_json(report)
    else:
        print_markdown(report, args.language)


if __name__ == "__main__":
    main()
