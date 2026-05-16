#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

"""航班价格监控 - 基于考试日程动态计算航班日期"""
import json, os, subprocess, re
from datetime import datetime, date, timedelta
from pathlib import Path

# ===== 考试日程 (via exam-prep-2026 GitHub 验证) =====
EXAM_SCHEDULE = {
    "阪大": {
        "笔试": date(2026, 8, 1),   # 8/1(土) 9-12時 @吹田
        "面试": date(2026, 8, 3),   # 8/3(月) 10:30～ @吹田
    },
    "东科大": {
        "笔试": date(2026, 8, 18),  # 8/18(火) 9:30-12:00 @東科大
        "面试": date(2026, 8, 24),  # 8/24(月) 口頭試問(専門+英語上位者のみ)
    },
    "东大": {
        "笔试": date(2026, 8, 20),  # 8/20(木) 一般教育科目(数学or编程)
        "専門": date(2026, 8, 26),  # 8/26(水) 13:00-15:30 創造情報学
        "面试": date(2026, 8, 27),  # 8/27(木) 口述試験 @工6号館
    },
    "九大": {
        "笔试": date(2026, 8, 25),  # 8/25(火) 9:00-17:30 @伊都(一天搞定,无面试)
    },
}

# ===== 航线定义：基于考试日程自动计算日期 =====
# 每条路线定义一个 "flight_date" 计算函数
# 参数: EXAM_SCHEDULE -> date

def fmt_date(d):
    """格式化日期，去掉前导零"""
    return f"{d.month}/{d.day}"

def calc_flight_dates(schedule):
    """基于考试日程计算所有航班日期"""
    阪大 = schedule["阪大"]
    东科大 = schedule["东科大"]
    东大 = schedule["东大"]
    九大 = schedule["九大"]
    
    routes = [
        {
            "id": 1,
            "from": "PVG", "to": "KIX",
            "date": (阪大["笔试"] - timedelta(days=1)).strftime("%Y-%m-%d"),
            "label": "上海→大阪 (考前1天)",
            "context": f"阪大 {fmt_date(阪大['笔试'])} 笔试 | {fmt_date(阪大['面试'])} 面试",
            "target": 1000,
        },
        {
            "id": 2,
            "from": "KIX", "to": "PVG",
            "date": (阪大["面试"]).strftime("%Y-%m-%d"),
            "label": "大阪→上海 (面试当天)",
            "context": f"阪大 {fmt_date(阪大['面试'])} 面试结束→当晚回国递签",
            "target": 1000,
        },
        {
            "id": 3,
            "from": "PVG", "to": "HND",
            "date": (东科大["笔试"] - timedelta(days=1)).strftime("%Y-%m-%d"),
            "label": "上海→东京 (东科大考前1天)",
            "context": f"东科大 {fmt_date(东科大['笔试'])} 笔试 | {fmt_date(东科大['面试'])} 面试 | 东大 {fmt_date(东大['笔试'])} 笔试",
            "target": 1000,
        },
        {
            "id": 4,
            "from": "HND", "to": "FUK",
            "date": (九大["笔试"] - timedelta(days=1)).strftime("%Y-%m-%d"),
            "label": "东京→福冈 (九大考前1天)",
            "context": f"⚠️与东科大面试({fmt_date(东科大['面试'])})同日 | 九大 {fmt_date(九大['笔试'])} 笔试",
            "target": 1000,
        },
        {
            "id": 5,
            "from": "FUK", "to": "HND",
            "date": (九大["笔试"]).strftime("%Y-%m-%d"),
            "label": "福冈→东京 (九大当天回)",
            "context": f"九大笔试 {fmt_date(九大['笔试'])} 17:30结束→傍晚回东京 | 东大 {fmt_date(东大['専門'])} 専門",
            "target": 1000,
            "min_departure_hour": 18,  # 考试17:30结束，必须18:00后起飞
        },
        {
            "id": 6,
            "from": "HND", "to": "PVG",
            "date": (东大["面试"] + timedelta(days=1)).strftime("%Y-%m-%d"),
            "label": "东京→上海 (返程)",
            "context": f"东大 {fmt_date(东大['面试'])} 口述→全部考试结束→回国",
            "target": 1000,
        },
    ]
    return routes

