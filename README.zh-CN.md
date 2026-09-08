# Codex Token Usage Skill

[English](README.md) | **中文**

**看清 Codex 的总用量，也看清每一天的投入。**

从本地 Codex Desktop / CLI 会话日志中统计 Token 用量，默认生成可离线使用的 HTML 看板，并请求系统默认外部浏览器打开。安装后，直接说「统计本周用量」即可。

## 看板预览

总量、净用量、缓存命中率、会话数与日均用量集中展示；每日趋势支持切换总量与净用量，Token 构成按互斥分类拆分。

![Codex 用量看板：汇总指标、每日趋势与 Token 构成](docs/images/usage-dashboard.png)

每日明细支持按日期或总量排序，悬停查看精确数值，也可以导出 CSV 继续分析。

![每日明细：峰值日、缓存复用、最忙的一周与每日 Token 表格](docs/images/daily-details.png)

*截图展示一份本地报告快照；实际数值取决于你的日志、日期范围和时区。*

## 安装与使用

使用 Skills CLI 安装到你的 Codex 环境：

```bash
npx skills add https://github.com/huajiexiewenfeng/codex-token-usage-skill --skill codex-token-usage
```

安装后，在 Codex 中直接输入：

```text
统计本周 Codex token 用量。
```

```text
统计最近 30 天的用量，看看每天用了多少、缓存命中率是多少。
```

```text
统计 2026 年 8 月的用量，生成 HTML 看板。
```

Skill 会解析日期范围、运行统计脚本、生成固定模板的 HTML，并请求外部浏览器打开。

| 模块 | 内容 |
| --- | --- |
| 用量总览 | 总量、净用量、缓存命中率、有用量的会话、日均 Token |
| 每日趋势 | 堆叠柱状图、日志总量线、总量/净用量切换、点击或键盘选择日期 |
| Token 构成 | 非缓存输入、缓存输入、输出，以及分类合计与日志总量的差额 |
| 用量摘要 | 峰值日、缓存复用、最忙的一周 |
| 每日明细 | 含零用量日期的完整列表、排序、精确值提示、CSV 导出 |

Token 显示统一使用 **亿、千万、百万**，不足百万显示完整数字。每日明细也遵循这一规则，悬停提示与 CSV 保留原始数值。

## 直接运行脚本

需要 Python 3.9+。使用 IANA 时区时，系统需提供时区数据库；缺失时可安装 `tzdata`。以下命令从仓库根目录运行。

默认统计最近 30 个自然日，生成并打开 HTML：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --timezone Asia/Shanghai
```

默认保存到当前工作目录下的 `output/token-usage-<开始日期>-<结束日期>.html`。

| 参数 | 用途 | 示例 |
| --- | --- | --- |
| `--days` | 截至今天或 `--end` 的最近 N 个自然日 | `--days 7` |
| `--month` | 指定自然月，当月截到今天 | `--month 2026-08` |
| `--start` / `--end` | 指定首尾都包含的日期范围 | `--start 2026-09-01 --end 2026-09-08` |
| `--timezone` | 指定统计时区 | `--timezone Asia/Shanghai` |
| `--codex-home` | 日志目录，默认使用 `CODEX_HOME`，否则 `~/.codex` | `--codex-home ~/.codex` |
| `--output` | 自定义输出文件，所有格式均支持 | `--output output/usage.html` |
| `--no-open` | 仅生成 HTML，不启动浏览器 | `--no-open` |
| `--format` | HTML（默认）、Markdown 或 JSON | `--format json` |
| `--language` | 中文（默认）或英文界面 | `--language en` |

“本周”按周一至今天统计；直接运行脚本时传入对应的 `--start` 和 `--end`，`--days 7` 表示滚动七天。

自动化生成文件：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --no-open --output output/usage.html
```

文字或机器可读输出：

```bash
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --format markdown
python -B skills/codex-token-usage/scripts/codex_token_usage.py --days 30 --format json
```

Markdown / JSON 默认写入标准输出，不打开浏览器。**旧版依赖默认 Markdown 输出的脚本，升级后请补上 `--format markdown`。** 旧任务若仍沿用此前指令，可要求 Codex「重新读取 codex-token-usage Skill」。

## 统计口径

读取 `sessions/` 与 `archived_sessions/` 中的 JSONL 日志，按会话、时间戳及部分用量字段去重后，汇总 `token_count` 事件的 `last_token_usage`。不逐条累加会话累计值 `total_token_usage`。

| 指标 | 计算方式 |
| --- | --- |
| 总量 | `last_token_usage.total_tokens` 之和 |
| 输入 / 缓存输入 | `input_tokens` / `cached_input_tokens` 之和 |
| 输出 / 推理输出 | `output_tokens` / `reasoning_output_tokens` 之和 |
| 非缓存输入 | `输入 − 缓存输入` |
| 净用量 | `非缓存输入 + 输出` |
| 缓存命中率 | `缓存输入 ÷ 输入` |
| 日均总量 | `总量 ÷ 所选自然日数`，包含零用量日期 |

缓存输入包含在输入中，推理输出包含在输出中，图表不重复叠加。日志总量可能与输入加输出不一致，看板会标明差额。周统计按周一分组，仅计入选定范围内的事件；Token 事件数不等于工具调用次数。

这些是本机可读取日志的统计，不是账户账单或实时配额。报告不推断成功率、活跃时长或模型/项目排名。JSON 包含汇总、每日、每周、峰值、时区与生成时间。

## 本地与离线

统计过程不上传日志、认证信息或用量报告。HTML 只嵌入汇总数据，不包含提示词、会话 ID 或源日志路径。

页面使用固定模板，CSS、JavaScript 和数据均内嵌，无需服务端、构建工具或 CDN；浏览器需启用 JavaScript。它是生成时的快照，重新运行才会更新。浏览器启动失败时，仍可从输出路径手动打开文件。

## 开发验证

```bash
python -B skills/codex-token-usage/scripts/test_codex_token_usage.py
npx skills add . --list
```

测试覆盖汇总与每日一致性、零用量日期、时区、归档去重、HTML 导出、默认浏览器启动分发与 `--no-open`。浏览器启动在测试中使用模拟调用。

## 许可证

[MIT](LICENSE)
