# Codex Token Usage Skill

[English](README.md) | [中文](README.zh-CN.md)

Codex Token Usage Skill 用于从本地 Codex Desktop 和 Codex CLI 的 session JSONL 日志中统计 token 用量。它会输出总量、净用量、缓存命中率、日均用量、最多的一天和最多的一周，方便你了解最近的 Codex 使用情况。

## 隐私

这个 skill 只读取本地文件。它不会上传日志、认证信息、SQLite 数据库或用量报告。

## 安装

使用 Skills CLI 安装：

```bash
npx skills add https://github.com/huajiexiewenfeng/codex-token-usage-skill --skill codex-token-usage
```

列出这个仓库中的可用 skills：

```bash
npx skills add https://github.com/huajiexiewenfeng/codex-token-usage-skill --list
```

## Codex 使用示例

安装后，可以直接用自然语言让 Codex 统计用量：

```text
统计我最近 30 天的 Codex token 用量，包含净用量和最多的一天。
```

```text
统计 2026 年 4 月的 Codex token 用量，包含缓存命中率和最多的一周。
```

```text
对比我本月每天的 Codex token 平均用量。
```

## 直接运行脚本

也可以在仓库根目录直接运行脚本：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30
```

统计某个自然月：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --month 2026-04
```

统计指定日期范围：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --start 2026-04-01 --end 2026-04-29
```

输出 JSON，方便自动化处理：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --format json
```

指定 Codex home：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --codex-home ~/.codex
```

## 指标定义

| 指标 | 公式 |
| --- | --- |
| 总量 | `last_token_usage.total_tokens` 汇总 |
| Input | `last_token_usage.input_tokens` 汇总 |
| Cached input | `last_token_usage.cached_input_tokens` 汇总 |
| Output | `last_token_usage.output_tokens` 汇总 |
| Reasoning output | `last_token_usage.reasoning_output_tokens` 汇总 |
| 非缓存 Input | `Input - Cached input` |
| 净用量 | `非缓存 Input + Output` |
| 缓存命中率 | `Cached input / Input` |
| 日均总量 | `总量 / 统计范围天数` |

脚本会聚合 Codex `token_count` 事件中的 `last_token_usage`。

它不会逐条累加 `total_token_usage`，因为这个字段是单个会话内的累计值，直接累加会重复计算。

## 验证

运行测试脚本：

```bash
python -B skills/codex-token-usage/scripts/test_codex_token_usage.py
```

验证 skill 元数据：

```bash
python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/codex-token-usage
```

验证本地 Skills CLI 是否能发现这个 skill：

```bash
npx skills add . --list
```

## 许可证

MIT
