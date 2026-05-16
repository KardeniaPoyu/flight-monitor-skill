# Flight Monitor Skill

监控日本考研航线的价格，自动检查达标推送。

## 功能

- 监控 6 条中日航线价格
- 自动对比目标价 ¥1000
- 4 次/天 自动检查（3/9/15/21点）
- 微信推送告警

## 安装

```bash
# 依赖已内置，uvx自动下载
uv --version  # 需已安装
```

## 使用

```bash
# 手动运行
python C:\Users\LENOVO\.agents\skills\flight-monitor\flight_check_cron.py

# 查看帮助
python C:\Users\LENOVO\.agents\skills\flight-monitor\flight_check_cron.py --help
```

## 配置

修改脚本中的 `EXAM_SCHEDULE` 字典可以调整考试日期。

## 定时任务

脚本运行后会将 cron jobs 写入 `C:\Users\LENOVO\.qclaw\data\flight_monitor\` 目录。

## 输出示例

```
✈️ 机票监控 · 时刻表
=============================================
📅 考试日程
  🏫 阪大: 笔试 8/1 | 面试 8/3
  ...

📊 价格快照
1. 📍 上海→大阪 (考前1天)
   💰 ¥1231 ($171)
   🎯 距目标价 ¥1000 还差 ¥231
```

## 依赖

- Python 3.11+
- uv (Package runner)
- fast-flights (通过 uvx 自动下载)

## 文件

- `flight_check_cron.py` - 主脚本