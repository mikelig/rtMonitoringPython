#!/bin/sh
DB_FILE="sensor_events.db"

# Check if the database file already exists
if [ ! -f "$DB_FILE" ]; then
    # Create the database and set up the tables
    sqlite3 "$DB_FILE" <<EOF
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA mmap_size = 268435456;
PRAGMA cache_size = -2000;

CREATE TABLE IF NOT EXISTS sensorEvents (
    idEvent INTEGER PRIMARY KEY AUTOINCREMENT,
    receptionTs INTEGER NOT NULL,
    insertionTs INTEGER DEFAULT(strftime('%s', 'now') * 1000),
    receptionDt TEXT NOT NULL,
    insertionDt TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),
    idSensor TEXT,
    sensorType TEXT,
    sensorValue REAL
);

EOF
    echo "Database and tables created successfully."
else
    echo "Database already exists. No changes made."
fi