# ===== 配置 =====
SKILL_DIR = Path(r"C:\Users\LENOVO\.agents\skills\flights")
SCRIPT = str(SKILL_DIR / "scripts" / "flights-search")
DATA_DIR = Path(r"C:\Users\LENOVO\.qclaw\data\flight_monitor")
DATA_FILE = DATA_DIR / "flight_prices.json"
EXCHANGE_RATE = 7.2

def init_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"routes": {}, "last_update": "", "exam_schedule": {k: {sk: str(sv) for sk, sv in v.items()} for k, v in EXAM_SCHEDULE.items()}}, f, ensure_ascii=False)

def load():
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"routes": {}, "exam_schedule": {}}

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_hour(depart_str):
    """解析 '3:05 PM' -> 15, '11:00 AM' -> 11, None if unparseable"""
    m = re.match(r'(\d+):(\d+)\s*([AP])M', depart_str)
    if m:
        h = int(m.group(1))
        if m.group(3) == 'P' and h != 12:
            h += 12
        elif m.group(3) == 'A' and h == 12:
            h = 0
        return h
    return None

def query_flight_details(origin, dest, date_str, min_hour=None):
    """查询航班详情。用列分割法解析 flights-search 表格输出。
    min_hour: 只返回 departure hour >= min_hour 的航班 (e.g. 18 for after 6PM)"""
    # 国际航线不加 --nonstop (经停航班更便宜)
    # 中日航线: PVG/SHA <-> KIX/HND/NRT
    is_intl = (origin in ["PVG", "SHA"] and dest in ["KIX", "HND", "NRT"]) or \
               (origin in ["KIX", "HND", "NRT"] and dest in ["PVG", "SHA"])
    use_nonstop = "" if is_intl else "--nonstop"
    cmd = ["uvx", "--with", "fast-flights", "python", SCRIPT, origin, dest, date_str] + ([use_nonstop] if use_nonstop else [])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(SKILL_DIR))
    
    flights = []
    for line in result.stdout.split("\n"):
        if "Route" in line or "---" in line or "Check price" in line or not line.strip():
            continue
        price_match = re.search(r"\$(\d+)", line)
        if not price_match:
            continue
        usd_price = int(price_match.group(1))

        # 列分割法: flights-search 输出用 2+ 空格分隔列
        # 完整格式: [Depart, Arrive, Airline, Price, Duration]
        parts = re.split(r'\s{2,}', line.strip())
        
        if len(parts) >= 5:
            # 完整格式: 有 airline/depart/arrive/duration
            airline = parts[2]
            # 提取起降时间（去掉日期部分）
            times = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', line)
            depart = times[0] if times else parts[0]
            arrive = times[1] if len(times) > 1 else parts[1]
            duration = parts[4] if len(parts) > 4 else "未知"
        else:
            # 简化格式（国际航线）: 只有价格，无详细列
            airline = "未知"
            depart = "未知"
            arrive = "未知"
            duration = "未知"

        # 时间约束过滤
        if min_hour is not None and depart != "未知":
            dh = parse_hour(depart)
            if dh is not None and dh < min_hour:
                continue

        flights.append({
            "airline": airline, "usd_price": usd_price,
            "cny_price": int(usd_price * EXCHANGE_RATE),
            "depart": depart, "arrive": arrive, "duration": duration
        })
    
    if flights:
        flights.sort(key=lambda x: x["usd_price"])
        return flights[0]
    return None

