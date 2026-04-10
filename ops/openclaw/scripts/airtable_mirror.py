#!/usr/bin/env python3
"""Airtable -> SQLite read-only mirror for OpenClaw ops data.

Syncs Projects, Tasks, Time Log, and Material Lists from the
Airtable Operations base into a local SQLite database for fast reads.
Designed to run via cron on the VPS.
"""

import json
import logging
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pyairtable import Api

# ── Config ─────────────────────────────────────────────────────

BASE_ID = "appfa63VIz7mjwNHe"
DB_PATH = Path(__file__).resolve().parent.parent / "workspace" / "ops_mirror.db"

# ── Coercion helpers ───────────────────────────────────────────

def _text(v):
    return str(v) if v is not None else None

def _number(v):
    return v if isinstance(v, (int, float)) else None

def _select(v):
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return v.get("name")
    return None

def _multi_select(v):
    if not isinstance(v, list):
        return None
    return json.dumps([x["name"] if isinstance(x, dict) else x for x in v])

def _linked(v):
    if not isinstance(v, list):
        return None
    return json.dumps(v)

def _checkbox(v):
    return 1 if v else 0

COERCERS = {
    "text": _text,
    "number": _number,
    "select": _select,
    "multi_select": _multi_select,
    "linked": _linked,
    "checkbox": _checkbox,
}

# ── Table configs ──────────────────────────────────────────────
# Each field tuple: (airtable_field_id, sqlite_column, coerce_type)

TABLE_CONFIGS = [
    {
        "airtable_table_id": "tblDV2R7ng7OL4kLj",
        "sqlite_table": "projects",
        "fields": [
            ("fldfbYUO8v3YTufZZ", "name", "text"),
            ("fldaF4cJP7hM1Aq14", "status", "select"),
            ("fldfnFFK2qFDtw5Gy", "project_code", "text"),
            ("fldnO0BlD6emnU6Ym", "customer", "linked"),
            ("fldEnzrYlnwVLGROd", "descriptors", "multi_select"),
            ("fld7VfIGKg9TDFtmK", "last_modified", "text"),
            ("fldgNqfsFJyL7j1CB", "created", "text"),
            ("fldZLDODT79pPZNAy", "rate_name", "linked"),
            ("fldmMp4rFZBuPz4ve", "labor_rate", "text"),
            ("fld0BKS0vyuwR1A1u", "auto_id", "number"),
            ("fld9ByYaWPnbpd19I", "record_id", "text"),
        ],
    },
    {
        "airtable_table_id": "tblVuX72HUTsG2agQ",
        "sqlite_table": "tasks",
        "fields": [
            ("fldGxSbCw8LRhN1BR", "name", "text"),
            ("fldkSxoEXuBElvv4n", "description", "text"),
            ("fldTnsAxA7g4Gnfvy", "date_created", "text"),
            ("fldXWLPWf5D8tHrhg", "project", "text"),
            ("fldJtHHF8jYRLWg60", "due", "text"),
            ("fldzJRe4nglXkKi2M", "priority", "select"),
        ],
    },
    {
        "airtable_table_id": "tblzp7AGiI32RUEMf",
        "sqlite_table": "time_log",
        "fields": [
            ("fld8NY9G3E08O3NbX", "name", "text"),
            ("fldor9BbnYMUqClg5", "project", "linked"),
            ("fldoNmiTvI4thM9Ie", "description", "text"),
            ("fldi4M4ftKjs0yoGK", "clock_in", "text"),
            ("fldQuSxZP1MZc6xDd", "clock_out", "text"),
            ("fldJ4TszP8NfNz4KK", "duration", "text"),
            ("fldI6CCQPCRJwim5v", "approved", "checkbox"),
            ("fldEm2T5aXKvb6LKR", "date_from_ci", "text"),
        ],
    },
    {
        "airtable_table_id": "tblRFab8AYPnemPnE",
        "sqlite_table": "material_lists",
        "fields": [
            ("fldzNZmHyCISB8thI", "name", "text"),
            ("fldkswaGMMTvnAUwN", "field_entry", "text"),
            ("fld5sl0uZnqwwiTyJ", "common_mats", "linked"),
            ("fldybs3FSTA0cIcOH", "qty", "number"),
            ("fldoPTi7N3qnZs26V", "project", "linked"),
            ("fldULfNV7LUbIUrZd", "purchased", "select"),
        ],
    },
]

