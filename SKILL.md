# Flight Monitor Skill

监控航班价格，自动检查达标推送。适合考试、旅行等定时航班需求。

## 特性

- 📊 6 条航线价格监控
- 🎯 自定义目标价，达标告警
- 📉 价格涨跌追踪 (5%/10%阈值)
- ⏰ 支持定时自动检查 (配合 cron / crontab)
- 🔧 纯 Python，无外部依赖 (无需 PyYAML)
- 📁 通过 config.yaml 配置，无需修改代码
- 🐧 **Windows / Linux / macOS 全平台支持**

## 安装

```bash
# 安装航班查询 CLI
skillhub_install install_skill flights

# 安装本 skill
skillhub_install install_skill_zip flight-monitor-skill.zip
```

依赖：
- Python 3.11+
- uv (Python package runner)
- fast-flights (通过 uvx 自动下载)

## 快速开始

```bash
# 1. 编辑 config.yaml，填入你的考试日程
# 2. 运行
python flight_check_cron.py
```

## 配置

复制 `config.yaml` 到你的工作目录，修改考试日程：

```yaml
exam_schedule:
  阪大:
    笔试: "2026-08-01"
    面试: "2026-08-03"

target_price: 1000       # 目标价格 (CNY)
exchange_rate: 7.2       # 汇率

routes:
  - {id: 1, from: PVG, to: KIX, auto_date: "阪大.笔试 - 1", label: "上海→大阪"}
```

### auto_date 语法

```
学校名.考试类型 [+/- 天数]
```

示例：
- `"阪大.笔试 - 1"` → 阪大笔试前1天
- `"东大.面试 + 1"` → 东大面试后1天
- `"九大.笔试"` → 九大笔试当天

## 使用

```bash
# 默认配置 (config.yaml 在同目录)
python flight_check_cron.py

# 指定配置文件
python flight_check_cron.py --config ~/my-exam-config.yaml

# 环境变量
export FLIGHT_MONITOR_CONFIG=/path/to/config.yaml
export FLIGHT_MONITOR_DATA_DIR=/path/to/data/
export FLIGHTS_SEARCH_PATH=/path/to/flights-search
```

## 配置文件优先级

1. `--config` 命令行参数
2. `FLIGHT_MONITOR_CONFIG` 环境变量
3. `./config.yaml` (脚本同目录)
4. `~/.config/flight-monitor/config.yaml`

## Linux 部署

### crontab 定时任务

```bash
# 赋予执行权限
chmod +x flight_monitor.sh

# 编辑 crontab
crontab -e

# 添加 (每天 3:00/9:00/15:00/21:00 执行)
0 3,9,15,21 * * * /path/to/flight-monitor-skill/flight_monitor.sh
```

### systemd timer (可选)

```ini
# /etc/systemd/system/flight-monitor.timer
[Unit]
Description=Flight Price Monitor

[Timer]
OnCalendar=*-*-* 03:00:00
OnCalendar=*-*-* 09:00:00
OnCalendar=*-*-* 15:00:00
OnCalendar=*-*-* 21:00:00

[Install]
WantedBy=timers.target
```

### AstrBot 部署

如果使用 AstrBot，CLI 路径已内置：
```
/root/AstrBot/data/skills/temp-flights-skill/skills/flights
```

## 输出示例

```
✈️ 机票监控 · 时刻表
=============================================
📅 考试日程
  🏫 阪大: 笔试 8/1(77天后) | 面试 8/3(79天后)

📊 价格快照 (05/16 10:00)
=============================================
1. 📍 上海→大阪
   📅 2026-07-31 (76天后)
   ✈️ Peach Aviation | 6:15 AM→9:35 AM | 2 hr 20 min
   💰 ¥1231 ($171)
   🎯 距目标价 ¥1000 还差 ¥231
```

## 文件结构

```
flight-monitor-skill/
├── flight_check_cron.py    # 主脚本 (跨平台)
├── flight_monitor.sh       # Linux crontab 封装
├── config.yaml             # 配置文件
└── SKILL.md                # 本文档
```