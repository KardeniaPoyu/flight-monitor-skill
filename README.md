<div align="center">

# ✈️ 机票.skill

### *"Cheap flights don't knock — they flash and vanish."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()
[![Stars](https://img.shields.io/github/stars/KardeniaPoyu/flight-monitor-skill?style=social)](https://github.com/KardeniaPoyu/flight-monitor-skill/stargazers)

<br>

<table>
<tr><td align="left">

✈️ &nbsp;考完才发现机票贵了两千？<br>
📉 &nbsp;盯着价格犹豫，回头最低价已过去？<br>
🎯 &nbsp;多条航线要查，手动刷新根本盯不过来？<br>

</td></tr>
</table>

### ✨ 机票.skill solves all three.

填入考试日程 → 自动推算航班日期 → 定时查询价格 → 达标/降价即时告警

<br>

[⚡ 快速开始](#-快速开始) · [📊 配置](#-配置) · [🚀 使用](#-使用) · [🐧 部署](#-部署) · [📂 文件结构](#-文件结构)

</div>

---

## ✨ 功能

| 功能 | 说明 |
|:----:|------|
| 多航线监控 | 任意数量航线，统一目标价管理 |
| 达标告警 🎯 | 价格低于目标价自动标记 |
| 涨跌追踪 📉📈 | 较上次查询涨跌 ≥5% / ≥10% |
| 历史最低 🌟 | 创 30 天内新低自动标记 |
| 定时运行 ⏰ | crontab / Task Scheduler 自动化 |
| 全平台 | Windows / Linux / macOS 同一脚本 |
| 零依赖 | 纯 Python，内置 YAML 解析，无需 PyYAML |

---

## ⚡ 快速开始

> 把下面这行丢给你的 Agent，它会帮你搞定一切：

```text
帮我安装机票监控 skill: https://github.com/KardeniaPoyu/flight-monitor-skill
```

<details>
<summary><b>🛠️ 手动安装</b></summary>

<br>

```bash
# 1. 安装航班查询依赖
skillhub_install install_skill flights

# 2. 克隆本仓库
git clone https://github.com/KardeniaPoyu/flight-monitor-skill

# 3. 编辑 config.yaml，填入你的日程和航线

# 4. 运行
python flight_check_cron.py
```

**依赖：** Python 3.11+ · uv (package runner) · fast-flights (通过 `uvx` 自动下载)

</details>

---

## 📊 配置

编辑 `config.yaml`，所有配置项均可自定义：

```yaml
exam_schedule:
  Your University:
    笔试: "2026-08-01"
    面试: "2026-08-03"

target_price: 1000       # 目标价格 (CNY)
exchange_rate: 7.2       # USD → CNY

routes:
  - {id: 1, from: SHA, to: KIX, auto_date: "Your University.笔试 - 1", label: "出发→大阪"}
  - {id: 2, from: KIX, to: SHA, auto_date: "Your University.面试",     label: "大阪→出发"}
```

### auto_date 语法

从考试日程**自动推算航班日期**，告别手动算天数：

```
学校名.考试类型 [+/- 天数]
```

| 表达式 | 含义 |
|--------|------|
| `"Your University.笔试 - 1"` | 笔试前一天出发 |
| `"Your University.面试 + 1"` | 面试后一天返程 |
| `"Your University.笔试"` | 笔试当天 |

### 航线参数

| 参数 | 必填 | 说明 |
|------|:----:|------|
| `id` | ✅ | 唯一标识 |
| `from` / `to` | ✅ | IATA 机场代码 |
| `auto_date` | ✅* | 自动日期表达式（与 `date` 二选一） |
| `date` | ✅* | 手动指定 `YYYY-MM-DD` |
| `label` | — | 显示名称 |
| `target` | — | 航线专属目标价（覆盖全局） |
| `min_departure_hour` | — | 最早起飞小时（0–23） |

### 机场代码参考

| 代码 | 机场 | 地区 |
|:---:|:---|:---:|
| SHA / PVG | 上海虹桥 / 浦东 | 🇨🇳 |
| PEK / PKX | 北京首都 / 大兴 | 🇨🇳 |
| CAN / SZX | 广州 / 深圳 | 🇨🇳 |
| KIX / ITM | 大阪关西 / 伊丹 | 🇯🇵 |
| HND / NRT | 东京羽田 / 成田 | 🇯🇵 |
| FUK / CTS | 福冈 / 札幌 | 🇯🇵 |

---

## 🚀 使用

```bash
# 检查依赖
python flight_check_cron.py --check

# 运行监控
python flight_check_cron.py

# 指定配置文件
python flight_check_cron.py --config ~/my-config.yaml
```

### 输出示例

```
✈️ 机票监控 · 时刻表
=============================================

📅 考试日程
  🏫 Your University: 笔试 8/1 (77天后) | 面试 8/3 (79天后)

=============================================
📊 价格快照 (05/16 10:31)
=============================================

1. 📍 出发→大阪
   📅 2026-07-31 (76天后)
   ✈️ Peach Aviation | 6:15 AM→9:35 AM | 2 hr 20 min
   💰 ¥1224 ($170)
   🎯 距目标价 ¥1000 还差 ¥224
   🔔 🌟历史最低

=============================================
🔔 告警汇总:
  🌟历史最低 → 出发→大阪
```

---

## 🐧 部署

### Linux / macOS — crontab

```bash
chmod +x flight_monitor.sh
crontab -e
# 每天 9:00 和 21:00 执行
0 9,21 * * * /path/to/flight-monitor-skill/flight_monitor.sh >> /tmp/flight.log 2>&1
```

### Linux — systemd timer

<details>
<summary>点击展开</summary>

```ini
# /etc/systemd/system/flight-monitor.timer
[Unit]
Description=Flight Price Monitor

[Timer]
OnCalendar=*-*-* 09:00:00
OnCalendar=*-*-* 21:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl enable --now flight-monitor.timer
```

</details>

### Windows — Task Scheduler

<details>
<summary>点击展开</summary>

1. 打开「任务计划程序」
2. 创建基本任务 → 每天 9:00 和 21:00
3. 操作 → 启动程序
4. 程序：`python` → 参数：`flight_check_cron.py` → 起始于：`C:\path\to\flight-monitor-skill\`

</details>

---

## 🌐 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FLIGHT_MONITOR_CONFIG` | 配置文件路径 | `./config.yaml` |
| `FLIGHT_MONITOR_DATA_DIR` | 价格历史目录 | `./data/` |
| `FLIGHTS_SEARCH_PATH` | CLI 路径 | 自动查找 |

---

## 📂 文件结构

```
flight-monitor-skill/
├── flight_check_cron.py    # 主脚本 (跨平台)
├── flight_monitor.sh       # Linux crontab 封装
├── config.yaml             # 配置文件模板
├── SKILL.md               # Skill 元数据
├── README.md              # 本文档
├── LICENSE                # MIT License
├── .gitignore             # Git 忽略规则
└── data/                   # 价格历史 (运行时生成)
    └── flight_prices.json
```

---

## ❓ FAQ

| 问题 | 方案 |
|------|------|
| `❌ 未找到 flights-search CLI` | `skillhub_install install_skill flights` |
| `uvx: command not found` | `pip install uv` |
| Windows 中文乱码 | 确保 config.yaml 为 UTF-8 编码 |

---

<div align="center">

**MIT License** © [KardeniaPoyu](https://github.com/KardeniaPoyu)

<sub>Made with ✈️ for everyone who's tired of refreshing flight prices.</sub>

</div>
