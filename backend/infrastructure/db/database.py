import sqlite3
from pathlib import Path
import os

DB_PATH = Path(os.getenv("DB_PATH", "aurumai.db"))


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with required tables"""
    conn = get_connection()
    cur = conn.cursor()

    # Machines table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT UNIQUE NOT NULL,
            machine_type TEXT NOT NULL,
            site TEXT NOT NULL,
            status TEXT DEFAULT 'operational',
            commissioned_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Raw measurements table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metric_key TEXT NOT NULL,
            metric_value REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
        )
    """
    )

    # Index for time-based queries
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_raw_measurements_timestamp
        ON raw_measurements(timestamp DESC)
    """
    )

    # Features table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            feature_key TEXT NOT NULL,
            feature_value REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
        )
    """
    )

    # Predictions table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            risk_score REAL NOT NULL,
            failure_probability REAL NOT NULL,
            confidence REAL DEFAULT 0.85,
            next_maintenance_hours INTEGER,
            co2eq_instant REAL NOT NULL,
            co2eq_total REAL NOT NULL,
            fuel_rate_lh REAL,
            kwh REAL,
            scope TEXT DEFAULT 'scope1',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
        )
        """
    )

    # Insert demo machines if not exist
    machines_data = [
        ("TRUCK-21", "haul_truck", "Copper Mine - North Pit", "operational"),
        ("MILL-3", "grinding_mill", "Coal Plant - Processing", "operational"),
        ("BOILER-7", "industrial_boiler", "Power Generation - Unit 2", "operational"),
    ]

    for machine in machines_data:
        cur.execute(
            """
            INSERT OR IGNORE INTO machines (machine_id, machine_type, site, status)
            VALUES (?, ?, ?, ?)
        """,
            machine,
        )

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")


mi_lista = [
    (1, 2),
    (3, 4)
]


if __name__ == "__main__":
    init_db()
