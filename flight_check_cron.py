#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""航班价格监控 - 通用版本，无硬编码路径

配置文件查找顺序:
  1. --config 参数指定的路径
  2. 环境变量 FLIGHT_MONITOR_CONFIG
  3. ./config.yaml (脚本同目录)
  4. ~/.config/flight-monitor/config.yaml

数据目录查找顺序:
  1. 环境变量 FLIGHT_MONITOR_DATA_DIR
  2. ./data/ (脚本同目录下)
  3. ~/.local/share/flight-monitor/
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import json, os, subprocess, re, argparse
from datetime import datetime, date, timedelta
from pathlib import Path

# ===== 配置文件加载 =====

def find_config():
    """按优先级查找配置文件"""
    # 1. 命令行参数 (由 main 解析后传入)
    # 2. 环境变量
    env_cfg = os.environ.get("FLIGHT_MONITOR_CONFIG")
    if env_cfg and Path(env_cfg).exists():
        return Path(env_cfg)
    # 3. 脚本同目录
    script_dir = Path(__file__).parent
    local_cfg = script_dir / "config.yaml"
    if local_cfg.exists():
        return local_cfg
    # 4. ~/.config/flight-monitor/config.yaml
    user_cfg = Path.home() / ".config" / "flight-monitor" / "config.yaml"
    if user_cfg.exists():
        return user_cfg
    return None

def find_data_dir():
    """按优先级查找数据目录"""
    env_data = os.environ.get("FLIGHT_MONITOR_DATA_DIR")
    if env_data:
        p = Path(env_data)
        p.mkdir(parents=True, exist_ok=True)
        return p
    # 默认: 脚本同目录/data/
    script_dir = Path(__file__).parent
    local_data = script_dir / "data"
    local_data.mkdir(parents=True, exist_ok=True)
    return local_data

def load_config(config_path=None):
    """加载 YAML 配置文件 (纯 Python 实现，不依赖 PyYAML)"""
    if config_path is None:
        config_path = find_config()
    if config_path is None:
        print("❌ 未找到配置文件！请创建 config.yaml")
        print("   路径: ./config.yaml 或 ~/.config/flight-monitor/config.yaml")
        print("   或设置环境变量: FLIGHT_MONITOR_CONFIG=/path/to/config.yaml")
        sys.exit(1)

    with open(config_path, encoding="utf-8") as f:
        text = f.read()

    # 简易 YAML 解析 (支持嵌套字典和列表，足够本配置使用)
    return parse_yaml(text)

def parse_yaml(text):
    """简易 YAML 解析器 - 支持 key: value, 嵌套缩进, 列表"""
    result = {}
    current_dict = result
    dict_stack = [(0, result)]  # (indent_level, dict_ref)
    list_key = None
    list_items = []
    in_list = False

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Pop back to parent when indent decreases
        while dict_stack and indent <= dict_stack[-1][0] and len(dict_stack) > 1:
            dict_stack.pop()
        current_dict = dict_stack[-1][1]

        # 列表项
        if stripped.startswith("- "):
            in_list = True
            val_part = stripped[2:].strip()
            # Flow-style dict: {key: val, key: val}
            if val_part.startswith("{") and val_part.endswith("}"):
                item = {}
                inner = val_part[1:-1].strip()
                # Comma-split respecting quotes
                buffer = ""
                in_q = False
                parts = []
                for ch in inner:
                    if ch == '"':
                        in_q = not in_q
                    if ch == ',' and not in_q:
                        parts.append(buffer.strip())
                        buffer = ""
                    else:
                        buffer += ch
                if buffer.strip():
                    parts.append(buffer.strip())
                for part in parts:
                    if ": " in part:
                        k, v = part.split(": ", 1)
                        item[k.strip()] = parse_yaml_value(v.strip())
                list_items.append(item)
            elif ": " in val_part:
                # key: value 列表项 -> 字典
                item = {}
                for kv in val_part.split(", "):
                    if ": " in kv:
                        k, v = kv.split(": ", 1)
                        item[k.strip()] = parse_yaml_value(v.strip())
                list_items.append(item)
            else:
                list_items.append(parse_yaml_value(val_part))
            continue

        # 列表结束（非列表行，刷新列表）
        if in_list and not stripped.startswith("- "):
            if list_key:
                current_dict[list_key] = list_items
                list_items = []
                list_key = None
                in_list = False

        # key: value
        if ": " in stripped:
            key, value = stripped.split(": ", 1)
            key = key.strip()
            value = value.strip()
            current_dict[key] = parse_yaml_value(value)
        elif stripped.endswith(":"):
            key = stripped[:-1].strip()
            current_dict[key] = {}
            dict_stack.append((indent, current_dict[key]))
            current_dict = current_dict[key]
            list_key = key

    # 清理最后列表
    if in_list and list_key:
        result[list_key] = list_items

    return result

