from flask import Flask, render_template, request, redirect, url_for
from roster_logic import generate_roster, month_days, explain_gap, gap_cause, suggest_backups, add_leave, add_assignment, remove_assignment
from db import init_db, get_conn
from seed import seed_all

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/roster")
@app.route("/roster")
def roster():
    year = request.args.get("year", 2026, type=int)
    month = request.args.get("month", 11, type=int)
    data, grid, gaps = generate_roster(year, month)

    pod = request.args.get("pod", type=int)
    brand = request.args.get("brand", "")
    process = request.args.get("process", type=int)
    employee = request.args.get("employee", type=int)

    pods = get_conn().execute("SELECT id, name FROM pods").fetchall()
    brands = sorted({p["brand"] for p in data["processes"].values()})
    process_list = sorted(data["processes"].items(), key=lambda x: (x[1]["brand"], x[1]["name"]))
    all_employees = list(data["employees"].values())

    employees = all_employees
    if pod:
        employees = [e for e in employees if e["pod_id"] == pod]
    if brand:
        ids = set()
        for pid, emps in data["assignments"].items():
            if data["processes"][pid]["brand"] == brand:
                ids.update(emps)
        employees = [e for e in employees if e["id"] in ids]
        gaps = [g for g in gaps if g["brand"] == brand]
    if process:
        employees = [e for e in employees if e["id"] in data["assignments"].get(process, [])]
        gaps = [g for g in gaps if g["pid"] == process]
    if employee:
        employees = [e for e in employees if e["id"] == employee]
        gaps = [g for g in gaps if employee in data["assignments"].get(g["pid"], [])]

    conflicts = []
    for gap in gaps:
        conflicts.append({
            "text": explain_gap(gap, grid, data),
            "cause": gap_cause(gap, grid, data),
            "backups": suggest_backups(gap, grid, data),
        })

    return render_template(
        "roster.html", year=year, month=month, gap_count=len(gaps),
        days=month_days(year, month),
        employees=employees, all_employees=all_employees,
        pods=pods, pod=pod, brands=brands, brand=brand,
        process_list=process_list, process=process, employee=employee,
        grid=grid, conflicts=conflicts,
    )

@app.route("/add-leave", methods=["POST"])
def add_leave_route():
    emp_id = request.form.get("employee_id", type=int)
    day = request.form.get("date")
    kind = request.form.get("kind", "leave")
    if emp_id and day:
        add_leave(emp_id, day, kind)
        year, month = int(day[:4]), int(day[5:7])
        return redirect(url_for("roster", year=year, month=month))
    return redirect(url_for("roster"))

@app.route("/assign", methods=["POST"])
def assign_route():
    emp_id = request.form.get("employee_id", type=int)
    process_id = request.form.get("process_id", type=int)
    action = request.form.get("action")
    if emp_id and process_id:
        if action == "add":
            add_assignment(emp_id, process_id)
        elif action == "remove":
            remove_assignment(emp_id, process_id)
    return redirect(url_for("roster"))

seed_all()

if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False)
