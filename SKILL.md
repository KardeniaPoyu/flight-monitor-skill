---
name: 机票.skill
description: |
  航班价格监控。自动查询多条航线价格，达标/降价告警，配合 cron 定时运行。
  触发词：「查机票」「机票监控」「航班价格」「机票降价」「机票提醒」「flight monitor」。
  支持 Windows / Linux / macOS 全平台。
lifecycle: recurring
deactivate_on:
  - user-explicit-exit: true
---

# ✈️ 机票.skill

> 航班价格监控，自动检查多条航线，达标/降价即时告警

## 依赖

| 依赖 | 安装方式 |
|------|---------|
| Python 3.11+ | 系统自带或 `brew install python` |
| uv | `pip install uv` |
| flights skill | `skillhub_install install_skill flights` |

## 使用

```bash
# ✅ 检查依赖
python flight_check_cron.py --check

# ✅ 运行监控
python flight_check_cron.py

# ✅ 指定配置
python flight_check_cron.py --config /path/to/config.yaml

# ✅ Linux crontab
chmod +x flight_monitor.sh
0 9,21 * * * /path/to/flight_monitor.sh
```

## 配置

编辑 `config.yaml`：

```yaml
exam_schedule:
  Your University:
    笔试: "2026-08-01"
    面试: "2026-08-03"

target_price: 1000
exchange_rate: 7.2

routes:
  - {id: 1, from: SHA, to: KIX, auto_date: "Your University.笔试 - 1", label: "出发→大阪"}
```

### auto_date

```
学校名.考试类型 [+/- 天数]
```

## 告警

- 🎯 达目标价
- 📉 降价 ≥5%
- 🌟 历史最低价