---
name: sqlite-ops-mirror
description: When Alec asks about projects, jobs, tasks, time entries, or materials -- query this local SQLite DB immediately. Do not say "I'd need to check" -- just check it. This is the default source for ops reads. Covers Projects (all electrical jobs/customers), Tasks, Time Log, and Material Lists.
---

# SQLite Ops Mirror

DB: `/home/node/.openclaw/workspace/ops_mirror.db`
Tool: `python3 /home/node/.openclaw/workspace/query_mirror.py "<SQL>"`

"Projects" = electrical contracting jobs, not software projects.

## Named queries -- use these directly

    # Ongoing jobs
    python3 /home/node/.openclaw/workspace/query_mirror.py "SELECT name, project_code, labor_rate FROM projects WHERE status='Ongoing' ORDER BY name"

    # Recent time entries
    python3 /home/node/.openclaw/workspace/query_mirror.py "SELECT tl.date_from_ci, tl.duration, tl.description, p.name AS job FROM time_log tl, json_each(tl.project) je JOIN projects p ON je.value=p.airtable_id ORDER BY tl.clock_in DESC LIMIT 20"

    # Open tasks
    python3 /home/node/.openclaw/workspace/query_mirror.py "SELECT name, project, due, priority FROM tasks WHERE due IS NOT NULL ORDER BY due"

    # Material lists for a job (replace %term%)
    python3 /home/node/.openclaw/workspace/query_mirror.py "SELECT ml.name, ml.qty, ml.purchased FROM material_lists ml, json_each(ml.project) je JOIN projects p ON je.value=p.airtable_id WHERE p.name LIKE '%term%'"

    # DB freshness
    python3 /home/node/.openclaw/workspace/query_mirror.py freshness

## Schema (key columns only)

projects: airtable_id, name, status, project_code, customer (JSON IDs), labor_rate, auto_id
tasks: airtable_id, name, description, project (text), due, priority
time_log: airtable_id, project (JSON IDs), description, clock_in, clock_out, duration, approved, date_from_ci
material_lists: airtable_id, name, field_entry, qty, project (JSON IDs), purchased

Linked fields (customer, project) are JSON arrays of Airtable record IDs -- join with json_each().

## Return format

- Jobs/tasks: bullet list, name + relevant detail
- Time entries: table with date, duration, job, description
- Counts/totals: single line
- Always show freshness timestamp if data staleness could matter

## Limits

Writes go to Airtable API, not this DB. Tables not mirrored: Customers, Purchased Items, BEL, Receipts, Vendors, Estimates.