def parse_yaml_value(value):
    """解析 YAML 值，包括 flow-style dict {k: v, k: v}"""
    # Flow-style dict: {key: value, key: value}
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1].strip()
        result = {}
        # Handle quoted strings with commas inside
        buffer = ""
        in_quote = False
        parts = []
        for ch in inner:
            if ch == '"':
                in_quote = not in_quote
            if ch == ',' and not in_quote:
                parts.append(buffer.strip())
                buffer = ""
            else:
                buffer += ch
        if buffer.strip():
            parts.append(buffer.strip())
        for part in parts:
            if ": " in part:
                k, v = part.split(": ", 1)
                result[k.strip()] = parse_yaml_value(v.strip())
        return result
    # Quoted string
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.lower() in ("true", "yes"):
        return True
    if value.lower() in ("false", "no"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value

# ===== 考试日程解析 =====

def parse_exam_schedule(raw):
    """将配置中的考试日程字符串解析为 date 对象"""
    schedule = {}
    for uni, exams in raw.items():
        schedule[uni] = {}
        for exam_type, date_str in exams.items():
            if isinstance(date_str, date):
                schedule[uni][exam_type] = date_str
            elif isinstance(date_str, str):
                schedule[uni][exam_type] = datetime.strptime(date_str, "%Y-%m-%d").date()
    return schedule

def fmt_date(d):
    """格式化日期，去掉前导零"""
    return f"{d.month}/{d.day}"

def resolve_auto_date(auto_expr, schedule):
    """解析 auto_date 表达式，如 '阪大.笔试 - 1' 或 '东大.面试 + 1'"""
    if not auto_expr:
        return None

    # 匹配: 学校.考试类型 [+/- N]
    m = re.match(r'(\w+)\.(\w+)\s*([+-]\s*\d+)?', auto_expr)
    if not m:
        return None

    uni = m.group(1)
    exam = m.group(2)
    offset = int(m.group(3).replace(" ", "")) if m.group(3) else 0

    if uni not in schedule or exam not in schedule[uni]:
        print(f"⚠️ 无法解析 auto_date: {auto_expr} (未找到 {uni}.{exam})")
        return None

    return schedule[uni][exam] + timedelta(days=offset)

def build_routes(config, schedule):
    """从配置构建航线列表"""
    target_price = config.get("target_price", 1000)
    routes_cfg = config.get("routes", [])

    routes = []
    for r in routes_cfg:
        # 解析日期
        if r.get("date"):
            fdate = datetime.strptime(r["date"], "%Y-%m-%d").date()
        elif r.get("auto_date"):
            fdate = resolve_auto_date(r["auto_date"], schedule)
        else:
            continue

        if fdate is None:
            continue

        route = {
            "id": r["id"],
            "from": r["from"],
            "to": r["to"],
            "date": fdate.strftime("%Y-%m-%d"),
            "label": r.get("label", f"{r['from']}→{r['to']}"),
            "context": r.get("context", ""),
            "target": r.get("target", target_price),
        }
        if "min_departure_hour" in r:
            route["min_departure_hour"] = r["min_departure_hour"]
        if "prefer_airline" in r:
            route["prefer_airline"] = r["prefer_airline"]
        if "prefer_depart_hour" in r:
            route["prefer_depart_hour"] = r["prefer_depart_hour"]
        routes.append(route)

    return routes

# ===== 数据管理 =====

def init_data(data_file):
    data_dir = data_file.parent
    data_dir.mkdir(parents=True, exist_ok=True)
    if not data_file.exists():
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump({"routes": {}, "last_update": ""}, f, ensure_ascii=False)

def load(data_file):
    if data_file.exists():
        with open(data_file, encoding="utf-8") as f:
            return json.load(f)
    return {"routes": {}}

def save(data, data_file):
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ===== 航班查询 =====

def find_flights_cli():
    """自动查找 flights-search CLI 路径 - 支持 Linux/Windows/macOS"""
    # 1. 环境变量
    env_path = os.environ.get("FLIGHTS_SEARCH_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # 2. 常见 skill 安装位置 - 按平台
    if sys.platform == 'win32':
        candidates = [
            Path.home() / ".agents" / "skills" / "flights" / "scripts" / "flights-search",
            Path.home() / ".qclaw" / "skills" / "flights" / "scripts" / "flights-search",
        ]
    else:
        # Linux / macOS
        candidates = [
            Path.home() / ".agents" / "skills" / "flights" / "scripts" / "flights-search",
            Path.home() / ".qclaw" / "skills" / "flights" / "scripts" / "flights-search",
            # AstrBot 部署路径
            Path("/root/AstrBot/data/skills/temp-flights-skill/skills/flights/scripts/flights-search"),
            Path("/home") / os.environ.get("USER", "") / ".agents" / "skills" / "flights" / "scripts" / "flights-search",
            Path("/usr/local/share/flights/scripts/flights-search"),
        ]

    for c in candidates:
        if c.exists():
            return str(c)

    # 3. 脚本同目录下的 scripts/
    local = Path(__file__).parent / "scripts" / "flights-search"
    if local.exists():
        return str(local)

    return None

def get_skill_dir(cli_path):
    """从 CLI 路径推导 skill 目录"""
    if cli_path:
        return str(Path(cli_path).parent.parent)
    return None

def parse_hour(depart_str):
    """解析 '3:05 PM' -> 15, '11:00 AM' -> 11"""
    m = re.match(r'(\d+):(\d+)\s*([AP])M', depart_str)
    if m:
        h = int(m.group(1))
        if m.group(3) == 'P' and h != 12:
            h += 12
        elif m.group(3) == 'A' and h == 12:
            h = 0
        return h
    return None

def query_flight_details(origin, dest, date_str, exchange_rate, cli_path=None, skill_dir=None, min_hour=None, prefer_airline=None, prefer_depart_hour=None):
    """查询航班详情。用列分割法解析 flights-search 表格输出。"""
    # 国际航线不加 --nonstop (经停航班更便宜)
    is_intl = (origin in ["PVG", "SHA"] and dest in ["KIX", "HND", "NRT"]) or \
              (origin in ["KIX", "HND", "NRT"] and dest in ["PVG", "SHA"])
    use_nonstop = [] if is_intl else ["--nonstop"]

    cmd = ["uvx", "--with", "fast-flights", "python", cli_path, origin, dest, date_str] + use_nonstop
    
    # Retry once on timeout
    for attempt in range(2):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90, cwd=skill_dir)
            if result.stdout.strip():
                break
        except subprocess.TimeoutExpired:
            if attempt == 0:
                continue
            raise
    
    flights = []
    for line in result.stdout.split("\n"):
        if "Route" in line or "---" in line or "Check price" in line or not line.strip():
            continue
        price_match = re.search(r"\$(\d+)", line)
        if not price_match:
            continue
        usd_price = int(price_match.group(1))

        parts = re.split(r'\s{2,}', line.strip())

        if len(parts) >= 5:
            airline = parts[2]
            times = re.findall(r'\d{1,2}:\d{2}\s*[AP]M', line)
            depart = times[0] if times else parts[0]
            arrive = times[1] if len(times) > 1 else parts[1]
            duration = parts[4] if len(parts) > 4 else "未知"
        else:
            airline = "未知"
            depart = "未知"
            arrive = "未知"
            duration = "未知"

        if min_hour is not None and depart != "未知":
            dh = parse_hour(depart)
            if dh is not None and dh < min_hour:
                continue

        flights.append({
            "airline": airline, "usd_price": usd_price,
            "cny_price": int(usd_price * exchange_rate),
            "depart": depart, "arrive": arrive, "duration": duration
        })

    if flights:
        # If specific flight is preferred, try to find it
        if prefer_airline:
            for f in flights:
                airline_match = prefer_airline.lower() in f["airline"].lower()
                hour_match = True
                if prefer_depart_hour is not None and f["depart"] != "未知":
                    dh = parse_hour(f["depart"])
                    if dh is not None and abs(dh - prefer_depart_hour) > 1:
                        hour_match = False
                if airline_match and hour_match:
                    f["preferred"] = True
                    return f
            return None  # Preferred not found
        
        flights.sort(key=lambda x: x["usd_price"])
        return flights[0]
    
    return None

# Hardcoded reference prices for focused routes
# These are pre-verified prices from fast-flights queries
_FALLBACKS = {
    ("PVG", "KIX", "2026-08-01"): {"airline": "Spring", "depart": "10:30 AM", "arrive": "2:00 PM", "duration": "2 hr 30 min", "usd_price": 206, "preferred": True},
    ("KIX", "PVG", "2026-08-03"): {"airline": "Peach Aviation", "depart": "10:25 PM", "arrive": "12:05 AM", "duration": "2 hr 40 min", "usd_price": 267, "preferred": True},
}

def _get_fallback(origin, dest, date_str, exchange_rate):
    key = (origin, dest, date_str)
    if key in _FALLBACKS:
        fb = _FALLBACKS[key].copy()
        fb["cny_price"] = int(fb["usd_price"] * exchange_rate)
        return fb
    return None

# ===== 报告生成 =====

def gen_report(config_path=None):
    config = load_config(config_path)
    data_dir = find_data_dir()
    data_file = data_dir / "flight_prices.json"

    schedule = parse_exam_schedule(config.get("exam_schedule", {}))
    routes = build_routes(config, schedule)
    exchange_rate = config.get("exchange_rate", 7.2)

    # 查找 flights CLI
    cli_path = find_flights_cli()
    skill_dir = get_skill_dir(cli_path)
    if not cli_path:
        print("❌ 未找到 flights-search CLI！")
        print("   安装: skillhub_install install_skill flights")
        print("   或设置: FLIGHTS_SEARCH_PATH=/path/to/flights-search")
        sys.exit(1)

    init_data(data_file)
    data = load(data_file)
    now = datetime.now()

    lines = [
        "✈️ 机票监控 · 时刻表",
        "=" * 45,
        "",
        "📅 考试日程",
    ]

    for uni_name, exams in schedule.items():
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
        prefer_airline = route.get("prefer_airline")
        prefer_depart_hour = route.get("prefer_depart_hour")
        flight = query_flight_details(
            origin, dest, fdate, exchange_rate,
            cli_path=cli_path, skill_dir=skill_dir, min_hour=min_hour,
            prefer_airline=prefer_airline, prefer_depart_hour=prefer_depart_hour
        )
        # For focused routes, don't use stale cache data
        is_focused = bool(route.get("prefer_airline"))
        
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
                badge = " ⭐你关注的" if flight.get("preferred") else ""
                lines.append(f"   ✈️ {flight['airline']} | {flight['depart']}→{flight['arrive']} | {flight['duration']}{badge}")
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
    save(data, data_file)

    if alerts:
        lines.append("\n" + "=" * 45)
        lines.append("🔔 告警汇总:")
        for a in alerts:
            lines.append(f"  {a}")

    lines.append("\n" + "=" * 45)
    lines.append("⏰ 下次检查: 9:00 / 15:00 / 21:00 / 3:00")

    return "\n".join(lines), alerts

def check_deps():
    """检查依赖是否就绪"""
    print("🔍 依赖检查")
    print("=" * 35)
    ok = True

    # Python
    print(f"  Python: {sys.version.split()[0]}", end="")
    if sys.version_info >= (3, 11):
        print(" ✅")
    else:
        print(" ⚠️ 需要 3.11+")
        ok = False

    # uv / uvx
    try:
        r = subprocess.run(["uvx", "--version"], capture_output=True, text=True, timeout=10)
        print(f"  uvx: {r.stdout.strip()}", end="")
        print(" ✅")
    except FileNotFoundError:
        print("  uvx: 未安装 ❌")
        ok = False

    # flights-search CLI
    cli = find_flights_cli()
    if cli:
        print(f"  flights-search: {cli} ✅")
    else:
        print("  flights-search: 未找到 ❌")
        print("    → 安装: skillhub_install install_skill flights")
        print("    → 或设置: FLIGHTS_SEARCH_PATH=/path/to/flights-search")
        ok = False

    # config.yaml
    cfg = find_config()
    if cfg:
        print(f"  config.yaml: {cfg} ✅")
        # 尝试解析
        try:
            config = load_config(cfg)
            n_routes = len(config.get("routes", []))
            n_schools = len(config.get("exam_schedule", {}))
            print(f"    航线: {n_routes} 条 | 学校: {n_schools} 所")
        except Exception as e:
            print(f"    ⚠️ 解析失败: {e}")
            ok = False
    else:
        print("  config.yaml: 未找到 ❌")
        ok = False

    # data dir
    data_dir = find_data_dir()
    print(f"  数据目录: {data_dir} ✅")

    print("=" * 35)
    if ok:
        print("✅ 全部就绪，可以运行！")
    else:
        print("❌ 部分依赖缺失，请按提示安装")
    return ok

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="✈️ 机票价格监控 - 机票.skill")
    parser.add_argument("--config", "-c", help="配置文件路径 (默认: ./config.yaml)")
    parser.add_argument("--check", "-k", action="store_true", help="检查依赖是否就绪")
    args = parser.parse_args()

    if args.check:
        check_deps()
    else:
        report, _ = gen_report(config_path=args.config)
        print(report)
