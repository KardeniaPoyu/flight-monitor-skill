# ✈️ 机票.skill

[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)](.)
[![Python](https://img.shields.io/badge/python-3.11+-green)](.)
[![License](https://img.shields.io/badge/license-MIT-orange)](.)

> 航班价格监控工具 — 自动检查多条航线价格，达标/降价自动告警，适合考研、旅行等场景

## ✨ 功能

- 📊 多条航线批量监控（不限条数）
- 🎯 自定义目标价，达标即告警
- 📉 价格涨跌追踪（降 ≥5% / 涨 ≥10%）
- ⏰ 配合 cron / crontab 定时运行
- 🗓️ `auto_date` 语法 — 从考试日程自动推算航班日期
- 🔧 零外部依赖 — 纯 Python，内置 YAML 解析器
- 🌍 Windows / Linux / macOS 全平台

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 flights CLI（航班查询底层）
skillhub_install install_skill flights
```

前提：Python 3.11+，[uv](https://docs.astral.sh/uv/) 已安装。

### 2. 配置

编辑 `config.yaml`：

```yaml
exam_schedule:
  你的学校:
    笔试: "2026-08-01"
    面试: "2026-08-03"

target_price: 1000       # 目标价格 (CNY)
exchange_rate: 7.2       # USD→CNY 汇率

routes:
  - {id: 1, from: PVG, to: KIX, auto_date: "你的学校.笔试 - 1", label: "上海→大阪"}
  - {id: 2, from: KIX, to: PVG, auto_date: "你的学校.面试", label: "大阪→上海"}
```

### 3. 运行

```bash
# 基础运行
python flight_check_cron.py

# 检查依赖
python flight_check_cron.py --check

# 指定配置文件
python flight_check_cron.py --config ~/my-config.yaml
```

---

## 📋 auto_date 语法

自动从考试日程推算航班日期，无需手动计算：

```
学校名.考试类型 [+/- 天数]
```

| 表达式 | 含义 |
|--------|------|
| `"阪大.笔试 - 1"` | 笔试前一天出发 |
| `"东大.面试 + 1"` | 面试后一天返程 |
| `"九大.笔试"` | 笔试当天 |

---

## 🐧 Linux 部署

### crontab

```bash
chmod +x flight_monitor.sh
crontab -e
# 每天 9:00 和 21:00 执行
0 9,21 * * * /path/to/flight-monitor-skill/flight_monitor.sh
```

### systemd timer (可选)

```ini
[Timer]
OnCalendar=*-*-* 09:00:00
OnCalendar=*-*-* 21:00:00
```

### AstrBot

CLI 路径已内置，直接运行即可：
```
/root/AstrBot/data/skills/temp-flights-skill/skills/flights
```

---

## 📊 输出示例

```
✈️ 机票监控 · 时刻表
=============================================
📅 考试日程
  🏫 阪大: 笔试 8/1(77天后) | 面试 8/3(79天后)

=============================================
📊 价格快照 (05/16 10:31)
=============================================

1. 📍 上海→大阪
   📅 2026-07-31 (76天后) | 阪大笔试前1天
   ✈️ Peach Aviation | 6:15 AM→9:35 AM | 2 hr 20 min
   💰 ¥1224 ($170)
   🎯 距目标价 ¥1000 还差 ¥224
   🔔 🌟历史最低

2. 📍 大阪→上海
   📅 2026-08-03 (79天后) | 阪大面试当天
   ✈️ Peach Aviation | 10:25 PM→12:05 AM | 2 hr 40 min
   💰 ¥1922 ($267)
   🎯 距目标价 ¥1000 还差 ¥922
   🔔 🌟历史最低

=============================================
🔔 告警汇总:
  🎯达目标价 ¥1000 → 东京→福冈
  🎯达目标价 ¥1000 → 福冈→东京
  📉降价 9% → 上海→东京
  🌟历史最低 → 上海→大阪
```

---

## 🔧 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FLIGHT_MONITOR_CONFIG` | 配置文件路径 | `./config.yaml` |
| `FLIGHT_MONITOR_DATA_DIR` | 价格历史存储目录 | `./data/` |
| `FLIGHTS_SEARCH_PATH` | flights-search CLI 路径 | 自动查找 |
| `PYTHON` | Python 解释器 (仅 flight_monitor.sh) | `python3` |

---

## 📁 文件结构

```
机票.skill/
├── flight_check_cron.py    # 主脚本 (跨平台)
├── flight_monitor.sh       # Linux crontab 封装
├── config.yaml             # 配置文件
├── SKILL.md                # Skill 元数据
└── README.md               # 本文件
```

---

## 📄 License

MIT