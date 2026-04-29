#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path


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
        *args,
    ]
    return subprocess.run(command, text=True, capture_output=True, check=True)


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


if __name__ == "__main__":
    test_json_output()
    test_markdown_output_mentions_new_metrics()
    print("tests passed")
