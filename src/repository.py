import json
import sqlite3
from pathlib import Path


class ActivityRepository:
    def __init__(self, database_path: Path, seed_path: Path):
        self.database_path = database_path
        self.seed_path = seed_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self):
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    max_participants INTEGER NOT NULL CHECK (max_participants > 0)
                );

                CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
                    email TEXT NOT NULL,
                    UNIQUE (activity_id, email)
                );
                """
            )

            activity_count = connection.execute(
                "SELECT COUNT(*) FROM activities"
            ).fetchone()[0]
            if activity_count == 0:
                self._load_seed_data(connection)

    def _load_seed_data(self, connection):
        seed_activities = json.loads(self.seed_path.read_text(encoding="utf-8"))
        for activity in seed_activities:
            cursor = connection.execute(
                """
                INSERT INTO activities (name, description, schedule, max_participants)
                VALUES (?, ?, ?, ?)
                """,
                (
                    activity["name"],
                    activity["description"],
                    activity["schedule"],
                    activity["max_participants"],
                ),
            )
            connection.executemany(
                "INSERT INTO registrations (activity_id, email) VALUES (?, ?)",
                ((cursor.lastrowid, email) for email in activity["participants"]),
            )

    def list_activities(self):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    activities.id,
                    activities.name,
                    activities.description,
                    activities.schedule,
                    activities.max_participants,
                    registrations.email
                FROM activities
                LEFT JOIN registrations ON registrations.activity_id = activities.id
                ORDER BY activities.id, registrations.id
                """
            ).fetchall()

        activities = {}
        for row in rows:
            if row["name"] not in activities:
                activities[row["name"]] = {
                    "id": row["id"],
                    "description": row["description"],
                    "schedule": row["schedule"],
                    "max_participants": row["max_participants"],
                    "participants": [],
                }
            if row["email"] is not None:
                activities[row["name"]]["participants"].append(row["email"])
        return activities

    def activity_exists(self, activity_name: str):
        with self._connect() as connection:
            return connection.execute(
                "SELECT 1 FROM activities WHERE name = ?", (activity_name,)
            ).fetchone() is not None

    def signup(self, activity_name: str, email: str):
        with self._connect() as connection:
            activity = connection.execute(
                "SELECT id FROM activities WHERE name = ?", (activity_name,)
            ).fetchone()
            if activity is None:
                raise KeyError(activity_name)
            connection.execute(
                "INSERT INTO registrations (activity_id, email) VALUES (?, ?)",
                (activity["id"], email),
            )

    def unregister(self, activity_name: str, email: str):
        with self._connect() as connection:
            activity = connection.execute(
                "SELECT id FROM activities WHERE name = ?", (activity_name,)
            ).fetchone()
            if activity is None:
                raise KeyError(activity_name)
            cursor = connection.execute(
                "DELETE FROM registrations WHERE activity_id = ? AND email = ?",
                (activity["id"], email),
            )
            return cursor.rowcount > 0