#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import re
from datetime import date
from pathlib import Path
from unittest.mock import patch
from codex_token_usage import build_report, render_html


SCRIPT = Path(__file__).with_name("codex_token_usage.py")


def write_session(codex_home):
    session_dir = codex_home / "sessions" / "2026" / "04" / "29"
    session_dir.mkdir(parents=True)
    path = session_dir / "rollout-2026-04-29T10-00-00-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee.jsonl"
    events = [
        ("2026-04-28T01:00:00.000Z", 100, 40, 30, 5, 130),
        ("2026-04-28T02:00:00.000Z", 200, 50, 80, 10, 280),
        ("2026-04-29T01:00:00.000Z", 50, 10, 20, 2, 70),
    ]
    with path.open("w", encoding="utf-8") as handle:
        for timestamp, input_tokens, cached, output, reasoning, total in events:
            payload = {
                "timestamp": timestamp,
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "last_token_usage": {
                            "input_tokens": input_tokens,
                            "cached_input_tokens": cached,
                            "output_tokens": output,
                            "reasoning_output_tokens": reasoning,
                            "total_tokens": total,
                        }
                    },
                },
            }
            handle.write(json.dumps(payload) + "\n")


def run_script(codex_home, *args):
    command = [
        sys.executable,
        "-B",
        str(SCRIPT),
        "--codex-home",
        str(codex_home),
        "--timezone",
        "Asia/Shanghai",
        "--language",
        "en",
        "--no-open",
        *args,
    ]
    return subprocess.run(command, text=True, encoding="utf-8", capture_output=True, check=True,
                          env={**__import__('os').environ, "PYTHONIOENCODING": "utf-8"})


def test_json_output():
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
        codex_home = Path(temp)
        write_session(codex_home)
        result = run_script(codex_home, "--start", "2026-04-28", "--end", "2026-04-29", "--format", "json")
        data = json.loads(result.stdout)

    assert data["summary"]["total"] == 480
    assert data["summary"]["input"] == 350
    assert data["summary"]["cached_input"] == 100
    assert data["summary"]["output"] == 130
    assert data["summary"]["non_cached_input"] == 250
    assert data["summary"]["net_usage"] == 380
    assert data["summary"]["cache_hit_rate"] == 100 / 350
    assert data["summary"]["daily_average_total"] == 240
    assert data["peak_day"]["date"] == "2026-04-28"
    assert data["peak_day"]["summary"]["total"] == 410


def test_markdown_output_mentions_new_metrics():
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
        codex_home = Path(temp)
        write_session(codex_home)
        result = run_script(codex_home, "--start", "2026-04-28", "--end", "2026-04-29", "--format", "markdown")

    assert "| Cache hit rate | 28.57% |" in result.stdout
    assert "| Daily average total | 240 |" in result.stdout
    assert "Peak day: 2026-04-28, 410 tokens." in result.stdout
    assert "### Daily usage" in result.stdout
    assert "| 2026-04-28 | 410 | 300 | 90 | 110 | 320 |" in result.stdout


def test_zero_days_and_empty_range():
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
        home = Path(temp)
        write_session(home)
        data = json.loads(run_script(home, "--start", "2026-04-27", "--end", "2026-04-30", "--format", "json").stdout)
        assert [r['date'] for r in data['daily']] == ['2026-04-27', '2026-04-28', '2026-04-29', '2026-04-30']
        assert [r['summary']['total'] for r in data['daily']] == [0, 410, 70, 0]
        assert data['summary']['daily_average_total'] == 120
        for key in ['total', 'input', 'cached_input', 'output', 'reasoning', 'net_usage', 'calls']:
            assert sum(r['summary'][key] for r in data['daily']) == data['summary'][key]
        empty = json.loads(run_script(home, '--days', '2', '--end', '2026-01-02', '--format', 'json').stdout)
        assert len(empty['daily']) == 2
        assert empty['peak_day'] is None and empty['peak_week'] is None
        assert empty['summary']['cache_hit_rate'] == 0


