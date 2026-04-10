---
name: sqlite-ops-mirror
description: Query the local SQLite mirror of Airtable ops data for fast reads. Use this instead of Airtable API calls when reading Projects, Tasks, Time Log, or Material Lists. The mirror syncs hourly via cron. Use Airtable API directly only for writes or for tables not in the mirror.
---

# SQLite Ops Mirror

A local SQLite database mirrors four Airtable tables from the Operations base. It syncs every hour via cron. **Use this for all read queries against these tables instead of calling the Airtable API.**

## When to use this skill

- Looking up project names, statuses, or codes
- Querying the time log (recent entries, totals, filtering by project)
- Checking tasks and their priorities/due dates
- Viewing material lists for a project
- Any read-only query against Projects, Tasks, Time Log, or Material Lists

## When NOT to use this skill

- **Writing** data (creating/updating records) — use Airtable API directly
- Querying tables **not in the mirror**: Customers, Purchased Items, Billable Expense Log, Receipts, Vendors, Estimates, etc.
- When you need data that changed **in the last hour** and freshness is critical — check freshness first, or query Airtable directly

## Query tool

```bash
python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py "<SQL>"
```

### Built-in commands

```bash
# List all tables and record counts
python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py tables

# Show column names for a table
python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py schema projects

# Check when each table was last synced
python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py freshness
```

## Database location

```
~/open-claw/ops/openclaw/data/ops_mirror.db
```

## Schema

### projects
| Column | Type | Source |
|--------|------|--------|
| airtable_id | TEXT (PK) | record ID |
| name | TEXT | project name |
| status | TEXT | singleSelect: Ongoing, Closed, Quoted, etc. |
| project_code | TEXT | formula |
| customer | TEXT | JSON array of record IDs |
| descriptors | TEXT | JSON array of strings |
| last_modified | TEXT | timestamp |
| created | TEXT | timestamp |
| rate_name | TEXT | JSON array of record IDs |
| labor_rate | TEXT | formula |
| auto_id | INTEGER | autoNumber |
| record_id | TEXT | formula |

### tasks
| Column | Type | Source |
|--------|------|--------|
| airtable_id | TEXT (PK) | record ID |
| name | TEXT | task name |
| description | TEXT | details |
| date_created | TEXT | date |
| project | TEXT | plain text (not linked) |
| due | TEXT | date |
| priority | TEXT | singleSelect |

### time_log
| Column | Type | Source |
|--------|------|--------|
| airtable_id | TEXT (PK) | record ID |
| name | TEXT | formula |
| project | TEXT | JSON array of record IDs |
| description | TEXT | work description |
| clock_in | TEXT | dateTime |
| clock_out | TEXT | dateTime |
| duration | TEXT | formula |
| approved | INTEGER | 0/1 |
| date_from_ci | TEXT | formula (date only) |

### material_lists
| Column | Type | Source |
|--------|------|--------|
| airtable_id | TEXT (PK) | record ID |
| name | TEXT | formula |
| field_entry | TEXT | raw field input |
| common_mats | TEXT | JSON array of record IDs |
| qty | REAL | number |
| project | TEXT | JSON array of record IDs |
| purchased | TEXT | singleSelect |

## Linked record joins

Customer and project links are stored as JSON arrays of Airtable record IDs. To resolve them, use SQLite's `json_each()`:

```sql
-- Get project names for time log entries
SELECT tl.clock_in, tl.duration, p.name AS project_name
FROM time_log tl, json_each(tl.project) je
JOIN projects p ON je.value = p.airtable_id
ORDER BY tl.clock_in DESC;

-- Get all material lists for a specific project
SELECT ml.name, ml.qty, ml.purchased
FROM material_lists ml, json_each(ml.project) je
JOIN projects p ON je.value = p.airtable_id
WHERE p.name LIKE '%Ranch%';
```

## Freshness

Data is at most ~1 hour stale. Always check freshness if the user asks about something that just changed:

```bash
python3 ~/open-claw/ops/openclaw/scripts/query_mirror.py freshness
```

If the data is too stale, trigger a manual sync:

```bash
python3 ~/open-claw/ops/openclaw/scripts/airtable_mirror.py
```

## Relationship to other skills

- **airtable-project-ops**: That skill handles project writes (create, update, relink). This skill handles project reads. Use this for lookups, use that for mutations.
- **field-task-orchestrator**: That skill handles task creation/orchestration. This skill can quickly look up existing tasks.
