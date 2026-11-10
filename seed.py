from db import get_conn,init_db

PODS = ["Pod Alpha", "Pod Beta", "Pod Gamma", "Pod Delta", "Pod Omega"]

EMPLOYEES = [
    ("Aarav Mehta", "Pod Alpha", 1), ("Priya Nair", "Pod Alpha", 0),
    ("Rohan Desai", "Pod Alpha", 0), ("Sneha Kulkarni", "Pod Alpha", 0),
    ("Imran Shaikh", "Pod Alpha", 0), ("Neha Verma", "Pod Alpha", 0),
    ("Karan Joshi", "Pod Alpha", 0),
    ("Kavya Iyer", "Pod Beta", 1), ("Arjun Patil", "Pod Beta", 0),
    ("Pooja Singh", "Pod Beta", 0), ("Vikram Rao", "Pod Beta", 0),
    ("Ananya Das", "Pod Beta", 0), ("Farhan Qureshi", "Pod Beta", 0),
    ("Meera Pillai", "Pod Beta", 0),
    ("Rahul Sharma", "Pod Gamma", 1), ("Divya Menon", "Pod Gamma", 0),
    ("Sahil Khan", "Pod Gamma", 0), ("Ritu Agarwal", "Pod Gamma", 0),
    ("Nikhil Gupta", "Pod Gamma", 0), ("Tanvi Bhatt", "Pod Gamma", 0),
    ("Zoya Ansari", "Pod Delta", 1), ("Amit Chavan", "Pod Delta", 0),
    ("Shruti Naik", "Pod Delta", 0), ("Harsh Vora", "Pod Delta", 0),
    ("Lakshmi Reddy", "Pod Delta", 0), ("Yash Thakur", "Pod Delta", 0),
    ("Deepak Yadav", "Pod Omega", 1), ("Isha Kapoor", "Pod Omega", 0),
    ("Manish Pandey", "Pod Omega", 0), ("Sana Siddiqui", "Pod Omega", 0),
    ("Varun Malhotra", "Pod Omega", 0), ("Pallavi Jadhav", "Pod Omega", 0),
]

def seed_people():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if count > 0:
        print("Employees already exist, skipping.")
        conn.close()
        return
    for pod in PODS:
        conn.execute("INSERT OR IGNORE INTO pods (name) VALUES (?)", (pod,))
    for name, pod, is_lead in EMPLOYEES:
        row = conn.execute("SELECT id FROM pods WHERE name = ?", (pod,)).fetchone()
        conn.execute(
            "INSERT INTO employees (name, pod_id, is_pod_lead) VALUES (?, ?, ?)",
            (name, row["id"], is_lead),
        )
    conn.commit()
    conn.close()

BRANDS = [
    ("Glowvia", [("CS", "365", 1), ("ACC", "except_holidays", 1)]),
    ("UrbanLeaf", [("CS", "except_holidays", 1), ("NDR", "except_sundays_holidays", 1)]),
    ("KiddoCart", [("CS", "365", 1)]),
    ("NutriNest", [("CS", "except_holidays", 1), ("ACC", "except_holidays", 1), ("NDR", "except_sundays_holidays", 1)]),
    ("ThreadHouse", [("CS", "except_sundays_holidays", 1)]),
    ("PureBrew", [("CS", "365", 1), ("Retention", "except_holidays", 1)]),
    ("Zenwear", [("CS", "except_holidays", 1)]),
    ("PetPal", [("CS", "except_holidays", 1), ("ACC", "except_sundays_holidays", 1)]),
    ("BloomSkin", [("CS", "365", 1)]),
    ("GadgetGo", [("CS", "except_holidays", 1), ("NDR", "except_holidays", 1)]),
    ("HomeNest", [("CS", "except_sundays_holidays", 1), ("ACC", "except_sundays_holidays", 1)]),
    ("FitFuel", [("CS", "except_holidays", 1)]),
    ("SilkRoute", [("CS", "except_sundays_holidays", 1), ("NDR", "except_sundays_holidays", 1)]),
    ("AromaStudio", [("CS", "except_holidays", 1)]),
    ("TrailMate", [("CS", "365", 1)]),
    ("CraftCorner", [("CS", "except_holidays", 1), ("Retention", "except_sundays_holidays", 1)]),
    # multi-employee brands
    ("Velora", [("CS", "365", 1), ("ACC", "except_holidays", 1), ("NDR", "except_sundays_holidays", 1)]),
    ("StyleStreet", [("CS", "365", 1), ("ACC", "except_holidays", 1), ("Retention", "except_sundays_holidays", 1)]),
    ("MediGlow", [("CS", "except_holidays", 2), ("NDR", "except_holidays", 1)]),
    ("UrbanKitchen", [("CS", "365", 1), ("ACC", "except_holidays", 1)]),
]

def seed_brands():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    if count > 0:
        print("Brands already exist, skipping.")
        conn.close()
        return
    for brand, processes in BRANDS:
        cur = conn.execute("INSERT INTO brands (name) VALUES (?)", (brand,))
        brand_id = cur.lastrowid
        for pname, rule, min_staff in processes:
            conn.execute(
                "INSERT INTO processes (brand_id, name, operating_rule, min_staff) VALUES (?, ?, ?, ?)",
                (brand_id, pname, rule, min_staff),
            )
    conn.commit()
    conn.close()