# ── SQLite schema ──────────────────────────────────────────────

SCHEMAS = {
    "projects": """
        CREATE TABLE IF NOT EXISTS projects (
            airtable_id   TEXT PRIMARY KEY,
            name          TEXT,
            status        TEXT,
            project_code  TEXT,
            customer      TEXT,
            descriptors   TEXT,
            last_modified TEXT,
            created       TEXT,
            rate_name     TEXT,
            labor_rate    TEXT,
            auto_id       INTEGER,
            record_id     TEXT
        )
    """,
    "tasks": """
        CREATE TABLE IF NOT EXISTS tasks (
            airtable_id   TEXT PRIMARY KEY,
            name          TEXT,
            description   TEXT,
            date_created  TEXT,
            project       TEXT,
            due           TEXT,
            priority      TEXT
        )
    """,
    "time_log": """
        CREATE TABLE IF NOT EXISTS time_log (
            airtable_id   TEXT PRIMARY KEY,
            name          TEXT,
            project       TEXT,
            description   TEXT,
            clock_in      TEXT,
            clock_out     TEXT,
            duration      TEXT,
            approved      INTEGER,
            date_from_ci  TEXT
        )
    """,
    "material_lists": """
        CREATE TABLE IF NOT EXISTS material_lists (
            airtable_id   TEXT PRIMARY KEY,
            name          TEXT,
            field_entry   TEXT,
            common_mats   TEXT,
            qty           REAL,
            project       TEXT,
            purchased     TEXT
        )
    """,
    "_sync_meta": """
        CREATE TABLE IF NOT EXISTS _sync_meta (
            table_name    TEXT PRIMARY KEY,
            synced_at     TEXT,
            record_count  INTEGER
        )
    """,
}

# ── Sync logic ─────────────────────────────────────────────────

def create_all_tables(db):
    for ddl in SCHEMAS.values():
        db.execute(ddl)

def sync_table(api, db, config):
    table = api.table(BASE_ID, config["airtable_table_id"])
    records = table.all(use_field_ids=True)

    sqlite_table = config["sqlite_table"]
    columns = ["airtable_id"] + [f[1] for f in config["fields"]]
    placeholders = ", ".join(["?"] * len(columns))

    db.execute(f"DELETE FROM {sqlite_table}")

    rows = []
    for rec in records:
        row = [rec["id"]]
        fields = rec.get("fields", {})
        for fld_id, _col, coerce_type in config["fields"]:
            raw = fields.get(fld_id)
            row.append(COERCERS[coerce_type](raw))
        rows.append(tuple(row))

    col_str = ", ".join(columns)
    db.executemany(f"INSERT INTO {sqlite_table} ({col_str}) VALUES ({placeholders})", rows)

    db.execute(
        "INSERT OR REPLACE INTO _sync_meta (table_name, synced_at, record_count) VALUES (?, ?, ?)",
        (sqlite_table, datetime.now(timezone.utc).isoformat(), len(rows)),
    )

    logging.info("  %s: %d records", sqlite_table, len(rows))

# ── Main ───────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    pat = os.environ.get("AIRTABLE_PAT")
    if not pat:
        logging.error("AIRTABLE_PAT not set in environment or .env")
        sys.exit(1)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    api = Api(pat)

    logging.info("Syncing Airtable -> %s", DB_PATH)

    with sqlite3.connect(DB_PATH) as db:
        db.execute("PRAGMA journal_mode=WAL")
        create_all_tables(db)
        for config in TABLE_CONFIGS:
            sync_table(api, db, config)
        db.commit()

    logging.info("Sync complete")

if __name__ == "__main__":
    main()
