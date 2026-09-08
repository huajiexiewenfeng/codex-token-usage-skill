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

## 每日用量与 HTML 看板

现在默认生成固定模板的 HTML 看板，并请求系统默认外部浏览器打开；“统计本周用量”等普通请求也使用此行为。默认文件位于当前工作目录的 `output/token-usage-<开始日期>-<结束日期>.html`。每日明细包含零用量日期，Token 显示使用亿、千万、百万，不足百万显示完整数字。

生成深色分析面板：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --timezone Asia/Shanghai --format html --output output/token-usage.html
```

直接用浏览器打开文件即可，无需服务端、构建工具或网络连接；浏览器需启用 JavaScript。支持总量/净用量切换、点击或键盘选择每日柱子、Token 构成环图、峰值日/周、按日期或总量排序的每日明细、CSV 导出。使用 `--language en` 切换英文；所有格式都支持 `--output` 写入 UTF-8 文件。

自动化或仅生成文件时加 `--no-open`。需要旧的文字输出时显式使用 `--format markdown`；JSON 使用 `--format json`。这两种格式不会打开浏览器。浏览器启动失败时仍保留报告文件并提示路径。升级前依赖默认 stdout Markdown 的脚本需补上 `--format markdown`。

也可以直接对 Codex 说：“生成我最近 30 天的 Token 用量 HTML 看板，展示总数和每天明细。”

图表拆分为非缓存输入、缓存输入和输出，避免重复计算。现有日志解析器不提供成功率、工具调用或工作时长，因此页面不展示推测数值。报告是生成时的快照，含统计时区和生成时间；只嵌入汇总数据，不包含提示词、会话 ID 或日志路径。

JSON 保留原有字段，新增 `timezone`、`generated_at`；`daily` 现在覆盖范围内每个自然日，无用量日期为零。周统计按周一分组，只计入所选范围内的事件。

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
