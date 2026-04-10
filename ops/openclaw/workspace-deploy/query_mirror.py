#!/usr/bin/env python3
"""Query the local SQLite ops mirror.

Usage:
    python3 query_mirror.py "SELECT name, status FROM projects WHERE status = 'Ongoing'"
    python3 query_mirror.py tables
    python3 query_mirror.py schema projects
    python3 query_mirror.py freshness
"""

import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "ops_mirror.db"


def run_query(sql):
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(sql).fetchall()
        results = [dict(r) for r in rows]
        print(json.dumps(results, indent=2, default=str))
        print(f"\n({len(results)} rows)")


def show_tables():
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as db:
        rows = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        for r in rows:
            count = db.execute(f"SELECT COUNT(*) FROM [{r[0]}]").fetchone()[0]
            print(f"  {r[0]}: {count} records")


def show_schema(table):
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as db:
        rows = db.execute(f"PRAGMA table_info([{table}])").fetchall()
        if not rows:
            print(f"Table '{table}' not found")
            return
        print(f"{table}:")
        for r in rows:
            print(f"  {r[1]} ({r[2]})")


def show_freshness():
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as db:
        rows = db.execute("SELECT * FROM _sync_meta ORDER BY table_name").fetchall()
        for r in rows:
            print(f"  {r[0]}: {r[2]} records, synced {r[1]}")


def main():
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH}")
        sys.exit(1)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "tables":
        show_tables()
    elif cmd == "schema":
        table = sys.argv[2] if len(sys.argv) > 2 else None
        if not table:
            print("Usage: query_mirror.py schema <table_name>")
            sys.exit(1)
        show_schema(table)
    elif cmd == "freshness":
        show_freshness()
    else:
        run_query(cmd)


if __name__ == "__main__":
    main()
