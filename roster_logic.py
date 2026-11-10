import calendar
from datetime import date
from db import get_conn

def month_days(year, month):
    total = calendar.monthrange(year, month)[1]
    return [date(year, month, d) for d in range(1, total+1)]

def operates_on(rule, day, holidays):
    is_holiday = day.isoformat() in holidays
    is_sunday = day.weekday() == 6
    if rule == "365":
        return True
    if rule == "except_holidays":
        return not is_holiday
    if rule == "except_sundays_holidays":
        return not is_holiday and not is_sunday
    return True

def load_data():
    conn = get_conn()
    data = {}

    data["employees"] = {
        r["id"]: dict(r) for r in conn.execute("SELECT * FROM employees")
    }

    data["processes"] = {}
    for r in conn.execute(
        "SELECT p.id, p.name, p.operating_rule, p.min_staff, b.name AS brand "
        "FROM processes p JOIN brands b ON b.id = p.brand_id"
    ):
        data["processes"][r["id"]] = dict(r)

    data["assignments"] = {}
    for r in conn.execute("SELECT employee_id, process_id FROM assignments"):
        data["assignments"].setdefault(r["process_id"], []).append(r["employee_id"])

    data["holidays"] = {r["date"] for r in conn.execute("SELECT date FROM holidays")}

    data["leaves"] = {
        (r["employee_id"], r["date"]): r["kind"]
        for r in conn.execute("SELECT employee_id, date, kind FROM leaves")
    }

    data["preferred_offs"] = {
        r["employee_id"]: r["weekday"]
        for r in conn.execute("SELECT employee_id, weekday FROM preferred_offs")
    }        
    conn.close()
    return data

def base_status(emp_id, day, data):
    kind = data["leaves"].get((emp_id, day.isoformat()))
    if kind == "leave":
        return "LEAVE"
    if kind == "comp_off":
        return "COMP"

    open_somewhere = False
    for pid, emps in data["assignments"].items():
        if emp_id in emps:
            rule = data["processes"][pid]["operating_rule"]
            if operates_on(rule, day, data["holidays"]):
                open_somewhere = True
                break

    if not open_somewhere:
        if day.isoformat() in data["holidays"]:
            return "PH"
        return "OFF"
    return "WORK"

def build_grid(year, month, data):
    grid = {}
    for emp_id in data["employees"]:
        grid[emp_id] = {}
        for day in month_days(year, month):
            grid[emp_id][day.isoformat()] = base_status(emp_id, day, data)
    return grid

def workers_on(paid, day, grid, data):
    working = []
    for emp_id in data["assignments"].get(paid, []):
        if grid[emp_id][day.isoformat()] == "WORK":
            working.append(emp_id)
    return working

def find_gaps(year, month, grid, data):
    gaps = []
    for pid, proc in data["processes"].items():
        for day in month_days(year, month):
            if not operates_on(proc["operating_rule"], day, data["holidays"]):
                continue
            have = len(workers_on(pid, day, grid, data))
            if have < proc["min_staff"]:
                gaps.append({
                    "date": day.isoformat(),
                    "brand": proc["brand"],
                    "process": proc["name"],
                    "needed": proc["min_staff"],
                    "have": have,
                    "pid": pid,
                })
    return gaps

def split_weeks(year, month):
    weeks = []
    current = []
    for day in month_days(year, month):
        current.append(day)
        if day.weekday() == 6:
            weeks.append(current)
            current = []
    if current:
        weeks.append(current)
    return weeks

def violations_if_off(emp_id, day, grid, data):
    count = 0
    for pid, emps in data["assignments"].items():
        if emp_id not in emps:
            continue
        proc = data["processes"][pid]
        if not operates_on(proc["operating_rule"], day, data["holidays"]):
            continue
        have = len(workers_on(pid, day, grid, data))
        if have - 1 < proc["min_staff"]:
            count += 1
    return count