def test_html_and_output_file():
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
        home = Path(temp)
        write_session(home)
        target = home / 'report' / '用量.html'
        run_script(home, '--start', '2026-04-28', '--end', '2026-04-29', '--format', 'html', '--output', str(target), '--language', 'zh')
        html = target.read_text(encoding='utf-8')
        assert html.startswith('<!doctype html>') and '<html lang="zh">' in html
        assert '__REPORT_JSON__' not in html and '__LANGUAGE__' not in html
        embedded = json.loads(re.search(r'<script id="report-data" type="application/json">(.*?)</script>', html, re.S).group(1))
        assert embedded['summary']['total'] == 480
        assert embedded['timezone'] == 'Asia/Shanghai'
        assert str(home) not in html
        assert not re.search(r'<(?:script|link)[^>]+(?:src|href)\s*=', html)
        for output_format in ['json', 'markdown']:
            output = home / ('output.' + output_format)
            run_script(home, '--days', '2', '--end', '2026-04-29', '--format', output_format, '--output', str(output))
            assert output.read_text(encoding='utf-8')


def test_embedded_data_cannot_close_script():
    report = build_report(date(2026, 1, 1), date(2026, 1, 1), [])
    report['timezone'] = '</script><script>alert("x")</script>&'
    html = render_html(report)
    assert report['timezone'] not in html
    embedded = re.search(r'<script id="report-data" type="application/json">(.*?)</script>', html, re.S).group(1)
    assert json.loads(embedded)['timezone'] == report['timezone']


def test_timezone_and_archive_deduplication():
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
        home = Path(temp)
        write_session(home)
        path = next((home / 'sessions').rglob('*.jsonl'))
        text = path.read_text(encoding='utf-8').replace('2026-04-28T01:00:00.000Z', '2026-04-27T16:00:00.000Z')
        path.write_text(text, encoding='utf-8')
        archived = home / 'archived_sessions'
        archived.mkdir()
        (archived / path.name).write_text(text, encoding='utf-8')
        data = json.loads(run_script(home, '--start', '2026-04-28', '--end', '2026-04-29', '--format', 'json').stdout)
        assert data['summary']['total'] == 480 and data['summary']['calls'] == 3
        assert data['daily'][0]['summary']['total'] == 410


def test_invalid_range():
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
        for args in [('--days', '0'), ('--days', '-1'), ('--start', '2026-05-01', '--end', '2026-04-01')]:
            try:
                run_script(Path(temp), *args)
            except subprocess.CalledProcessError as error:
                assert 'Invalid range' in error.stderr
            else:
                raise AssertionError('Invalid range was accepted')


def test_default_html_and_browser_dispatch():
    import codex_token_usage as usage
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp:
        home = Path(temp)
        write_session(home)
        with patch.object(sys, 'argv', ['codex_token_usage.py']):
            args = usage.parse_args()
            assert args.format == 'html' and args.no_open is False
        args.codex_home = str(home)
        args.timezone = 'Asia/Shanghai'
        args.start, args.end = '2026-04-28', '2026-04-29'
        expected = home / 'output' / 'token-usage-2026-04-28-2026-04-29.html'
        with patch.object(usage, 'parse_args', return_value=args), patch.object(Path, 'cwd', return_value=home), patch.object(usage, 'open_external_report') as browser:
            usage.main()
            assert expected.exists()
            browser.assert_called_once_with(expected)
            browser.reset_mock()
            args.no_open = True
            usage.main()
            browser.assert_not_called()
        with patch.object(usage.sys, 'platform', 'win32'), patch.object(usage.os, 'startfile', create=True) as startfile:
            assert usage.open_external_report(expected)
            startfile.assert_called_once_with(str(expected.resolve()))
        with patch.object(usage.sys, 'platform', 'linux'), patch.object(usage.webbrowser, 'open', return_value=True) as browser:
            assert usage.open_external_report(expected)
            browser.assert_called_once_with(expected.resolve().as_uri(), new=2)
        with patch.object(usage.sys, 'platform', 'linux'), patch.object(usage.webbrowser, 'open', return_value=False):
            assert not usage.open_external_report(expected)
            assert expected.exists()


if __name__ == "__main__":
    test_json_output()
    test_markdown_output_mentions_new_metrics()
    test_zero_days_and_empty_range()
    test_html_and_output_file()
    test_embedded_data_cannot_close_script()
    test_timezone_and_archive_deduplication()
    test_invalid_range()
    test_default_html_and_browser_dispatch()
    print("tests passed")