SINGLE_BRANDS = {
    "Glowvia": "Priya Nair", "UrbanLeaf": "Rohan Desai",
    "KiddoCart": "Sneha Kulkarni", "NutriNest": "Imran Shaikh",
    "ThreadHouse": "Neha Verma", "PureBrew": "Karan Joshi",
    "Zenwear": "Arjun Patil", "PetPal": "Pooja Singh",
    "BloomSkin": "Vikram Rao", "GadgetGo": "Ananya Das",
    "HomeNest": "Farhan Qureshi", "FitFuel": "Meera Pillai",
    "SilkRoute": "Divya Menon", "AromaStudio": "Sahil Khan",
    "TrailMate": "Ritu Agarwal", "CraftCorner": "Nikhil Gupta",
}

EXTRA_ASSIGNMENTS = [
    # multi-employee brands
    ("Velora", "CS", ["Tanvi Bhatt"]),
    ("Velora", "ACC", ["Amit Chavan"]),
    ("Velora", "NDR", ["Shruti Naik"]),
    ("StyleStreet", "CS", ["Harsh Vora"]),
    ("StyleStreet", "ACC", ["Lakshmi Reddy", "Yash Thakur"]),
    ("StyleStreet", "Retention", ["Yash Thakur"]),
    ("MediGlow", "CS", ["Isha Kapoor", "Manish Pandey"]),
    ("MediGlow", "NDR", ["Sana Siddiqui"]),
    ("UrbanKitchen", "CS", ["Varun Malhotra"]),
    ("UrbanKitchen", "ACC", ["Pallavi Jadhav"]),
    # backups for 365-day single-person brands
    ("Glowvia", "CS", ["Aarav Mehta"]),
    ("KiddoCart", "CS", ["Aarav Mehta"]),
    ("PureBrew", "CS", ["Kavya Iyer"]),
    ("BloomSkin", "CS", ["Kavya Iyer"]),
    ("TrailMate", "CS", ["Rahul Sharma"]),
]

def seed_assignments():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
    if count > 0:
        print("Assignments already exist, skipping.")
        conn.close()
        return

    def add(emp_name, brand, process):
        emp = conn.execute(
            "SELECT id FROM employees WHERE name = ?", (emp_name,)
        ).fetchone()
        proc = conn.execute(
            "SELECT p.id FROM processes p JOIN brands b ON b.id = p.brand_id "
            "WHERE b.name = ? AND p.name = ?", (brand, process)
        ).fetchone()
        if emp is None or proc is None:
            print("NOT FOUND:", emp_name, brand, process)
            return
        conn.execute(
            "INSERT OR IGNORE INTO assignments (employee_id, process_id) VALUES (?, ?)",
            (emp["id"], proc["id"]),
        )
    
    for brand, emp_name in SINGLE_BRANDS.items():
        rows = conn.execute(
            "SELECT p.name FROM processes p JOIN brands b ON b.id = p.brand_id "
            "WHERE b.name = ?", (brand,)
        ).fetchall()
        for r in rows:
            add(emp_name, brand, r["name"])

    for brand, process, emps in EXTRA_ASSIGNMENTS:
        for emp_name in emps:
            add(emp_name, brand, process)

    conn.commit()
    conn.close()

HOLIDAYS = [
    ("2026-11-10", "Diwali Padwa"),
    ("2026-11-24", "Guru Nanak Jayanti"),
    ("2026-12-25", "Christmas"),
]

PREFERRED_OFFS = {
    "Priya Nair": 6, "Rohan Desai": 6, "Imran Shaikh": 2,
    "Neha Verma": 0, "Arjun Patil": 6, "Pooja Singh": 4,
    "Ananya Das": 6, "Meera Pillai": 1, "Divya Menon": 6,
    "Tanvi Bhatt": 3, "Harsh Vora": 6, "Isha Kapoor": 2,
}

LEAVES = [
    ("Priya Nair", "2026-11-16", "leave"),
    ("Arjun Patil", "2026-11-17", "leave"),
    ("Imran Shaikh", "2026-11-19", "leave"),
    ("Isha Kapoor", "2026-11-12", "leave"),
    ("Karan Joshi", "2026-11-26", "comp_off"),
    ("Tanvi Bhatt", "2026-11-20", "leave"),
]

def seed_calander():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM holidays").fetchone()[0]
    if count > 0:
        print("Calendar data already exists, skipping.")
        conn.close()
        return
    def emp_id(name):
        return conn.execute(
            "SELECT id FROM employees WHERE name = ?", (name,)
        ).fetchone()["id"]
    for date, name in HOLIDAYS:
        conn.execute("INSERT INTO holidays (date, name) VALUES (?, ?)", (date, name))
    for name, weekday in PREFERRED_OFFS.items():
        conn.execute(
            "INSERT INTO preferred_offs (employee_id, weekday) VALUES (?, ?)",
            (emp_id(name), weekday),
        )
    for name, date, kind in LEAVES:
        conn.execute(
            "INSERT INTO leaves (employee_id, date, kind) VALUES (?, ?, ?)",
            (emp_id(name), date, kind),
        )
    conn.commit()
    conn.close()

def seed_all():
    init_db()
    seed_people()
    seed_brands()
    seed_assignments()
    seed_calander()

if __name__ == "__main__":
    init_db()
    seed_people()
    seed_brands()
    seed_calander()
    seed_assignments()
    print("Done")