def assign_weekly_offs(year, month, grid, data):
    for week in split_weeks(year, month):
        if len(week) < 7:
            continue
        for emp_id in data["employees"]:
            row = grid[emp_id]
            if any(row[d.isoformat()] == "OFF" for d in week):
                continue
            best = None
            for day in week:
                if row[day.isoformat()] != "WORK":
                    continue
                v = violations_if_off(emp_id, day, grid, data)
                pref = 0 if data["preferred_offs"].get(emp_id) == day.weekday() else 1
                load = sum(1 for e in grid if grid[e][day.isoformat()] == "WO")
                score = (v, pref, load)
                if best is None or score < best[0]:
                    best = (score, day)
            if best:
                row[best[1].isoformat()] = "WO"

def generate_roster(year, month):
    data = load_data()
    grid = build_grid(year, month, data)
    assign_weekly_offs(year, month, grid, data)
    gaps = find_gaps(year, month, grid, data)
    return data, grid, gaps

STATUS_TEXT = {
    "WO": "on weekly off", "LEAVE": "on planned leave", "COMP": "on comp-off",
    "PH": "on a public holiday", "OFF": "off", "WORK": "working",
}

def explain_gap(gap, grid, data):
    reasons = []
    for emp_id in data["assignments"].get(gap["pid"], []):
        name = data["employees"][emp_id]["name"]
        status = grid[emp_id][gap["date"]]
        reasons.append(name + " is " + STATUS_TEXT[status])
    return(
        gap["brand"] + " " + gap["process"] + " on " + gap["date"]
        + ": needs " + str(gap["needed"]) + ", has " + str(gap["have"]) + ". "
        + "; ".join(reasons) + "."
    )

def gap_cause(gap, grid, data):
    statuses = []
    for emp_id in data["assignments"].get(gap["pid"], []):
        statuses.append(grid[emp_id][gap["date"]])
    if "LEAVE" in statuses or "COMP" in statuses:
        return "Leave"
    if "WO" in statuses:
        return "Weekly off"
    return "No staff available"

def suggest_backups(gap, grid, data, limit=3):
    assigned = data["assignments"].get(gap["pid"], [])
    pods = {data["employees"][e]["pod_id"] for e in assigned}
    day = gap["date"]
    options = []
    for emp_id, emp in data["employees"].items():
        if emp_id in assigned:
            continue
        if grid[emp_id][day] != "WORK":
            continue
        load = 0
        for pid, emps in data["assignments"].items():
            if emp_id in emps:
                rule = data["processes"][pid]["operating_rule"]
                if operates_on(rule, date.fromisoformat(day), data["holidays"]):
                    load += 1
        same_pod = 0 if emp["pod_id"] in pods else 1
        options.append((same_pod, load, emp["name"]))
    options.sort()
    result = []
    for same_pod, load, name in options[:limit]:
        label = name + " (same pod, " if same_pod == 0 else name + " (other pod, "
        result.append(label + str(load) + " processes that day)")
    return result

def add_leave(emp_id, day, kind = "leave"):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO leaves (employee_id, date, kind) VALUES (?, ?, ?)",
        (emp_id, day, kind),
    )
    conn.commit()
    conn.close()

def remove_leave(emp_id, day):
    conn = get_conn()
    conn.execute("DELETE FROM leaves WHERE employee_id = ? AND date = ?", (emp_id, day))
    conn.commit()
    conn.close()

def new_gaps(before, after):
    seen = {(g["date"], g["pid"]) for g in before}
    return [g for g in after if (g["date"], g["pid"]) not in seen]

def add_assignment(emp_id, process_id):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO assignments (employee_id, process_id) VALUES (?, ?)",
        (emp_id, process_id),
    )
    conn.commit()
    conn.close()

def remove_assignment(emp_id, process_id):
    conn = get_conn()
    conn.execute(
        "DELETE FROM assignments WHERE employee_id = ? AND process_id = ?",
        (emp_id, process_id),
    )
    conn.commit()
    conn.close()    
