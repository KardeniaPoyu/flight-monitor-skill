# 机票.skill

航班价格监控。自动查询多条航线价格，达标/降价告警，配合 cron 定时运行。

触发词：查机票、机票监控、航班价格、机票降价、机票提醒、flight monitor。

## 依赖

- Python 3.11+
- uv (package runner)
- flights skill (`skillhub_install install_skill flights`)

## 使用

```bash
# 检查依赖
python flight_check_cron.py --check

# 运行
python flight_check_cron.py

# 指定配置
python flight_check_cron.py --config /path/to/config.yaml

# Linux crontab
0 9,21 * * * /path/to/flight_monitor.sh
```

## 配置

编辑 `config.yaml`：

```yaml
exam_schedule:
  学校名:
    笔试: "2026-08-01"
    面试: "2026-08-03"

target_price: 1000
exchange_rate: 7.2

routes:
  - {id: 1, from: PVG, to: KIX, auto_date: "学校名.笔试 - 1", label: "上海→大阪"}
```

auto_date 语法：`"学校.考试类型 [+/- 天数]"`

## 告警

- 🎯 达目标价
- 📉 降价 ≥5%
- 🌟 历史最低价