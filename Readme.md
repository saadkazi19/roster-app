# Smart Roster Management System

A browser-based tool to plan, generate and validate monthly rosters for employees across multiple brands, processes and pods.

**Live app:** https://roster-app-vue6.onrender.com/
(The first load can take about a minute, because the free host puts the app to sleep when idle.)

## What it does

- Generates a monthly roster for 32 employees, 5 pods, 20 brands and 36 processes
- Respects each process's operating calendar, public holidays, planned leaves, comp-offs and minimum staffing
- Finds coverage gaps, labels the cause (leave or weekly off), explains it in plain English and suggests backups
- Views by company, pod, brand, process and employee (filters on the roster page)
- Add a leave or comp-off, and the roster and gaps regenerate
- Assign or unassign an employee to a process without touching code

## Tech stack

Python, Flask, SQLite, HTML and CSS. Deployed on Render with gunicorn.

## Run locally

1. Create and activate a virtual environment: `python -m venv venv`, then `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
2. Install the libraries: `pip install -r requirements.txt`
3. Start the app: `python app.py`
4. Open http://127.0.0.1:5000

The database (`roster.db`) is created and filled with sample data automatically on the first start. No `.env` file is needed, so there is no `.env.example`.

## Project files

- `db.py`: database tables
- `seed.py`: sample data (pods, employees, brands, processes, assignments, holidays, leaves)
- `roster_logic.py`: scheduling and validation logic
- `app.py`: Flask routes
- `templates/` and `static/`: HTML pages and CSS

## Assumptions

- Each process has one operating rule: `365` (every day), `except_holidays`, or `except_sundays_holidays`. The rule belongs to the process, so one brand can mix different schedules.
- A brand's operating calendar is separate from an employee's schedule: the calendar decides whether work exists, and the employee's leaves and weekly offs decide who can do it.
- Weeks run Monday to Sunday. Each full week gives every employee one weekly off. Partial weeks at the start or end of a month get none.
- An employee whose processes are all closed on a day (for example a Sunday) already has that day as a rest day, so no extra weekly off is given that week.
- Pod leads in the sample data have no processes assigned, so their rows show OFF. A pod lead with processes would be scheduled like anyone else.
- The five 365-day single-person brands have a pod lead as a backup, so their main person can take a weekly off.
- Backup suggestions prefer someone in the same pod who is working that day, and then the lightest workload.
- Public holidays and employee preferences in the sample data are fictional.
- On the free host, the database resets when the app restarts, and the sample data is rebuilt each time. Leaves added on the live site don't last.


## Tell us how you think

### 1. How did you model employees, brands, processes, pods and their relationships?

Each thing has its own table: pods, employees, brands, processes, holidays and leaves. A brand is just a name, and the real work sits in its **processes**, each with its own working rule and minimum staff. An `assignments` table links employees to processes, so one person can cover a whole brand or several people can share one. Coverage is not stored. It is worked out each time.

### 2. How does your system generate a roster and check the constraints?

It gives every employee a status for every day (working, leave, holiday, or off). Then it adds one weekly off per week, choosing the day that leaves the fewest processes uncovered, and using the employee's preferred day only as a tie-breaker. Finally it checks every process on every operating day, and records a gap when fewer people are working than the minimum.

### 3. How did you handle single-resource brands versus brands with multiple employees?

Both use the same tables, and only the data differs. A single-resource brand has one person assigned to all its processes (16 of my 20 brands). A multi-employee brand splits the processes between people, and some need two. Pod leads act as backups on the 365-day single-person brands.

### 4. What happens when an employee who manages all processes for a brand is unavailable on a required working day?

The roster regenerates and each affected process shows a gap, with the cause and the person's name. The app suggests up to three backups (working that day, same pod first). The manager picks one with the Assign form, and the gap closes.



### 5. How does your system handle conflicting requirements or insufficient staffing?

It never hides a problem. If a process has too few people working, the roster is still shown, and that day appears in the conflicts table with the cause (leave or weekly off) and the people involved. Required coverage always beats a preferred weekly off. When coverage can't be met, the app flags it and suggests backups.

### 6. Which parts did you automate, and which did you leave under human control? Why?

Automated: daily statuses, weekly offs, finding gaps, explaining them, suggesting backups, and regenerating the roster after a change. Left to the manager: approving leaves, choosing which backup to use, and changing assignments. These depend on things the app can't know, so it suggests and the person decides.

### 7. If the company doubled its team and brand count, what would you change?

I would move from SQLite to a hosted database like PostgreSQL, save each month's roster instead of recalculating it every time, use an optimisation solver for the weekly offs, and add logins for pod leads and managers.

### 8. If you had one additional week, what would you improve first?

Screens to add and edit brands, processes, holidays and working rules, because right now only leaves and assignments can be changed from the page. Then smarter weekly offs for single-person brands, so fewer gaps appear, followed by saved rosters, a pod lead approval step and CSV export.