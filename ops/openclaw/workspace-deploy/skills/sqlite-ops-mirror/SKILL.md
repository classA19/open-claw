---
name: sqlite-ops-mirror
description: When Alec asks about projects, jobs, tasks, time entries, or materials -- query this local SQLite DB immediately. Do not say "I'd need to check" -- just check it. This is the default source for ops reads. Covers Projects (all electrical jobs/customers), Tasks, Time Log, and Material Lists.
---

# SQLite Ops Mirror

A local SQLite database mirrors four Airtable tables from the Operations base. It syncs every hour via cron. **When Alec asks about projects, jobs, time, tasks, or materials -- query this DB immediately. Do not ask permission or hedge. Just run the query and show results.**

"Projects" in this context means Alec's electrical contracting jobs (customers, job sites), not his software/automation projects.

## Query tool

    python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py "<SQL>"

### Built-in commands

    # List all tables and record counts
    python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py tables

    # Show column names for a table
    python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py schema projects

    # Check when each table was last synced
    python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py freshness

## Common queries

    -- Ongoing projects
    SELECT name, project_code FROM projects WHERE status = 'Ongoing' ORDER BY name;

    -- Recent time entries
    SELECT tl.clock_in, tl.duration, p.name AS project
    FROM time_log tl, json_each(tl.project) je
    JOIN projects p ON je.value = p.airtable_id
    ORDER BY tl.clock_in DESC LIMIT 10;

    -- Tasks by priority
    SELECT name, project, due, priority FROM tasks ORDER BY due;

    -- Material lists for a project
    SELECT ml.name, ml.qty, ml.purchased
    FROM material_lists ml, json_each(ml.project) je
    JOIN projects p ON je.value = p.airtable_id
    WHERE p.name LIKE '%search_term%';

## Database location

    ~/open-claw/ops/openclaw/data/ops_mirror.db

## Schema

### projects
airtable_id (PK), name, status, project_code, customer (JSON array of record IDs), descriptors (JSON array), last_modified, created, rate_name (JSON array of record IDs), labor_rate, auto_id, record_id

### tasks
airtable_id (PK), name, description, date_created, project (plain text), due, priority

### time_log
airtable_id (PK), name, project (JSON array of record IDs), description, clock_in, clock_out, duration, approved (0/1), date_from_ci

### material_lists
airtable_id (PK), name, field_entry, common_mats (JSON array of record IDs), qty, project (JSON array of record IDs), purchased

## Linked record joins

Use json_each() to resolve linked record IDs:

    SELECT tl.clock_in, tl.duration, p.name AS project_name
    FROM time_log tl, json_each(tl.project) je
    JOIN projects p ON je.value = p.airtable_id;

## When NOT to use this skill

- **Writing** data -- use Airtable API directly
- Tables **not in the mirror**: Customers, Purchased Items, Billable Expense Log, Receipts, Vendors, Estimates
- When freshness matters and something just changed -- run a manual sync first: python3 ~/open-claw/ops/openclaw/scripts/airtable_mirror.py

## Relationship to other skills

- **airtable-project-ops**: handles project writes. This skill handles project reads.
- **field-task-orchestrator**: handles task creation. This skill looks up existing tasks.
