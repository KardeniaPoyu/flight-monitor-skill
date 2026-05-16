---
name: 机票.skill
description: |
  航班价格监控。自动查询多条航线价格，达标/降价告警，配合 cron 定时运行。
  触发词：「查机票」「机票监控」「航班价格」「机票降价」「机票提醒」「flight monitor」「机票降价提醒」。
  支持 Windows / Linux / macOS 全平台。
lifecycle: recurring
deactivate_on:
  - user-explicit-exit: true
---

# ✈️ 机票.skill

> 航班价格监控，自动检查多条航线，达标/降价即时告警

---

## 🎯 核心功能

| 功能 | 说明 |
|------|------|
| 多航线监控 | 自定义任意数量航线，统一目标价管理 |
| 达标告警 | 价格低于目标价时自动标记 🎯 |
| 涨跌追踪 | 较上次查询涨跌 ≥5% / ≥10% 时标记 📉📈 |
| 历史最低 | 价格创30天内新低时标记 🌟 |
| 定时运行 | 配合 crontab / Windows Task Scheduler 自动化 |
| 全平台 | Windows / Linux / macOS 同一脚本 |

---

## ⚡ 快速开始

```bash
# 1. 安装依赖
skillhub_install install_skill flights

# 2. 编辑 config.yaml，填入考试日程和航线

# 3. 运行
python flight_check_cron.py

# 4. 检查依赖是否就绪
python flight_check_cron.py --check
```

**依赖：**
- ✅ Python 3.11+
- ✅ uv (package runner)
- ✅ fast-flights (通过 `uvx` 自动下载，无需手动安装)

---

## 📋 config.yaml 配置

```yaml
exam_schedule:
  阪大:
    笔试: "2026-08-01"
    面试: "2026-08-03"
  东科大:
    笔试: "2026-08-18"
    面试: "2026-08-24"

target_price: 1000       # 目标价格 (CNY)
exchange_rate: 7.2       # USD → CNY 汇率

routes:
  - {id: 1, from: PVG, to: KIX, auto_date: "阪大.笔试 - 1", label: "上海→大阪"}
  - {id: 2, from: KIX, to: PVG, auto_date: "阪大.面试", label: "大阪→上海"}
```

### auto_date 语法

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

## 🔧 进阶配置

### 航线参数

```yaml
routes:
  - {id: 1, from: PVG, to: KIX, auto_date: "阪大.笔试 - 1",
     label: "上海→大阪",
     target: 1200}                   # 自定义目标价（覆盖全局）
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | int | ✅ | 航线唯一标识 |
| `from` | string | ✅ | 出发地 IATA 码 |
| `to` | string | ✅ | 目的地 IATA 码 |
| `auto_date` | string | ✅ | 自动日期表达式 |
| `date` | string | ✅ | 或手动指定 `YYYY-MM-DD` |
| `label` | string | ❌ | 显示名称 |
| `target` | int | ❌ | 航线专属目标价 |
| `min_departure_hour` | int | ❌ | 最早起飞小时（0-23） |

### 机场代码参考

| 代码 | 机场 | 国家 |
|------|------|------|
| PVG | 上海浦东 | 🇨🇳 |
| SHA | 上海虹桥 | 🇨🇳 |
| KIX | 关西国际机场 | 🇯🇵 |
| HND | 东京羽田 | 🇯🇵 |
| NRT | 东京成田 | 🇯🇵 |
| FUK | 福冈 | 🇯🇵 |

---

## 🐧 Linux / macOS 部署

### crontab 定时任务

```bash
# 赋予执行权限
chmod +x flight_monitor.sh

# 编辑 crontab
crontab -e

# 添加定时任务（每天 9:00 和 21:00 执行）
0 9,21 * * * /path/to/flight-monitor-skill/flight_monitor.sh >> /tmp/flight_monitor.log 2>&1
```

### systemd timer

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

### AstrBot 部署

AstrBot 环境已内置 CLI 路径，脚本会自动找到：
```
/root/AstrBot/data/skills/temp-flights-skill/skills/flights
```

---

## 💻 Windows 部署

### Task Scheduler

1. 打开「任务计划程序」
2. 创建基本任务
3. 触发器：每天 9:00 和 21:00
4. 操作：启动程序
5. 程序/脚本：`python`
6. 参数：`flight_check_cron.py`
7. 起始位置：`C:\path\to\flight-monitor-skill\`

---

## 🌐 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FLIGHT_MONITOR_CONFIG` | 配置文件路径 | `./config.yaml` |
| `FLIGHT_MONITOR_DATA_DIR` | 价格历史存储目录 | `./data/` |
| `FLIGHTS_SEARCH_PATH` | flights-search CLI 路径 | 自动查找 |
| `PYTHON` | Python 解释器 | `python3` |

### 配置文件查找顺序

1. `--config` 命令行参数
2. `FLIGHT_MONITOR_CONFIG` 环境变量
3. `./config.yaml`（脚本同目录）
4. `~/.config/flight-monitor/config.yaml`

---

## 📊 输出示例

```
✈️ 机票监控 · 时刻表
=============================================
📅 考试日程
  🏫 阪大: 笔试 8/1(77天后) | 面试 8/3(79天后)
  🏫 东科大: 笔试 8/18(94天后) | 面试 8/24(100天后)

=============================================
📊 价格快照 (05/16 10:31)
=============================================

1. 📍 上海→大阪
   📅 2026-07-31 (76天后) | 阪大笔试前1天
   ✈️ Peach Aviation | 6:15 AM→9:35 AM | 2 hr 20 min
   💰 ¥1224 ($170)
   🎯 距目标价 ¥1000 还差 ¥224
   🔔 🌟历史最低

2. 📍 东京→福冈
   📅 2026-08-24 (100天后) | 九大笔试前1天
   ✈️ Skymark | 6:20 AM→8:15 AM | 1 hr 55 min
   💰 ¥504 ($70)
   ✅ 已达目标价 ¥1000
   🔔 🎯达目标价 ¥1000

=============================================
🔔 告警汇总:
  🎯达目标价 ¥1000 → 东京→福冈
  📉降价 9% → 上海→东京
  🌟历史最低 → 上海→大阪
```

---

## 📁 文件结构

```
机票.skill/
├── flight_check_cron.py    # 主脚本 (跨平台)
├── flight_monitor.sh       # Linux crontab 封装
├── config.yaml             # 配置文件模板
├── SKILL.md               # Skill 元数据
└── README.md               # 本文档
```

---

## ❓ 常见问题

| 问题 | 解决方案 |
|------|---------|
| `❌ 未找到 flights-search CLI` | `skillhub_install install_skill flights` |
| 国际航线价格比记忆中高 | 正常，经停航班比直飞便宜但总价更低 |
| `uvx: command not found` | 安装 uv：`pip install uv` |
| Windows 中文乱码 | 确保 config.yaml 为 UTF-8 编码 |