def gen_report():
    init_data()
    data = load()
    now = datetime.now()
    routes = calc_flight_dates(EXAM_SCHEDULE)
    
    lines = [
        "✈️ 机票监控 · 时刻表",
        "=" * 45,
        "",
        "📅 考试日程",
    ]
    
    # 汇总考试日程
    for uni_name, exams in EXAM_SCHEDULE.items():
        exam_parts = []
        for exam_type, exam_date in exams.items():
            days_left = (exam_date - date.today()).days
            exam_parts.append(f"{exam_type} {fmt_date(exam_date)}({days_left}天后)")
        lines.append(f"  🏫 {uni_name}: {' | '.join(exam_parts)}")
    
    lines.append("")
    lines.append("=" * 45)
    lines.append(f"📊 价格快照 ({now.strftime('%m/%d %H:%M')})")
    lines.append("=" * 45)
    
    alerts = []
    
    for route in routes:
        rid = route["id"]
        origin = route["from"]
        dest = route["to"]
        fdate = route["date"]
        label = route["label"]
        context = route["context"]
        target = route["target"]
        
        days = (datetime.strptime(fdate, "%Y-%m-%d").date() - date.today()).days
        min_hour = route.get("min_departure_hour")
        flight = query_flight_details(origin, dest, fdate, min_hour=min_hour)
        
        if flight:
            key = str(rid)
            if key not in data["routes"]:
                data["routes"][key] = {"history": [], "last": None}
            rd = data["routes"][key]
            last = rd.get("last")
            hist = rd.get("history", [])
            
            old_price = last.get("cny_price") if isinstance(last, dict) else None
            
            if old_price:
                change = (flight["cny_price"] - old_price) / old_price * 100
                if abs(change) >= 5:
                    change_str = f"📉降{-change:.0f}%" if change < 0 else f"📈涨{change:.0f}%"
                else:
                    change_str = "→持平"
            else:
                change_str = "首查"
            
            hist.append(flight["cny_price"])
            if len(hist) > 30:
                hist[:] = hist[-30:]
            rd["history"] = hist
            rd["last"] = flight
            
            alert = ""
            if old_price and flight["cny_price"] < old_price * 0.95:
                alert = f"📉降价 {abs(change):.0f}%"
            elif flight["cny_price"] <= target:
                alert = f"🎯达目标价 ¥{target}"
            elif hist and len(hist) > 1 and flight["cny_price"] <= min(hist[:-1]):
                alert = "🌟历史最低"
            
            if alert:
                alerts.append(f"{alert} → {label}")
            
            target_diff = flight["cny_price"] - target
            
            lines.append(f"\n{rid}. 📍 {label}")
            lines.append(f"   📅 {fdate} ({days}天后) | {context}")
            if flight["airline"] != "未知":
                lines.append(f"   ✈️ {flight['airline']} | {flight['depart']}→{flight['arrive']} | {flight['duration']}")
            lines.append(f"   💰 ¥{flight['cny_price']} (${flight['usd_price']})")
            if target_diff > 0:
                lines.append(f"   🎯 距目标价 ¥{target} 还差 ¥{target_diff}")
                if change_str != "首查":
                    lines.append(f"      {change_str}")
            else:
                lines.append(f"   ✅ 已达目标价 ¥{target}")
            if alert:
                lines.append(f"   🔔 {alert}")
        else:
            lines.append(f"\n{rid}. 📍 {label}")
            lines.append(f"   📅 {fdate} ({days}天后) | {context}")
            lines.append(f"   ⚠️ 查询失败")
    
    data["last_update"] = now.isoformat()
    save(data)
    
    if alerts:
        lines.append("\n" + "=" * 45)
        lines.append("🔔 告警汇总:")
        for a in alerts:
            lines.append(f"  {a}")
    
    lines.append("\n" + "=" * 45)
    lines.append("⏰ 下次检查: 9:00 / 15:00 / 21:00 / 3:00")
    
    return "\n".join(lines), alerts

if __name__ == "__main__":
    report, _ = gen_report()
    print(report)